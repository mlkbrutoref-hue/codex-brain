"""Real single Story pipeline: generated image ingest -> typography -> QA -> manifest."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from PIL import __version__ as PILLOW_VERSION

from app.single_story.comparison import AntiMonotonyEvaluator
from app.single_story.layout import StoryDirector, TextLayoutError
from app.single_story.qa import SingleStoryQAEvaluator
from app.single_story.renderer import StoryTypographyRenderer
from app.creative.proportion_policy import write_recovery, finish_with_recovery


class RealSingleStoryPipeline:
    """Builds final static Story assets without invoking Google Flow."""

    PIPELINE_NAME = "NINA_REAL_SINGLE_STORY_PIPELINE"
    PIPELINE_VERSION = "1.0.0"

    def __init__(
        self,
        director: Optional[StoryDirector] = None,
        renderer: Optional[StoryTypographyRenderer] = None,
        qa: Optional[SingleStoryQAEvaluator] = None,
        anti_monotony: Optional[AntiMonotonyEvaluator] = None,
    ) -> None:
        self.director = director or StoryDirector()
        self.renderer = renderer or StoryTypographyRenderer()
        self.qa = qa or SingleStoryQAEvaluator()
        self.anti_monotony = anti_monotony or AntiMonotonyEvaluator()

    def run(
        self,
        creative_package_path: Path,
        generated_image_path: Path,
        output_dir: Path,
        *,
        image_provider: str = "CODEX_BUILT_IN_IMAGEGEN",
        prompt_path: Optional[Path] = None,
        semantic_review_path: Optional[Path] = None,
        comparison_baseline_dir: Optional[Path] = None,
        correction_provider=None,
        visual_reviewer=None,
    ) -> Dict[str, Any]:
        creative_package_path = Path(creative_package_path)
        generated_image_path = Path(generated_image_path)
        output_dir = Path(output_dir)
        if not creative_package_path.is_file():
            raise FileNotFoundError(f"Creative package missing: {creative_package_path}")
        if not generated_image_path.is_file():
            raise FileNotFoundError(f"Generated image missing: {generated_image_path}")
        package = json.loads(creative_package_path.read_text(encoding="utf-8-sig"))
        if package.get("validation_status") != "PASS":
            raise ValueError("creative_package.validation_status must be PASS")
        if not package.get("final_image_prompt_ready"):
            raise ValueError("creative_package.final_image_prompt_ready must be true")

        output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "creative_package": output_dir / "creative_package.json",
            "base_image": output_dir / "base_image.png",
            "text_overlay": output_dir / "text_overlay.png",
            "story_final": output_dir / "story_final.png",
            "layout": output_dir / "layout.json",
            "qa": output_dir / "qa.json",
            "manifest": output_dir / "manifest.json",
            "asset_manifest": output_dir / "asset_manifest.json",
            "prompt": output_dir / "prompt.txt",
        }
        shutil.copy2(creative_package_path, paths["creative_package"])
        if prompt_path and Path(prompt_path).is_file():
            shutil.copy2(prompt_path, paths["prompt"])
        else:
            paths["prompt"].write_text(str(package.get("final_image_prompt", "")) + "\n", encoding="utf-8")

        self.renderer.normalize_base(generated_image_path, paths["base_image"])
        plan = self.director.plan(package)
        try:
            layout = self.renderer.render(
                paths["base_image"], package, plan, paths["text_overlay"], paths["story_final"]
            )
        except TextLayoutError:
            self._write_failure_manifest(paths["manifest"], image_provider, "TEXT_LAYOUT_FAIL")
            raise
        paths["layout"].write_text(
            json.dumps(layout, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        semantic_review = None
        if semantic_review_path and Path(semantic_review_path).is_file():
            semantic_review = json.loads(Path(semantic_review_path).read_text(encoding="utf-8-sig"))
        report = self.qa.evaluate(
            package,
            layout,
            paths["base_image"],
            paths["text_overlay"],
            paths["story_final"],
            semantic_review=semantic_review,
        )
        if comparison_baseline_dir:
            baseline_dir = Path(comparison_baseline_dir)
            baseline_package = json.loads(
                (baseline_dir / "creative_package.json").read_text(encoding="utf-8-sig")
            )
            baseline_layout = json.loads(
                (baseline_dir / "layout.json").read_text(encoding="utf-8-sig")
            )
            comparison = self.anti_monotony.evaluate(
                baseline_package, baseline_layout, package, layout
            )
            report["anti_monotony"] = comparison
            report["checks"]["ANTI_MONOTONY"] = {
                "status": comparison["ANTI_MONOTONY"],
                "reason": comparison["reason"],
            }
            if comparison["ANTI_MONOTONY"] == "FAIL":
                report["qa_result"] = "FAIL"
                report["semantic_failures"].append("ANTI_MONOTONY")
        self.qa.write(paths["qa"], report)
        paths["anatomy_recovery"] = write_recovery(report, package.get("final_image_prompt", ""), output_dir, paths["story_final"])

        asset_manifest = {
            "image_provider": image_provider,
            "flow_used": False,
            "typography_engine": "Pillow",
            "typography_engine_version": PILLOW_VERSION,
            "generation_operation": "built-in image generation followed by local deterministic ingest",
            "source_generated_image": self._file_record(generated_image_path),
            "product_references": package.get("product_reference_paths", []),
            "style_references": package.get("style_reference_paths", []),
            "persona_references": package.get("persona_reference_paths", []),
            "fonts": sorted({
                component["font_path"]
                for component in layout["rendered_components"]
                if component.get("font_path")
            }),
        }
        paths["asset_manifest"].write_text(
            json.dumps(asset_manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        manifest = {
            "pipeline_name": self.PIPELINE_NAME,
            "pipeline_version": self.PIPELINE_VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "image_provider": image_provider,
            "flow_used": False,
            "typography_engine": "Pillow",
            "typography_engine_version": PILLOW_VERSION,
            "qa_result": report["qa_result"],
            "status": "READY" if report["qa_result"] == "PASS" else "REVIEW_REQUIRED",
            "artifacts": {
                name: self._file_record(path)
                for name, path in paths.items()
                if path.is_file() and name != "manifest"
            },
        }
        paths["manifest"].write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return finish_with_recovery(
            manifest, paths["anatomy_recovery"], output_dir, correction_provider, visual_reviewer,
            lambda image, dest, review: self.run(creative_package_path, image, dest,
                semantic_review_path=review, image_provider=image_provider,
                comparison_baseline_dir=comparison_baseline_dir),
        )

    def refresh_qa(
        self,
        output_dir: Path,
        semantic_review_path: Path,
    ) -> Dict[str, Any]:
        output_dir = Path(output_dir)
        package = json.loads((output_dir / "creative_package.json").read_text(encoding="utf-8-sig"))
        layout = json.loads((output_dir / "layout.json").read_text(encoding="utf-8-sig"))
        review = json.loads(Path(semantic_review_path).read_text(encoding="utf-8-sig"))
        report = self.qa.evaluate(
            package,
            layout,
            output_dir / "base_image.png",
            output_dir / "text_overlay.png",
            output_dir / "story_final.png",
            semantic_review=review,
        )
        self.qa.write(output_dir / "qa.json", report)
        recovery_path = write_recovery(report, package.get("final_image_prompt", ""), output_dir, output_dir / "story_final.png")
        manifest_path = output_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        manifest["qa_result"] = report["qa_result"]
        manifest["status"] = "READY" if report["qa_result"] == "PASS" else "REVIEW_REQUIRED"
        manifest["artifacts"]["qa"] = self._file_record(output_dir / "qa.json")
        manifest["artifacts"]["anatomy_recovery"] = self._file_record(recovery_path)
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return report

    @staticmethod
    def _file_record(path: Path) -> Dict[str, Any]:
        return {
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }

    def _write_failure_manifest(self, path: Path, image_provider: str, reason: str) -> None:
        path.write_text(json.dumps({
            "pipeline_name": self.PIPELINE_NAME,
            "pipeline_version": self.PIPELINE_VERSION,
            "image_provider": image_provider,
            "flow_used": False,
            "status": "FAIL",
            "failure": reason,
        }, indent=2) + "\n", encoding="utf-8")
