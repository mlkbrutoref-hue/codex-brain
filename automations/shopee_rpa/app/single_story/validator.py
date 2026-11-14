"""Validation rules for independent single-story creative packages."""

from __future__ import annotations

from typing import List

from app.single_story.models import SingleStoryCreativePackage


class SingleStoryValidator:
    """Checks format, independence, copy restraint and prompt readiness."""

    FORBIDDEN_UNVERIFIED_COPY = (
        "últimas unidades",
        "vai acabar",
        "mais vendido",
        "viral",
        "milagre",
        "garantido",
        "perfeito para todo mundo",
        "resolve sua vida",
    )

    def validate(self, package: SingleStoryCreativePackage) -> List[str]:
        errors: List[str] = []
        spec = package.format_spec
        if spec.get("aspect_ratio") != "9:16":
            errors.append("format_spec.aspect_ratio must be 9:16")
        if spec.get("width") != 1080 or spec.get("height") != 1920:
            errors.append("format_spec must be 1080x1920")
        if spec.get("artifact_count") != 1 or not spec.get("standalone"):
            errors.append("package must describe one standalone artifact")
        if not package.confirmed_facts:
            errors.append("confirmed_facts cannot be empty")
        if package.supporting_text not in package.confirmed_facts:
            errors.append("supporting_text must be copied from confirmed_facts")
        if package.benefit_text and package.benefit_text not in package.confirmed_facts:
            errors.append("benefit_text must be copied from confirmed_facts")
        if len(package.headline) > 52:
            errors.append("headline exceeds 52 characters")
        if len(package.cta_text) > 42:
            errors.append("cta_text exceeds 42 characters")
        generated_copy = " ".join((package.headline, package.cta_text)).casefold()
        for phrase in self.FORBIDDEN_UNVERIFIED_COPY:
            if phrase in generated_copy:
                errors.append(f"unverified or manipulative phrase: {phrase}")
        if package.persona_reference_paths and "NINA_PROPORTION_POLICY_V1" not in package.final_image_prompt:
            errors.append("MISSING_BODY_PROPORTION_POLICY")
        if "9:16" not in package.final_image_prompt:
            errors.append("final_image_prompt must state 9:16")
        if package.final_image_prompt_ready and not package.product_reference_paths:
            errors.append("prompt cannot be ready without a product reference")
        if package.persona_reference_paths and len(package.persona_reference_paths) < 2:
            errors.append("Nina requires both canonical persona references")
        return errors
