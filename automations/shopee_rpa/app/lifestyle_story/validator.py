"""Validation rules for lifestyle Story plans."""

from __future__ import annotations

from pathlib import Path
from typing import List

from app.lifestyle_story.models import LifestyleStoryPlan


class LifestyleStoryValidator:
    def validate(self, plan: LifestyleStoryPlan) -> List[str]:
        errors: List[str] = []
        if len(plan.persona_reference_paths) < 2:
            errors.append("MISSING_CANONICAL_NINA_REFERENCES")
        elif not all(Path(path).is_file() for path in plan.persona_reference_paths):
            errors.append("UNRESOLVABLE_NINA_REFERENCE")
        if plan.text_mode == "NO_TEXT" and plan.optional_text:
            errors.append("NO_TEXT_MODE_HAS_COPY")
        if plan.text_mode == "LIGHT_TEXT" and not plan.optional_text:
            errors.append("LIGHT_TEXT_MODE_MISSING_COPY")
        if len(plan.optional_text) > 36:
            errors.append("LIGHT_TEXT_TOO_LONG")
        if plan.story_type == "PRODUCT" and not plan.reference_source:
            errors.append("PRODUCT_STORY_REQUIRES_REFERENCE")
        if "NINA_PROPORTION_POLICY_V1" not in plan.final_image_prompt:
            errors.append("MISSING_BODY_PROPORTION_POLICY")
        if not plan.final_image_prompt.strip():
            errors.append("MISSING_FINAL_IMAGE_PROMPT")
        if plan.format_spec.get("aspect_ratio") != "9:16":
            errors.append("INVALID_ASPECT_RATIO")
        return errors
