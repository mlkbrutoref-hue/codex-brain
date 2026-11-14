"""Technical and review-aware QA for rendered single Story assets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from PIL import Image
from app.creative.proportion_policy import anatomy_checks, ANATOMY_CHECKS


class SingleStoryQAEvaluator:
    """Combines deterministic checks with explicit semantic visual review."""

    SEMANTIC_CHECKS = (
        "PRODUCT_FIDELITY",
        "PRODUCT_COLOR",
        "PRODUCT_PHYSICS",
        "PERSONA_CONSISTENCY",
        "REALISM",
        "AI_ARTIFACTS",
        "COMPOSITION",
        "VISUAL_HIERARCHY",
        "BRAND_CONSISTENCY",
    )

    def evaluate(
        self,
        package: Dict[str, Any],
        layout: Dict[str, Any],
        base_image_path: Path,
        overlay_path: Path,
        final_path: Path,
        semantic_review: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        checks: Dict[str, Dict[str, Any]] = {}
        hard_failures: List[str] = []

        dimensions_ok = self._dimensions_ok(base_image_path) and self._dimensions_ok(final_path)
        checks["OUTPUT_DIMENSIONS"] = self._check(dimensions_ok, "base and final are 1080x1920")
        if not dimensions_ok:
            hard_failures.append("OUTPUT_DIMENSIONS")

        with Image.open(overlay_path) as overlay_source:
            overlay = overlay_source.convert("RGBA")
            overlay_used = overlay.getbbox() is not None
        checks["TYPOGRAPHY_LAYER"] = self._check(overlay_used, "transparent overlay contains rendered components")
        if not overlay_used:
            hard_failures.append("TYPOGRAPHY_LAYER")

        rendered = layout.get("rendered_components", [])
        overflow = any(bool(component.get("overflow")) for component in rendered)
        checks["TEXT_OVERFLOW"] = self._check(not overflow, "all rendered bounds stay inside their assigned zones")
        if overflow:
            hard_failures.append("TEXT_OVERFLOW")

        accuracy_errors = self._text_accuracy_errors(package, rendered)
        checks["TEXT_ACCURACY"] = self._check(not accuracy_errors, "renderer used exact creative_package strings", accuracy_errors)
        if accuracy_errors:
            hard_failures.append("TEXT_ACCURACY")

        low_contrast = [
            item.get("component_type")
            for item in rendered
            if item.get("contrast_ratio") is not None and float(item["contrast_ratio"]) < 4.5
        ]
        checks["TEXT_CONTRAST"] = self._check(not low_contrast, "text components meet 4.5:1 design target", low_contrast)
        if low_contrast:
            hard_failures.append("TEXT_CONTRAST")

        safe_zone_errors = self._safe_zone_errors(layout)
        checks["SAFE_ZONES"] = self._check(not safe_zone_errors, "every component remains in its declared text safe zone", safe_zone_errors)
        if safe_zone_errors:
            hard_failures.append("SAFE_ZONES")

        semantic_review = semantic_review or {}
        for name in self.SEMANTIC_CHECKS:
            if name == "PERSONA_CONSISTENCY" and not package.get("persona_reference_paths"):
                checks[name] = {"status": "PASS", "reason": "Nina is not present in this Story."}
                continue
            supplied = semantic_review.get(name)
            if supplied and supplied.get("status") in {"PASS", "REVIEW", "FAIL"}:
                checks[name] = {
                    "status": supplied["status"],
                    "reason": supplied.get("reason", "Explicit visual review."),
                }
            else:
                checks[name] = {
                    "status": "REVIEW",
                    "reason": "Requires visual inspection against the official reference and scene intent.",
                }

        checks.update(anatomy_checks(semantic_review, final_path, nina_present=bool(package.get("persona_reference_paths"))))
        semantic_failures = [name for name in (*self.SEMANTIC_CHECKS, *ANATOMY_CHECKS) if checks[name]["status"] == "FAIL"]
        semantic_reviews = [name for name in (*self.SEMANTIC_CHECKS, *ANATOMY_CHECKS) if checks[name]["status"] == "REVIEW"]
        if hard_failures or semantic_failures:
            result = "FAIL"
        elif semantic_reviews:
            result = "REVIEW"
        else:
            result = "PASS"
        return {
            "qa_result": result,
            "checks": checks,
            "hard_failures": hard_failures,
            "semantic_failures": semantic_failures,
            "review_required": semantic_reviews,
            "correction_policy": {
                "text_only": "rerender text_overlay and story_final; preserve base_image",
                "layout_only": "change layout.json and rerender; preserve base_image",
                "localized_image_issue": "use localized image edit when available",
                "full_regeneration": "last resort for product, physics, realism or composition failure",
            },
            "artifacts": {
                "base_image": self._artifact(base_image_path),
                "text_overlay": self._artifact(overlay_path),
                "story_final": self._artifact(final_path),
            },
        }

    @staticmethod
    def write(path: Path, report: Dict[str, Any]) -> None:
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    @staticmethod
    def _dimensions_ok(path: Path) -> bool:
        if not path.is_file():
            return False
        with Image.open(path) as image:
            return image.size == (1080, 1920)

    @staticmethod
    def _check(ok: bool, reason: str, details: Optional[List[str]] = None) -> Dict[str, Any]:
        item: Dict[str, Any] = {"status": "PASS" if ok else "FAIL", "reason": reason}
        if details:
            item["details"] = details
        return item

    @staticmethod
    def _text_accuracy_errors(package: Dict[str, Any], rendered: List[Dict[str, Any]]) -> List[str]:
        by_key = {
            item.get("source_key"): item.get("source_text")
            for item in rendered
            if item.get("source_key")
        }
        errors: List[str] = []
        for key in ("headline", "supporting_text", "benefit_text", "cta_text"):
            expected = str(package.get(key, "")).strip()
            if not expected:
                continue
            if by_key.get(key) != expected:
                errors.append(key)
        return errors

    @staticmethod
    def _safe_zone_errors(layout: Dict[str, Any]) -> List[str]:
        zones = layout.get("text_safe_zones", {})
        errors: List[str] = []
        for component in layout.get("rendered_components", []):
            zone = zones.get(component.get("zone_name"), {})
            box = component.get("rendered_bbox") or []
            if len(box) != 4 or not zone:
                errors.append(str(component.get("component_type")))
                continue
            right = int(zone["x"]) + int(zone["width"])
            bottom = int(zone["y"]) + int(zone["height"])
            if box[0] < zone["x"] or box[1] < zone["y"] or box[2] > right or box[3] > bottom:
                errors.append(str(component.get("component_type")))
        return errors

    @staticmethod
    def _artifact(path: Path) -> Dict[str, Any]:
        return {
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
