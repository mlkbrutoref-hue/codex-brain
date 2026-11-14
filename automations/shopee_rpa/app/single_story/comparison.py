"""Anti-monotony comparison for consecutive single Story outputs."""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any, Dict


class AntiMonotonyEvaluator:
    """Checks visual-system continuity and creative variation without numeric scoring."""

    def evaluate(
        self,
        baseline_package: Dict[str, Any],
        baseline_layout: Dict[str, Any],
        current_package: Dict[str, Any],
        current_layout: Dict[str, Any],
    ) -> Dict[str, Any]:
        same_brand = self._same_brand_identity(baseline_layout, current_layout)
        layout_variation = self._layout_varies(baseline_layout, current_layout)
        scene_variation = self._text_varies(
            str(baseline_package.get("scene_description", "")),
            str(current_package.get("scene_description", "")),
            maximum_similarity=0.78,
        )
        copy_variation = self._text_varies(
            self._copy_signature(baseline_package),
            self._copy_signature(current_package),
            maximum_similarity=0.72,
        )
        story_type_variation = (
            baseline_package.get("story_type") != current_package.get("story_type")
        )
        too_similar = not all((layout_variation, scene_variation, copy_variation, story_type_variation))
        status = "PASS" if same_brand and not too_similar else "FAIL"
        return {
            "ANTI_MONOTONY": status,
            "SAME_BRAND_IDENTITY": "YES" if same_brand else "NO",
            "TOO_SIMILAR_TO_FIRST_STORY": "YES" if too_similar else "NO",
            "LAYOUT_VARIATION": "PASS" if layout_variation else "FAIL",
            "SCENE_VARIATION": "PASS" if scene_variation else "FAIL",
            "COPY_VARIATION": "PASS" if copy_variation else "FAIL",
            "STORY_TYPE_VARIATION": "PASS" if story_type_variation else "FAIL",
            "baseline": {
                "story_type": baseline_package.get("story_type"),
                "layout_id": baseline_layout.get("layout_id"),
            },
            "current": {
                "story_type": current_package.get("story_type"),
                "layout_id": current_layout.get("layout_id"),
            },
            "reason": (
                "A paleta e os componentes tipográficos permanecem consistentes, enquanto tipo de Story, "
                "layout, cena e copy mudam em relação ao primeiro teste."
                if status == "PASS"
                else "A comparação detectou perda de identidade ou repetição em pelo menos um eixo criativo."
            ),
        }

    @staticmethod
    def _same_brand_identity(baseline_layout: Dict[str, Any], current_layout: Dict[str, Any]) -> bool:
        if baseline_layout.get("palette") != current_layout.get("palette"):
            return False
        required = {"PILL", "HEADLINE", "SUBHEADLINE"}
        role_aliases = {
            "CENTERED_HEADLINE": "HEADLINE",
            "CENTERED_SUBHEADLINE": "SUBHEADLINE",
            "FACT_PILL": "PILL",
        }
        baseline = {
            role_aliases.get(str(item.get("component_type")), item.get("component_type"))
            for item in baseline_layout.get("components", [])
        }
        current = {
            role_aliases.get(str(item.get("component_type")), item.get("component_type"))
            for item in current_layout.get("components", [])
        }
        return required.issubset(baseline) and required.issubset(current)

    @staticmethod
    def _layout_varies(baseline_layout: Dict[str, Any], current_layout: Dict[str, Any]) -> bool:
        if baseline_layout.get("layout_id") == current_layout.get("layout_id"):
            return False
        baseline_zone = baseline_layout.get("text_safe_zones", {}).get("HEADLINE_ZONE", {})
        current_zone = current_layout.get("text_safe_zones", {}).get("HEADLINE_ZONE", {})
        return baseline_zone.get("x") != current_zone.get("x") or baseline_zone.get("y") != current_zone.get("y")

    @staticmethod
    def _text_varies(first: str, second: str, maximum_similarity: float) -> bool:
        if not first.strip() or not second.strip():
            return False
        similarity = SequenceMatcher(None, first.casefold(), second.casefold()).ratio()
        return similarity <= maximum_similarity

    @staticmethod
    def _copy_signature(package: Dict[str, Any]) -> str:
        return " | ".join(
            str(package.get(key, ""))
            for key in ("headline", "supporting_text", "benefit_text", "cta_text")
        )
