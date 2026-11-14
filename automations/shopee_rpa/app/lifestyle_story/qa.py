"""Technical and semantic QA for Nina lifestyle Stories."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from PIL import Image
from app.creative.proportion_policy import anatomy_checks


class LifestyleStoryQAEvaluator:
    SEMANTIC_CHECKS = (
        "PERSONA_IDENTITY",
        "FACE_CONSISTENCY",
        "HAIR_CONSISTENCY",
        "BODY_REFERENCE_FIDELITY",
        "BODY_PLAUSIBILITY",
        "HAND_PLAUSIBILITY",
        "PHONE_PHYSICS",
        "LIGHTING",
        "REALISM",
        "AI_ARTIFACTS",
        "TIME_OF_DAY_COHERENCE",
        "SCENE_COHERENCE",
        "SPONTANEITY",
        "REFERENCE_ADAPTATION",
    )

    def evaluate(
        self,
        plan: Dict[str, Any],
        render: Dict[str, Any],
        base_path: Path,
        overlay_path: Path,
        final_path: Path,
        semantic_review: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        checks: Dict[str, Dict[str, str]] = {}
        hard_failures: List[str] = []
        dimensions_ok = self._size(base_path) == (1080, 1920) and self._size(final_path) == (1080, 1920)
        checks["OUTPUT_DIMENSIONS"] = self._check(dimensions_ok, "base and final are 1080x1920")
        if not dimensions_ok:
            hard_failures.append("OUTPUT_DIMENSIONS")

        mode = plan.get("text_mode")
        overlay_used = Image.open(overlay_path).convert("RGBA").getbbox() is not None
        overlay_ok = overlay_used if mode == "LIGHT_TEXT" else not overlay_used
        checks["TEXT_MODE"] = self._check(overlay_ok, "overlay presence matches NO_TEXT or LIGHT_TEXT")
        if not overlay_ok:
            hard_failures.append("TEXT_MODE")

        exact_text = (
            render.get("rendered_text") == plan.get("optional_text")
            if mode == "LIGHT_TEXT"
            else render.get("rendered_text") == ""
        )
        checks["TEXT_ACCURACY"] = self._check(exact_text, "deterministic overlay preserves exact optional text")
        if not exact_text:
            hard_failures.append("TEXT_ACCURACY")

        persona_ok = len(plan.get("persona_reference_paths", [])) >= 2
        checks["PERSONA_REFERENCES"] = self._check(persona_ok, "both canonical Nina references are declared")
        if not persona_ok:
            hard_failures.append("PERSONA_REFERENCES")

        anti = plan.get("anti_monotony", {})
        anti_status = anti.get("status", "REVIEW")
        checks["ANTI_MONOTONY"] = {
            "status": anti_status if anti_status in {"PASS", "REVIEW", "FAIL"} else "REVIEW",
            "reason": f"Scene signature prior exact uses: {anti.get('prior_exact_uses', 'unknown')}.",
        }

        supplied = semantic_review or {}
        for name in self.SEMANTIC_CHECKS:
            item = supplied.get(name, {})
            status = item.get("status")
            if status not in {"PASS", "REVIEW", "FAIL"}:
                checks[name] = {"status": "REVIEW", "reason": "Requires explicit visual inspection."}
            else:
                checks[name] = {"status": status, "reason": item.get("reason", "Explicit visual review.")}

        checks.update(anatomy_checks(supplied, final_path))
        failures = [name for name, item in checks.items() if item["status"] == "FAIL"]
        reviews = [name for name, item in checks.items() if item["status"] == "REVIEW"]
        result = "FAIL" if hard_failures or failures else ("REVIEW" if reviews else "PASS")
        return {
            "qa_result": result,
            "checks": checks,
            "hard_failures": hard_failures,
            "semantic_failures": [name for name in failures if name not in hard_failures],
            "review_required": reviews,
            "artifacts": {
                "base_image": self._artifact(base_path),
                "text_overlay": self._artifact(overlay_path),
                "story_final": self._artifact(final_path),
            },
        }

    @staticmethod
    def write(path: Path, report: Dict[str, Any]) -> None:
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    @staticmethod
    def _size(path: Path) -> tuple[int, int]:
        with Image.open(path) as image:
            return image.size

    @staticmethod
    def _check(ok: bool, reason: str) -> Dict[str, str]:
        return {"status": "PASS" if ok else "FAIL", "reason": reason}

    @staticmethod
    def _artifact(path: Path) -> Dict[str, Any]:
        return {"path": str(path), "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
