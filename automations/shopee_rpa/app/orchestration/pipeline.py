"""Deterministic pipeline orchestrator driving jobs through the lifecycle states."""
import json
import os
import re
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.core.telemetry import bind_job, job_operation, record_state, timed_call, count
from app.core.resume import ArtifactCache, read_json, atomic_json
from app.orchestration.resume_media import media_checkpoint

from app.models.enums import JobState, ContentFormat
from app.models.product import Product
from app.models.facts import ProductFacts
from app.models.creative import CreativeBrief, Script, Storyboard
from app.models.job import Job
from app.models.flow import FlowOperationRequest
from app.media.ffmpeg import FFmpegAssembler
from app.media.inventory import inspect_take_inventory
from app.platforms.copy_package import CopyPackageBuilder
from app.platforms.instagram_reels import InstagramReelsExporter
from app.platforms.shopee_video import ShopeeVideoExporter
from app.providers.shopee.base import ShopeeProductProvider
from app.providers.shopee.factory import get_shopee_provider
from app.providers.visual.base import VisualGenerationProvider
from app.providers.visual.manual_flow import ManualFlowProvider
from app.validation.facts.extractor import FactExtractor
from app.validation.facts.validator import FactSafetyValidator
from app.validation.media import TechnicalMediaValidator, TechnicalQAResult, TechnicalQAStatus
from app.validation.visual import VisualQAResult, VisualQAStatus
from app.creative.briefs.generator import BriefGenerator
from app.creative.scripts.generator import ScriptGenerator
from app.creative.storyboards.generator import StoryboardGenerator


