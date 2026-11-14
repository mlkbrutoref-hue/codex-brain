"""Deterministic and review-aware QA for 3:4 carousel slides."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

from PIL import Image

from app.carousel.models import SlideType
from app.creative.proportion_policy import ANATOMY_CHECKS, anatomy_checks
from app.single_story.qa import SingleStoryQAEvaluator


class CarouselQAEvaluator:
    WIDTH = 1080
    HEIGHT = 1440
    SEMANTIC_CHECKS = (
        "VISUAL_HIERARCHY",
        "PRODUCT_FIDELITY",
        "PRODUCT_COLOR",
        "PRODUCT_PHYSICS",
        "PERSONA_IDENTITY",
        "REALISM",
        "AI_ARTIFACTS",
        "REFERENCE_ADAPTATION",
        "BRAND_CONSISTENCY",
    )
    FULL_AI_TEXT_CHECKS = (
        "TEXT_PRESENCE",
        "TEXT_EXACTNESS",
        "SPELLING",
        "ACCENTS",
        "CTA_KEYWORD",
        "VISUAL_READABILITY",
    )
    FULL_AI_DESIGN_CHECKS = ("DESIGN_COHESION", "TEMPLATE_LOOK")

    def evaluate_full_ai(
        self,
        package: Dict[str, Any],
        final_path: Path,
        semantic_review: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Evaluate a slide whose photography, copy and graphics were generated as one image."""
        checks: Dict[str, Dict[str, Any]] = {}
        hard_failures: List[str] = []
        semantic_review = semantic_review or {}

        dimensions_ok = self._dimensions_ok(final_path)
        checks["DIMENSIONS"] = self._check(dimensions_ok, "final AI slide is 1080x1440")
        if not dimensions_ok:
            hard_failures.append("DIMENSIONS")

        has_product = bool(package.get("product_id"))
        has_persona = bool(package.get("persona_reference_paths"))
        semantic_names = (*self.SEMANTIC_CHECKS, *self.FULL_AI_TEXT_CHECKS, *self.FULL_AI_DESIGN_CHECKS)
        for name in semantic_names:
            if name.startswith("PRODUCT_") and not has_product:
                checks[name] = {"status": "PASS", "reason": "No commercial product is present on this slide."}
                continue
            if name == "PERSONA_IDENTITY" and not has_persona:
                checks[name] = {"status": "PASS", "reason": "Nina is not present on this slide."}
                continue
            if name == "CTA_KEYWORD" and package.get("slide_type") != SlideType.CTA.value:
                checks[name] = {"status": "PASS", "reason": "CTA keyword is not required on this slide type."}
                continue
            item = semantic_review.get(name, {})
            status = item.get("status")
            checks[name] = {
                "status": status if status in {"PASS", "REVIEW", "FAIL"} else "REVIEW",
                "reason": item.get("reason", "Requires explicit inspection of the final AI-composed slide."),
            }

        anatomy = anatomy_checks(semantic_review, final_path, nina_present=has_persona)
        checks.update(anatomy)
        anatomy_states = {item["status"] for item in anatomy.values()}
        body_status = "FAIL" if "FAIL" in anatomy_states else ("REVIEW" if "REVIEW" in anatomy_states else "PASS")
        checks["BODY_PROPORTIONS"] = {
            "status": body_status,
            "reason": "Aggregated evidence-aware Nina anatomy checks." if has_persona else "Nina is not present on this slide.",
        }

        all_semantic_names = (*semantic_names, "BODY_PROPORTIONS", *ANATOMY_CHECKS)
        semantic_failures = [name for name in all_semantic_names if checks[name]["status"] == "FAIL"]
        review_required = [name for name in all_semantic_names if checks[name]["status"] == "REVIEW"]
        result = "FAIL" if hard_failures or semantic_failures else ("REVIEW" if review_required else "PASS")
        return {
            "qa_result": result,
            "slide_type": package["slide_type"],
            "generation_mode": "FULL_AI_CREATIVE",
            "checks": checks,
            "hard_failures": hard_failures,
            "semantic_failures": semantic_failures,
            "review_required": review_required,
            "correction_policy": {
                "strategy": "LOCALIZED_AI_EDIT",
                "max_attempts": 1,
                "text_exhaustion_status": "TEXT_RENDER_REVIEW_REQUIRED",
            },
            "artifacts": {"rendered_image": self._artifact(final_path)},
        }

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
        semantic_review = semantic_review or {}

        dimensions_ok = self._dimensions_ok(base_image_path) and self._dimensions_ok(final_path)
        checks["DIMENSIONS"] = self._check(dimensions_ok, "base and final are 1080x1440")
        if not dimensions_ok:
            hard_failures.append("DIMENSIONS")

        with Image.open(overlay_path) as source:
            overlay_used = source.convert("RGBA").getbbox() is not None
        checks["TYPOGRAPHY_LAYER"] = self._check(overlay_used, "transparent overlay contains rendered components")
        if not overlay_used:
            hard_failures.append("TYPOGRAPHY_LAYER")

        rendered = layout.get("rendered_components", [])
        overflow = any(bool(item.get("overflow")) for item in rendered)
        checks["TEXT_OVERFLOW"] = self._check(not overflow, "rendered text stays inside its assigned zones")
        if overflow:
            hard_failures.append("TEXT_OVERFLOW")

        accuracy_errors = self._text_accuracy_errors(package, rendered)
        checks["TEXT_ACCURACY"] = self._check(not accuracy_errors, "renderer used exact slide copy", accuracy_errors)
        if accuracy_errors:
            hard_failures.append("TEXT_ACCURACY")

        safe_zone_errors = SingleStoryQAEvaluator._safe_zone_errors(layout)
        checks["SAFE_ZONES"] = self._check(not safe_zone_errors, "components remain in declared safe zones", safe_zone_errors)
        if safe_zone_errors:
            hard_failures.append("SAFE_ZONES")

        low_contrast = [
            str(item.get("component_type")) for item in rendered
            if item.get("contrast_ratio") is not None and float(item["contrast_ratio"]) < 4.5
        ]
        checks["CONTRAST"] = self._check(not low_contrast, "text meets the 4.5:1 design target", low_contrast)
        if low_contrast:
            hard_failures.append("CONTRAST")

        required_keys = {
            SlideType.COVER: ("top_pill", "headline", "subheadline"),
            SlideType.PRODUCT: ("micro_hook", "product_name", "benefit"),
            SlideType.CTA: ("question", "keyword", "cta"),
        }[SlideType(package["slide_type"])]
        rendered_keys = {item.get("source_key") for item in rendered}
        missing = [key for key in required_keys if key not in rendered_keys]
        checks["SLIDE_TYPE_REQUIREMENTS"] = self._check(not missing, f"{package['slide_type']} required copy is rendered", missing)
        if missing:
            hard_failures.append("SLIDE_TYPE_REQUIREMENTS")

        has_product = bool(package.get("product_id"))
        has_persona = bool(package.get("persona_reference_paths"))
        for name in self.SEMANTIC_CHECKS:
            if name.startswith("PRODUCT_") and not has_product:
                checks[name] = {"status": "PASS", "reason": "No commercial product is present on this slide."}
                continue
            if name == "PERSONA_IDENTITY" and not has_persona:
                checks[name] = {"status": "PASS", "reason": "Nina is not present on this slide."}
                continue
            item = semantic_review.get(name, {})
            status = item.get("status")
            checks[name] = {
                "status": status if status in {"PASS", "REVIEW", "FAIL"} else "REVIEW",
                "reason": item.get("reason", "Requires explicit visual inspection against the supplied references."),
            }

        anatomy = anatomy_checks(semantic_review, final_path, nina_present=has_persona)
        checks.update(anatomy)
        anatomy_states = {item["status"] for item in anatomy.values()}
        body_status = "FAIL" if "FAIL" in anatomy_states else ("REVIEW" if "REVIEW" in anatomy_states else "PASS")
        checks["BODY_PROPORTIONS"] = {
            "status": body_status,
            "reason": "Aggregated evidence-aware Nina anatomy checks." if has_persona else "Nina is not present on this slide.",
        }

        semantic_names = (*self.SEMANTIC_CHECKS, "BODY_PROPORTIONS", *ANATOMY_CHECKS)
        semantic_failures = [name for name in semantic_names if checks[name]["status"] == "FAIL"]
        review_required = [name for name in semantic_names if checks[name]["status"] == "REVIEW"]
        result = "FAIL" if hard_failures or semantic_failures else ("REVIEW" if review_required else "PASS")
        return {
            "qa_result": result,
            "slide_type": package["slide_type"],
            "checks": checks,
            "hard_failures": hard_failures,
            "semantic_failures": semantic_failures,
            "review_required": review_required,
            "correction_policy": {"max_attempts": 1, "on_exhaustion": "REVIEW_REQUIRED"},
            "artifacts": {
                "base_image": self._artifact(base_image_path),
                "text_overlay": self._artifact(overlay_path),
                "rendered_image": self._artifact(final_path),
            },
        }

    @classmethod
    def _dimensions_ok(cls, path: Path) -> bool:
        if not path.is_file():
            return False
        with Image.open(path) as image:
            return image.size == (cls.WIDTH, cls.HEIGHT)

    @staticmethod
    def _text_accuracy_errors(package: Dict[str, Any], rendered: List[Dict[str, Any]]) -> List[str]:
        errors: List[str] = []
        for item in rendered:
            key = item.get("source_key")
            if key and item.get("source_text") != str(package.get(key, "")).strip():
                errors.append(str(key))
        return errors

    @staticmethod
    def _check(ok: bool, reason: str, details: Optional[List[str]] = None) -> Dict[str, Any]:
        result: Dict[str, Any] = {"status": "PASS" if ok else "FAIL", "reason": reason}
        if details:
            result["details"] = details
        return result

    @staticmethod
    def _artifact(path: Path) -> Dict[str, Any]:
        return {"path": str(path), "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
