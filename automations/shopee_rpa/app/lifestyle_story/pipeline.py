"""Generated-image ingest and final packaging for lifestyle Stories."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from app.lifestyle_story.history import LifestyleHistoryStore
from app.lifestyle_story.qa import LifestyleStoryQAEvaluator
from app.lifestyle_story.renderer import LifestyleStoryRenderer
from app.creative.proportion_policy import write_recovery, finish_with_recovery


class LifestyleStoryPipeline:
    NAME = "NINA_REAL_LIFESTYLE_STORY_PIPELINE"
    VERSION = "1.0.0"

    def __init__(self) -> None:
        self.renderer = LifestyleStoryRenderer()
        self.qa = LifestyleStoryQAEvaluator()

    def run(
        self,
        plan_path: Path,
        generated_image_path: Path,
        output_dir: Path,
        *,
        semantic_review_path: Optional[Path] = None,
        image_provider: str = "CODEX_BUILT_IN_IMAGEGEN",
        history_path: Optional[Path] = None,
        correction_provider=None,
        visual_reviewer=None,
    ) -> Dict[str, Any]:
        plan = json.loads(Path(plan_path).read_text(encoding="utf-8-sig"))
        if plan.get("validation_status") != "PASS":
            raise ValueError("Lifestyle plan validation_status must be PASS")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "plan": output_dir / "creative_plan.json",
            "prompt": output_dir / "prompt.txt",
            "base": output_dir / "base_image.png",
            "overlay": output_dir / "text_overlay.png",
            "final": output_dir / "story_final.png",
            "render": output_dir / "render.json",
            "qa": output_dir / "qa.json",
            "asset_manifest": output_dir / "asset_manifest.json",
            "manifest": output_dir / "manifest.json",
        }
        shutil.copy2(plan_path, paths["plan"])
        paths["prompt"].write_text(str(plan.get("final_image_prompt", "")) + "\n", encoding="utf-8")
        self.renderer.normalize_base(Path(generated_image_path), paths["base"])
        render = self.renderer.render(paths["base"], plan, paths["overlay"], paths["final"])
        paths["render"].write_text(json.dumps(render, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        semantic = None
        if semantic_review_path:
            semantic = json.loads(Path(semantic_review_path).read_text(encoding="utf-8-sig"))
        report = self.qa.evaluate(plan, render, paths["base"], paths["overlay"], paths["final"], semantic)
        self.qa.write(paths["qa"], report)
        paths["anatomy_recovery"] = write_recovery(report, plan.get("final_image_prompt", ""), output_dir, paths["final"])
        assets = {
            "image_provider": image_provider,
            "flow_used": False,
            "source_generated_image": self._record(Path(generated_image_path)),
            "persona_references": plan.get("persona_reference_paths", []),
            "reference_sources": plan.get("reference_source", []),
            "font": render.get("font_path"),
        }
        paths["asset_manifest"].write_text(json.dumps(assets, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        manifest = {
            "pipeline_name": self.NAME,
            "pipeline_version": self.VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "qa_result": report["qa_result"],
            "status": "READY" if report["qa_result"] == "PASS" else "REVIEW_REQUIRED",
            "flow_used": False,
            "artifacts": {name: self._record(path) for name, path in paths.items() if path.is_file() and name != "manifest"},
        }
        paths["manifest"].write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if history_path and report["qa_result"] == "PASS":
            LifestyleHistoryStore(Path(history_path)).record(plan, str(paths["final"]))
        return finish_with_recovery(
            manifest, paths["anatomy_recovery"], output_dir, correction_provider, visual_reviewer,
            lambda image, dest, review: self.run(plan_path, image, dest,
                semantic_review_path=review, image_provider=image_provider, history_path=history_path),
        )

    @staticmethod
    def _record(path: Path) -> Dict[str, Any]:
        return {"path": str(path), "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