class PipelineOrchestrator:
    """Coordinates deterministic execution of a content generation job."""

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        product_provider: Optional[ShopeeProductProvider] = None,
        visual_provider: Optional[VisualGenerationProvider] = None,
    ):
        if base_dir is None:
            self.base_dir = Path(__file__).resolve().parents[2]
        else:
            self.base_dir = Path(base_dir)

        self.output_base = self.base_dir / "output"
        self.jobs_base = self.base_dir / "data" / "jobs"
        self.output_base.mkdir(parents=True, exist_ok=True)
        self.jobs_base.mkdir(parents=True, exist_ok=True)

        self.product_provider = product_provider or get_shopee_provider()
        self.visual_provider = visual_provider or ManualFlowProvider()

        self.fact_extractor = FactExtractor()
        self.fact_validator = FactSafetyValidator()
        self.brief_generator = BriefGenerator()
        self.script_generator = ScriptGenerator()
        self.storyboard_generator = StoryboardGenerator()

    @job_operation("CREATIVE_MS")
    def run_up_to_prompts(
        self,
        product_id: str,
        job_id: Optional[str] = None,
        format_type: ContentFormat = ContentFormat.ACHADINHO,
    ) -> Job:
        """Executes the pipeline up to the PROMPTS_READY state."""
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not job_id:
            safe_product_id = re.sub(r"[^A-Za-z0-9_-]+", "_", product_id).strip("_")
            if not safe_product_id:
                raise ValueError("product_id cannot produce an empty job identifier")
            job_id = f"job_{safe_product_id[:80]}_{timestamp_str}"

        job_dir = self._safe_job_dir(job_id)
        job_dir.mkdir(parents=True, exist_ok=True)
        bind_job(job_id)
        prior_data = read_json(self.jobs_base / f"{job_id}.json")
        prior = Job.from_dict(prior_data) if prior_data else None
        if prior and (prior.product_id != product_id or prior.metadata.get("format") != format_type.value):
            raise ValueError("job_id already belongs to another product or format; use a new job")
        cache = ArtifactCache(job_dir)

        now_iso = datetime.now().isoformat()
        job = Job(
            job_id=job_id,
            state=JobState.CREATED,
            created_at=now_iso,
            updated_at=now_iso,
            product_id=product_id,
            output_dir=str(job_dir),
            metadata={"format": format_type.value},
        )

        try:
            # 1. Load Product -> PRODUCT_LOADED
            def fetch():
                count("shopee_calls")
                return timed_call("SHOPEE_FETCH_MS", self.product_provider.get_product, product_id)
            product = self._cached_model(cache, "Product", [], "product.json", Product,
                lambda p: bool(p.product_id and p.shop_id and p.title.strip()), fetch, adopt=bool(prior))
            self._write_json(job_dir / "product.json", product.to_dict())
            job.transition_to(JobState.PRODUCT_LOADED)

            # 2. Extract Facts -> FACTS_READY
            facts = self._cached_model(cache, "ProductFacts", ["product.json"], "facts.json", ProductFacts,
                lambda f: f.product_id == product.product_id and bool(f.confirmed_facts),
                lambda: timed_call("FACT_EXTRACTION_MS", self.fact_extractor.extract, product), adopt=bool(prior))
            self._write_json(job_dir / "facts.json", facts.to_dict())
            job.transition_to(JobState.FACTS_READY)

            # 3. Creative Brief -> BRIEF_READY
            brief = self._cached_model(cache, "Brief", ["product.json", "facts.json"], "creative_brief.json", CreativeBrief,
                lambda b: b.job_id == job_id and b.product_id == product.product_id,
                lambda: timed_call("BRIEF_MS", self.brief_generator.generate,
                job_id=job_id,
                product=product,
                facts=facts,
                format_type=format_type,
            ), adopt=bool(prior))
            self._write_json(job_dir / "creative_brief.json", brief.to_dict())
            job.transition_to(JobState.BRIEF_READY)

            # 4. Generate Script & Validate -> SCRIPT_READY
            script = self._cached_model(cache, "Script", ["creative_brief.json", "facts.json"], "script.json", Script,
                lambda s: bool(s.scenes) and self.fact_validator.validate(s, facts)[0],
                lambda: timed_call("SCRIPT_AND_HOOK_MS", self.script_generator.generate,
                brief=brief,
                product=product,
                facts=facts,
            ), adopt=bool(prior))
            is_valid, violations = timed_call("FACT_VALIDATION_MS", self.fact_validator.validate, script, facts)
            if not is_valid:
                raise ValueError(f"Script validation failed: {violations}")

            self._write_json(job_dir / "script.json", script.to_dict())
            job.transition_to(JobState.SCRIPT_READY)

            # 5. Generate Storyboard -> STORYBOARD_READY
            storyboard = self._cached_model(cache, "Storyboard", ["script.json", "product.json"], "storyboard.json", Storyboard,
                lambda s: s.job_id == job_id and len(s.scenes) == len(script.scenes) and
                    all(scene.positive_prompt.strip() for scene in s.scenes),
                lambda: timed_call("STORYBOARD_AND_PROMPTS_MS", self.storyboard_generator.generate,
                job_id=job_id,
                script=script,
                product=product,
            ), adopt=bool(prior))
            self._write_json(job_dir / "storyboard.json", storyboard.to_dict())
            job.transition_to(JobState.STORYBOARD_READY)

            # 6. Generate Prompts -> PROMPTS_READY
            expected_prompts = [job_dir / "prompts" / f"scene_{s.scene_number:02d}.txt" for s in storyboard.scenes]
            prompt_files = cache.use("Prompts", [job_dir / "storyboard.json"], expected_prompts,
                lambda: timed_call("PROMPT_FILES_MS", self.visual_provider.prepare_job_prompts,
                job_output_dir=job_dir,
                storyboard=storyboard,
            ), lambda: expected_prompts,
                lambda paths: all(p.is_file() and p.read_text(encoding="utf-8").strip() for p in paths), adopt=bool(prior))
            job.metadata["prompt_files"] = [p.name for p in prompt_files]
            job.transition_to(JobState.PROMPTS_READY)
            package_files = [job_dir / name for name in ("creative_brief.json", "script.json", "storyboard.json")]
            package_path = job_dir / "creative_package.json"
            def package_build():
                package = {"schema_version": 1, "job_id": job_id, "brief": brief.to_dict(),
                           "script": script.to_dict(), "storyboard": storyboard.to_dict(),
                           "prompts": [p.read_text(encoding="utf-8") for p in expected_prompts]}
                self._write_json(package_path, package)
                return package
            cache.use("CreativePackage", package_files + expected_prompts, [package_path], package_build,
                lambda: self._read_json(package_path), lambda p: p.get("job_id") == job_id and bool(p.get("script")))
            if prior and not cache.changed:
                return prior
            if prior and prior.state not in {JobState.CREATED, JobState.PRODUCT_LOADED, JobState.FACTS_READY,
                    JobState.BRIEF_READY, JobState.SCRIPT_READY, JobState.STORYBOARD_READY,
                    JobState.PROMPTS_READY, JobState.FAILED}:
                prior.state = JobState.REVIEW_REQUIRED
                prior.metadata["resume_reason"] = "Creative inputs rebuilt; review existing media before continuing"
                self._save_job(prior)
                self._update_manifest(job_dir, {"status": prior.state.value})
                return prior

            # 7. Write Manifest
            manifest = {
                "job_id": job.job_id,
                "source_product": {
                    "product_id": product.product_id,
                    "shop_id": product.shop_id,
                    "title": product.title,
                    "kind": "MOCK" if "Fixture" in type(self.product_provider).__name__ else "LIVE",
                },
                "provider": {
                    "product": type(self.product_provider).__name__,
                    "visual": type(self.visual_provider).__name__,
                },
                "fact_safety": "PASS",
                "format": format_type.value,
                "scene_count": len(storyboard.scenes),
                "duration_seconds": storyboard.total_duration_seconds,
                "created_at": job.created_at,
                "updated_at": job.updated_at,
                "takes": [],
                "technical_qa": {"status": "NOT_EXECUTED"},
                "semantic_visual_qa": {"status": "NOT_EXECUTED"},
                "master": None,
                "platform_exports": {},
                "status": job.state.value,
                "state": job.state.value,
                "artifacts": [
                    "product.json",
                    "facts.json",
                    "creative_brief.json",
                    "script.json",
                    "storyboard.json",
                    "prompts/",
                ],
            }
            self._write_json(job_dir / "manifest.json", manifest)

            # Save job record
            self._write_json(self.jobs_base / f"{job.job_id}.json", job.to_dict())
            record_state(job.state.value)
            return job

        except Exception as exc:
            job.transition_to(JobState.FAILED, error=str(exc))
            self._write_json(self.jobs_base / f"{job.job_id}.json", job.to_dict())
            record_state(job.state.value)
            raise

    def _cached_model(self, cache, name, dependencies, filename, model, validate, build, *, adopt=False):
        path = cache.directory / filename
        def create():
            value = build()
            if not validate(value):
                raise ValueError(f"Invalid artifact: {name}")
            self._write_json(path, value.to_dict())
            return value
        return cache.use(name, [cache.directory / d for d in dependencies], [path], create,
            lambda: model.from_dict(self._read_json(path)), validate, adopt=adopt)

    def _write_json(self, path: Path, data: Dict[str, Any]) -> None:
        if read_json(path) == data:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".pending-", suffix=".json", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    @job_operation("PREPARE_GENERATION_MS")
    def prepare_generation(self, job_id: str) -> FlowOperationRequest:
        """Writes a reviewable Flow request and enters WAITING; it never generates media."""
        job, job_dir = self._load_job(job_id)
        if job.state != JobState.PROMPTS_READY:
            raise ValueError("Job must be PROMPTS_READY")
        product = Product.from_dict(self._read_json(job_dir / "product.json"))
        storyboard = Storyboard.from_dict(self._read_json(job_dir / "storyboard.json"))
        if not product.images:
            raise ValueError("Official product image is required")
        nina_reference = self.base_dir / "data" / "personas" / "nina_v1" / "references" / "persona_master.png"
        if not nina_reference.is_file():
            raise FileNotFoundError("Nina master reference is missing")
        operation = self.visual_provider.build_operation(
            job.job_id, job_dir, storyboard, product.images[0], str(nina_reference)
        )
        self._write_json(job_dir / "flow_operation.json", operation.to_dict())
        job.transition_to(JobState.WAITING_FOR_GENERATION)
        job.metadata["flow_provider"] = operation.provider
        job.metadata["flow_generation_authorized"] = False
        self._save_job(job)
        return operation

    @job_operation("RECORD_GENERATION_STATE_MS")
    def record_generation_started(
        self,
        job_id: str,
        *,
        operator_confirmation: bool = False,
        media_origin: str = "LIVE",
    ) -> Job:
        """Records an externally observed start; it does not click or call a provider."""
        if not operator_confirmation:
            raise PermissionError("Explicit operator confirmation is required")
        if media_origin not in {"MOCK", "SYNTHETIC", "LIVE"}:
            raise ValueError("media_origin must be MOCK, SYNTHETIC or LIVE")
        job, _ = self._load_job(job_id)
        if job.state != JobState.WAITING_FOR_GENERATION:
            raise ValueError("Job must be WAITING_FOR_GENERATION")
        job.transition_to(JobState.GENERATING_MEDIA)
        job.metadata["flow_generation_authorized"] = True
        job.metadata["media_origin"] = media_origin
        self._save_job(job)
        return job

    @job_operation("MEDIA_STATUS_MS")
    def refresh_media_status(self, job_id: str) -> Dict[str, Any]:
        """Transitions to MEDIA_READY only when every expected scene has a non-empty take."""
        job, job_dir = self._load_job(job_id)
        if job.state != JobState.GENERATING_MEDIA:
            raise ValueError("Job must be GENERATING_MEDIA")
        storyboard = Storyboard.from_dict(self._read_json(job_dir / "storyboard.json"))
        status = self.visual_provider.check_media_status(job_dir, len(storyboard.scenes))
        if status.get("all_ready"):
            job.transition_to(JobState.MEDIA_READY)
            self._save_job(job)
            self._update_manifest(job_dir, {
                "takes": status["found_takes"],
                "media_origin": job.metadata.get("media_origin", "LIVE"),
                "status": job.state.value,
            })
        return status

    @job_operation("TECHNICAL_QA_MS")
    @media_checkpoint("TechnicalQA")
    def run_technical_qa(
        self, job_id: str, validator: TechnicalMediaValidator
    ) -> List[TechnicalQAResult]:
        """Validates takes with ffprobe; no identity or scene semantics are asserted."""
        job, job_dir = self._load_job(job_id)
        if job.state != JobState.MEDIA_READY:
            raise ValueError("Job must be MEDIA_READY")
        storyboard = Storyboard.from_dict(self._read_json(job_dir / "storyboard.json"))
        inventory = inspect_take_inventory(job_dir / "generated", len(storyboard.scenes))
        if not inventory.ready:
            raise ValueError("Take inventory is not ready")
        results = [validator.validate(path) for path in inventory.ordered_takes]
        overall = "PASS" if all(result.status == TechnicalQAStatus.PASS for result in results) else "FAIL"
        payload = {"status": overall, "scope": "TAKES", "results": [item.to_dict() for item in results]}
        self._write_json(job_dir / "technical_qa.json", payload)
        self._update_manifest(job_dir, {"technical_qa": payload})
        if overall == "PASS":
            job.transition_to(JobState.VISUAL_QA)
        else:
            job.transition_to(JobState.REVIEW_REQUIRED)
        self._save_job(job)
        self._update_manifest(job_dir, {"status": job.state.value})
        return results

    @job_operation("VISUAL_QA_RECORD_MS")
    @media_checkpoint("VisualQA")
    def complete_visual_qa(
        self,
        job_id: str,
        result: VisualQAResult,
        *,
        synthetic_fixture_waiver: bool = False,
    ) -> Job:
        """Applies semantic QA without converting NOT_EXECUTED into a false PASS."""
        job, job_dir = self._load_job(job_id)
        if job.state != JobState.VISUAL_QA:
            raise ValueError("Job must be VISUAL_QA")
        payload = result.to_dict()
        self._write_json(job_dir / "semantic_visual_qa.json", payload)
        allowed_synthetic_waiver = (
            result.status == VisualQAStatus.NOT_EXECUTED
            and synthetic_fixture_waiver
            and job.metadata.get("media_origin") == "SYNTHETIC"
        )
        if result.status == VisualQAStatus.PASS or allowed_synthetic_waiver:
            if allowed_synthetic_waiver:
                job.metadata["semantic_qa_waiver"] = "SYNTHETIC_OFFLINE_FIXTURE"
            job.transition_to(JobState.EDITING)
        else:
            job.transition_to(JobState.REVIEW_REQUIRED)
        self._save_job(job)
        self._update_manifest(job_dir, {
            "semantic_visual_qa": payload,
            "status": job.state.value,
        })
        return job

    @job_operation("ASSEMBLE_MASTER_MS")
    @media_checkpoint("Master")
    def assemble_master(self, job_id: str, assembler: FFmpegAssembler) -> Path:
        """Normalizes and concatenates ordered takes into master/master.mp4."""
        job, job_dir = self._load_job(job_id)
        if job.state != JobState.EDITING:
            raise ValueError("Job must be EDITING")
        storyboard = Storyboard.from_dict(self._read_json(job_dir / "storyboard.json"))
        inventory = inspect_take_inventory(job_dir / "generated", len(storyboard.scenes))
        if not inventory.ready:
            raise ValueError("Take inventory is not ready")
        master = timed_call("FFMPEG_NORMALIZE_MS", assembler.assemble, inventory.ordered_takes, job_dir / "master" / "master.mp4")
        job.transition_to(JobState.VALIDATING)
        self._save_job(job)
        self._update_manifest(job_dir, {
            "master": str(master.relative_to(job_dir)),
            "status": job.state.value,
        })
        return master

    @job_operation("VALIDATE_AND_PACKAGE_MS")
    @media_checkpoint("PlatformExports")
    def validate_and_package(
        self,
        job_id: str,
        validator: TechnicalMediaValidator,
        *,
        shopee_exporter: Optional[ShopeeVideoExporter] = None,
        instagram_exporter: Optional[InstagramReelsExporter] = None,
        copy_builder: Optional[CopyPackageBuilder] = None,
    ) -> TechnicalQAResult:
        """Validates the real master metadata, exports without transcode, and finalizes."""
        job, job_dir = self._load_job(job_id)
        if job.state != JobState.VALIDATING:
            raise ValueError("Job must be VALIDATING")
        master = job_dir / "master" / "master.mp4"
        result = timed_call("MASTER_TECHNICAL_QA_MS", validator.validate,
            master, expected_width=1080, expected_height=1920, expected_fps=30,
            expected_video_codec="h264", allowed_audio_codecs={"aac"},
        )
        self._write_json(job_dir / "master_technical_qa.json", result.to_dict())
        prior_qa = self._read_json(job_dir / "manifest.json").get("technical_qa", {})
        combined_qa = {
            "status": result.status.value,
            "takes": prior_qa.get("results", prior_qa.get("takes", [])),
            "master": result.to_dict(),
        }
        if result.status != TechnicalQAStatus.PASS:
            job.transition_to(JobState.REVIEW_REQUIRED)
            self._save_job(job)
            self._update_manifest(job_dir, {
                "technical_qa": combined_qa,
                "status": job.state.value,
            })
            return result

        shopee = timed_call("EXPORT_SHOPEE_MS", (shopee_exporter or ShopeeVideoExporter()).export, master, job_dir)
        instagram = timed_call("EXPORT_INSTAGRAM_MS", (instagram_exporter or InstagramReelsExporter()).export, master, job_dir)
        product = Product.from_dict(self._read_json(job_dir / "product.json"))
        facts = ProductFacts.from_dict(self._read_json(job_dir / "facts.json"))
        brief = CreativeBrief.from_dict(self._read_json(job_dir / "creative_brief.json"))
        copies = timed_call("COPY_PACKAGE_MS", (copy_builder or CopyPackageBuilder()).build, job_dir, product, facts, brief)
        job.transition_to(JobState.PACKAGE_READY)
        self._save_job(job)
        self._update_manifest(job_dir, {
            "technical_qa": combined_qa,
            "platform_exports": {
                "shopee": {"path": str(Path(shopee.path).relative_to(job_dir)), "method": shopee.method},
                "instagram": {"path": str(Path(instagram.path).relative_to(job_dir)), "method": instagram.method},
            },
            "copy_package": {
                "shopee": str(Path(copies["shopee"]).relative_to(job_dir)),
                "instagram": str(Path(copies["instagram"]).relative_to(job_dir)),
                "hashtags": str(Path(copies["hashtags"]).relative_to(job_dir)),
                "hashtag_count": copies["hashtag_count"],
            },
            "status": job.state.value,
        })
        return result

    def _safe_job_dir(self, job_id: str) -> Path:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,119}", job_id):
            raise ValueError("Invalid job_id")
        job_dir = (self.output_base / job_id).resolve()
        if job_dir.parent != self.output_base.resolve():
            raise ValueError("Job path escapes output directory")
        return job_dir

    @staticmethod
    def _read_json(path: Path) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError("Expected JSON object")
        return data

    def _load_job(self, job_id: str):
        job_dir = self._safe_job_dir(job_id)
        bind_job(job_id)
        record = self.jobs_base / f"{job_id}.json"
        if not record.is_file() or not job_dir.is_dir():
            raise FileNotFoundError("Job record or output is missing")
        return Job.from_dict(self._read_json(record)), job_dir

    def _save_job(self, job: Job):
        self._write_json(self.jobs_base / f"{job.job_id}.json", job.to_dict())
        record_state(job.state.value)

    def _update_manifest(self, job_dir: Path, updates: Dict[str, Any]) -> None:
        manifest_path = job_dir / "manifest.json"
        manifest = self._read_json(manifest_path)
        manifest.update(updates)
        if "status" in updates:
            manifest["state"] = updates["status"]
        self._write_json(manifest_path, manifest)
