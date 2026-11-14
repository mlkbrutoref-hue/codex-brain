"""Carousel orchestration with full-slide AI generation as the default."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from PIL import Image, ImageOps, __version__ as PILLOW_VERSION

from app.carousel.layout import CarouselLayoutDirector
from app.carousel.models import CarouselPlan, CarouselSlide, SlideType
from app.carousel.qa import CarouselQAEvaluator
from app.creative.proportion_policy import negative_constraints, proportion_rules
from app.single_story.layout import TextLayoutError
from app.single_story.renderer import StoryTypographyRenderer


class CarouselPipeline:
    """Coordinates multiple slides without implementing an image provider."""

    PIPELINE_NAME = "NINA_CAROUSEL_PIPELINE"
    PIPELINE_VERSION = "2.0.0"
    CANVAS = (1080, 1440)
    FULL_AI_CREATIVE = "FULL_AI_CREATIVE"
    DETERMINISTIC_COMPOSITOR = "DETERMINISTIC_COMPOSITOR"
    DEFAULT_GENERATION_MODE = FULL_AI_CREATIVE
    DEFAULT_STYLE_REFERENCE = "data/brands/nina_v1/references/story_style_master.png"

    def __init__(
        self,
        director: Optional[CarouselLayoutDirector] = None,
        renderer: Optional[StoryTypographyRenderer] = None,
        qa: Optional[CarouselQAEvaluator] = None,
        generation_mode: str = DEFAULT_GENERATION_MODE,
    ) -> None:
        self.director = director or CarouselLayoutDirector()
        self.renderer = renderer or StoryTypographyRenderer()
        self.qa = qa or CarouselQAEvaluator()
        if generation_mode not in {self.FULL_AI_CREATIVE, self.DETERMINISTIC_COMPOSITOR}:
            raise ValueError(f"unsupported carousel generation mode: {generation_mode}")
        self.generation_mode = generation_mode

    def prepare(self, plan_path: Path, output_dir: Path) -> Dict[str, Any]:
        """Persist image-generation requests without invoking a provider."""
        plan_path = Path(plan_path)
        output_dir = Path(output_dir)
        plan = self._load_plan(plan_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(plan_path, output_dir / "carousel_plan.json")
        records = []
        for slide in plan.slides:
            slide_dir = output_dir / self._slide_dir_name(slide)
            slide_dir.mkdir(parents=True, exist_ok=True)
            request = self._generation_request(plan, slide, plan_path)
            self._write_json(slide_dir / "image_generation_request.json", request)
            self._write_json(slide_dir / "slide_plan.json", self._slide_package(plan, slide, plan_path))
            awaiting = "AWAITING_FINAL_AI_SLIDE" if self.generation_mode == self.FULL_AI_CREATIVE else "AWAITING_BASE_IMAGE"
            records.append(self._manifest_record(plan, slide, request, status=awaiting))
        aggregate = "AWAITING_FINAL_AI_SLIDES" if self.generation_mode == self.FULL_AI_CREATIVE else "AWAITING_BASE_IMAGES"
        manifest = self._carousel_manifest(plan, records, aggregate)
        self._write_json(output_dir / "carousel_manifest.json", manifest)
        return manifest

    def run(
        self,
        plan_path: Path,
        base_images: Mapping[int, Path],
        output_dir: Path,
        *,
        semantic_review_paths: Optional[Mapping[int, Path]] = None,
    ) -> Dict[str, Any]:
        """Ingest final AI slides by default; deterministic compositing is explicit legacy mode."""
        if self.generation_mode == self.FULL_AI_CREATIVE:
            return self._run_full_ai(plan_path, base_images, output_dir, semantic_review_paths=semantic_review_paths)
        plan_path = Path(plan_path)
        output_dir = Path(output_dir)
        plan = self._load_plan(plan_path)
        missing = [slide.slide_number for slide in plan.slides if slide.slide_number not in base_images]
        if missing:
            raise ValueError(f"missing base images for slides: {missing}")
        output_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(plan_path, output_dir / "carousel_plan.json")
        records = []
        for slide in plan.slides:
            request = self._generation_request(plan, slide, plan_path)
            package = self._slide_package(plan, slide, plan_path)
            slide_dir = output_dir / self._slide_dir_name(slide)
            slide_dir.mkdir(parents=True, exist_ok=True)
            paths = {
                "request": slide_dir / "image_generation_request.json",
                "plan": slide_dir / "slide_plan.json",
                "base": slide_dir / "base_image.png",
                "overlay": slide_dir / "text_overlay.png",
                "final": slide_dir / "rendered_image.png",
                "layout": slide_dir / "layout.json",
                "qa": slide_dir / "qa.json",
                "manifest": slide_dir / "slide_manifest.json",
            }
            self._write_json(paths["request"], request)
            self._write_json(paths["plan"], package)
            self.renderer.normalize_base(Path(base_images[slide.slide_number]), paths["base"], size=self.CANVAS)
            try:
                layout = self.renderer.render(
                    paths["base"], package, self.director.plan(slide.slide_type), paths["overlay"], paths["final"]
                )
            except TextLayoutError:
                failed = self._manifest_record(plan, slide, request, base_image=str(paths["base"]), status="FAIL")
                failed["final_status"] = "REVIEW_REQUIRED" if slide.correction_attempt else "CORRECTION_REQUIRED"
                self._write_json(paths["manifest"], failed)
                raise
            self._write_json(paths["layout"], layout)
            review = self._load_optional_review(semantic_review_paths, slide.slide_number)
            report = self.qa.evaluate(package, layout, paths["base"], paths["overlay"], paths["final"], review)
            self._write_json(paths["qa"], report)
            final_status = self._final_status(report["qa_result"], slide.correction_attempt)
            record = self._manifest_record(
                plan,
                slide,
                request,
                base_image=str(paths["base"]),
                rendered_image=str(paths["final"]),
                qa=report,
                status=final_status,
            )
            self._write_json(paths["manifest"], record)
            records.append(record)

        statuses = {record["final_status"] for record in records}
        if statuses == {"READY"}:
            aggregate = "READY"
        elif "CORRECTION_REQUIRED" in statuses:
            aggregate = "CORRECTION_REQUIRED"
        else:
            aggregate = "REVIEW_REQUIRED"
        manifest = self._carousel_manifest(plan, records, aggregate)
        self._write_json(output_dir / "carousel_manifest.json", manifest)
        return manifest

    def _run_full_ai(
        self,
        plan_path: Path,
        final_slides: Mapping[int, Path],
        output_dir: Path,
        *,
        semantic_review_paths: Optional[Mapping[int, Path]] = None,
    ) -> Dict[str, Any]:
        plan_path = Path(plan_path)
        output_dir = Path(output_dir)
        plan = self._load_plan(plan_path)
        missing = [slide.slide_number for slide in plan.slides if slide.slide_number not in final_slides]
        if missing:
            raise ValueError(f"missing final AI slides: {missing}")
        output_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(plan_path, output_dir / "carousel_plan.json")
        records = []
        for slide in plan.slides:
            request = self._generation_request(plan, slide, plan_path)
            package = self._slide_package(plan, slide, plan_path)
            slide_dir = output_dir / self._slide_dir_name(slide)
            slide_dir.mkdir(parents=True, exist_ok=True)
            final_path = slide_dir / "rendered_image.png"
            self._normalize_final_ai_slide(Path(final_slides[slide.slide_number]), final_path)
            self._write_json(slide_dir / "image_generation_request.json", request)
            self._write_json(slide_dir / "slide_plan.json", package)
            review = self._load_optional_review(semantic_review_paths, slide.slide_number)
            report = self.qa.evaluate_full_ai(package, final_path, review)
            self._write_json(slide_dir / "qa.json", report)
            final_status = self._full_ai_final_status(report, slide.correction_attempt)
            record = self._manifest_record(
                plan,
                slide,
                request,
                rendered_image=str(final_path),
                qa=report,
                status=final_status,
            )
            record["localized_ai_correction_used"] = bool(slide.correction_attempt)
            self._write_json(slide_dir / "slide_manifest.json", record)
            records.append(record)

        statuses = {record["final_status"] for record in records}
        if statuses == {"READY"}:
            aggregate = "READY"
        elif "LOCALIZED_AI_CORRECTION_REQUIRED" in statuses:
            aggregate = "LOCALIZED_AI_CORRECTION_REQUIRED"
        elif "TEXT_RENDER_REVIEW_REQUIRED" in statuses:
            aggregate = "TEXT_RENDER_REVIEW_REQUIRED"
        else:
            aggregate = "REVIEW_REQUIRED"
        manifest = self._carousel_manifest(plan, records, aggregate)
        self._write_json(output_dir / "carousel_manifest.json", manifest)
        return manifest

    def _generation_request(self, plan: CarouselPlan, slide: CarouselSlide, plan_path: Path) -> Dict[str, Any]:
        product = plan.product(slide.product_id)
        reference = plan.reference(slide.reference_id)
        product_reference = str(product.get("official_product_reference") or product.get("official_asset") or "")
        scene_reference = str(reference.get("path") or reference.get("scene_reference_path") or "")
        persona = plan.persona_reference_paths if slide.use_nina else []
        realism = [
            "photorealistic domestic photography with plausible smartphone or editorial camera physics",
            "natural skin and material texture; no artificial graphic background",
            *slide.realism_constraints,
        ]
        style_references = plan.style_reference_paths or ([self.DEFAULT_STYLE_REFERENCE] if Path(self.DEFAULT_STYLE_REFERENCE).is_file() else [])
        if self.generation_mode == self.FULL_AI_CREATIVE:
            copy_lines = [f'{key.upper()}: "{value}"' for key, value in slide.copy.items()]
            if slide.slide_type is SlideType.CTA and "keyword" not in slide.copy:
                copy_lines.append(f'KEYWORD: "{plan.cta_keyword}"')
            prompt_parts = [
                "Create the complete final 3:4 editorial carousel slide as one visually unified image.",
                "Integrate the photography, exact Portuguese copy, typography, pills, boxes, handwritten annotations and small decorative elements during generation.",
                "The graphics must feel designed together with the photograph, never like a rigid template or later overlay.",
                slide.scene_prompt.strip(),
                "Composition: " + "; ".join(slide.composition_requirements),
                "Realism: " + "; ".join(realism),
                "Render every quoted string exactly, preserving spelling and accents:\n" + "\n".join(copy_lines),
                "Use elegant high-contrast editorial serif headlines, soft pink rounded pills, restrained white text boxes, delicate handwritten accents, hearts or sparkles only where they support hierarchy.",
                "Keep all copy readable inside safe margins and preserve clear visual hierarchy.",
            ]
        else:
            prompt_parts = [
                "Create only the photographic base for a 3:4 carousel slide; render no typography.",
                slide.scene_prompt.strip(),
                "Composition: " + "; ".join(slide.composition_requirements),
                "Realism: " + "; ".join(realism),
                "Reserve the declared negative space so deterministic typography does not cover the face or product.",
            ]
        if scene_reference:
            prompt_parts.append(
                "Use the Pinterest scene reference only for pose, framing, environment, light and negative-space logic; do not copy its person, text or products."
            )
        if style_references and self.generation_mode == self.FULL_AI_CREATIVE:
            prompt_parts.append(
                "Use the supplied style reference only for editorial hierarchy, typography character, pink pills, white boxes, delicate annotations, spacing and decoration; do not copy its product or wording."
            )
        if product_reference:
            prompt_parts.append(
                "Treat the official product reference as authoritative for product geometry, color, material and included parts; do not redesign it."
            )
        proportion = []
        if persona:
            proportion = [proportion_rules(), "AVOID: " + negative_constraints()]
            prompt_parts.extend(proportion)
        return {
            "request_type": "IMAGE_GENERATION_REQUEST",
            "generation_mode": self.generation_mode,
            "provider_execution": "CODEX_AGENT_OR_INJECTED_GENERATOR",
            "provider_created_by_pipeline": False,
            "campaign_id": plan.campaign_id,
            "slide_number": slide.slide_number,
            "slide_type": slide.slide_type.value,
            "canvas": {"width": self.CANVAS[0], "height": self.CANVAS[1], "aspect_ratio": "3:4"},
            "prompt": "\n".join(part for part in prompt_parts if not part.endswith(": ")),
            "references": {
                "pinterest_scene_reference": self._resolve_reference(scene_reference, plan_path),
                "official_product_reference": self._resolve_reference(product_reference, plan_path),
                "persona_references": [self._resolve_reference(item, plan_path) for item in persona],
                "style_references": [self._resolve_reference(item, plan_path) for item in style_references],
            },
            "realism_constraints": realism,
            "proportion_constraints": proportion,
            "composition_requirements": slide.composition_requirements,
            "correction_attempt": slide.correction_attempt,
            "max_correction_attempts": 1,
            "correction_strategy": "LOCALIZED_AI_EDIT" if self.generation_mode == self.FULL_AI_CREATIVE else "DETERMINISTIC_RERENDER",
            "text_failure_fallback": "TEXT_RENDER_REVIEW_REQUIRED" if self.generation_mode == self.FULL_AI_CREATIVE else "REVIEW_REQUIRED",
        }

    def _slide_package(self, plan: CarouselPlan, slide: CarouselSlide, plan_path: Path) -> Dict[str, Any]:
        product = plan.product(slide.product_id)
        reference = plan.reference(slide.reference_id)
        package = {
            "campaign_id": plan.campaign_id,
            "slide_number": slide.slide_number,
            "slide_type": slide.slide_type.value,
            "product_id": slide.product_id,
            "reference_id": slide.reference_id,
            "persona_reference_paths": [self._resolve_reference(item, plan_path) for item in plan.persona_reference_paths] if slide.use_nina else [],
            "official_product_reference": self._resolve_reference(
                str(product.get("official_product_reference") or product.get("official_asset") or ""), plan_path
            ),
            "scene_reference_path": self._resolve_reference(
                str(reference.get("path") or reference.get("scene_reference_path") or ""), plan_path
            ),
            "style_reference_paths": [
                self._resolve_reference(item, plan_path)
                for item in (plan.style_reference_paths or ([self.DEFAULT_STYLE_REFERENCE] if Path(self.DEFAULT_STYLE_REFERENCE).is_file() else []))
            ],
            **slide.copy,
        }
        if slide.slide_type is SlideType.CTA:
            package["keyword"] = slide.copy.get("keyword") or plan.cta_keyword
        return package

    @staticmethod
    def _load_plan(path: Path) -> CarouselPlan:
        if not path.is_file():
            raise FileNotFoundError(f"carousel plan missing: {path}")
        return CarouselPlan.from_dict(json.loads(path.read_text(encoding="utf-8-sig")))

    @staticmethod
    def _load_optional_review(paths: Optional[Mapping[int, Path]], number: int) -> Optional[Dict[str, Any]]:
        if not paths or number not in paths:
            return None
        path = Path(paths[number])
        return json.loads(path.read_text(encoding="utf-8-sig"))

    @staticmethod
    def _resolve_reference(value: str, plan_path: Path) -> str:
        if not value:
            return ""
        candidate = Path(value)
        if candidate.is_absolute():
            return str(candidate)
        direct = Path.cwd() / candidate
        if direct.exists():
            return str(direct.resolve())
        return str((plan_path.parent / candidate).resolve())

    @staticmethod
    def _slide_dir_name(slide: CarouselSlide) -> str:
        return f"slide_{slide.slide_number:02d}_{slide.slide_type.value.lower()}"

    @staticmethod
    def _final_status(qa_result: str, correction_attempt: int) -> str:
        if qa_result == "PASS":
            return "READY"
        if qa_result == "FAIL" and correction_attempt == 0:
            return "CORRECTION_REQUIRED"
        return "REVIEW_REQUIRED"

    @staticmethod
    def _full_ai_final_status(report: Dict[str, Any], correction_attempt: int) -> str:
        if report["qa_result"] == "PASS":
            return "READY"
        text_names = set(CarouselQAEvaluator.FULL_AI_TEXT_CHECKS)
        unresolved = set(report.get("semantic_failures", [])) | set(report.get("review_required", []))
        if correction_attempt == 0:
            return "LOCALIZED_AI_CORRECTION_REQUIRED"
        if unresolved and unresolved.issubset(text_names):
            return "TEXT_RENDER_REVIEW_REQUIRED"
        return "REVIEW_REQUIRED"

    @classmethod
    def _normalize_final_ai_slide(cls, source: Path, destination: Path) -> None:
        """Technical canvas normalization only; no typography or visual design is added."""
        with Image.open(source) as image:
            normalized = ImageOps.fit(image.convert("RGB"), cls.CANVAS, method=Image.Resampling.LANCZOS)
            normalized.save(destination, format="PNG")

    def _manifest_record(
        self,
        plan: CarouselPlan,
        slide: CarouselSlide,
        request: Dict[str, Any],
        *,
        base_image: str = "",
        rendered_image: str = "",
        qa: Optional[Dict[str, Any]] = None,
        status: str,
    ) -> Dict[str, Any]:
        return {
            "campaign_id": plan.campaign_id,
            "slide_number": slide.slide_number,
            "slide_type": slide.slide_type.value,
            "product_id": slide.product_id or None,
            "reference_id": slide.reference_id,
            "prompt": request["prompt"],
            "base_image": base_image or None,
            "rendered_image": rendered_image or None,
            "qa": qa,
            "correction_used": bool(slide.correction_attempt),
            "final_status": status,
        }

    def _carousel_manifest(self, plan: CarouselPlan, slides, status: str) -> Dict[str, Any]:
        return {
            "pipeline_name": self.PIPELINE_NAME,
            "pipeline_version": self.PIPELINE_VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "campaign_id": plan.campaign_id,
            "format_spec": {"width": 1080, "height": 1440, "aspect_ratio": "3:4"},
            "image_provider_created": False,
            "generation_mode": self.generation_mode,
            "python_visual_compositor_default": False,
            "typography_engine": "AI_IN_IMAGE" if self.generation_mode == self.FULL_AI_CREATIVE else "Pillow",
            "typography_engine_version": None if self.generation_mode == self.FULL_AI_CREATIVE else PILLOW_VERSION,
            "renderer": None if self.generation_mode == self.FULL_AI_CREATIVE else f"{StoryTypographyRenderer.__module__}.{StoryTypographyRenderer.__name__}",
            "python_role": ["validation", "dimensions", "metadata", "manifest", "qa", "file_organization"],
            "correction_policy": {
                "strategy": "LOCALIZED_AI_EDIT" if self.generation_mode == self.FULL_AI_CREATIVE else "DETERMINISTIC_RERENDER",
                "max_attempts_per_slide": 1,
                "on_text_exhaustion": "TEXT_RENDER_REVIEW_REQUIRED" if self.generation_mode == self.FULL_AI_CREATIVE else "REVIEW_REQUIRED",
            },
            "slide_count": len(slides),
            "slides": slides,
            "status": status,
        }

    @staticmethod
    def _write_json(path: Path, payload: Dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    @staticmethod
    def file_record(path: Path) -> Dict[str, Any]:
        return {"path": str(path), "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
