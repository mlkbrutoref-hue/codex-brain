"""Composition-aware layout contracts for deterministic Story rendering."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


class TextLayoutError(RuntimeError):
    """Raised when exact copy cannot fit its safe zone legibly."""


@dataclass(frozen=True)
class SafeZone:
    name: str
    x: int
    y: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LayoutComponent:
    component_type: str
    zone_name: str
    text_key: str = ""
    literal_text: str = ""
    required: bool = True
    style_variant: str = "default"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LayoutPlan:
    layout_id: str
    story_type: str
    canvas_width: int = 1080
    canvas_height: int = 1920
    outer_safe_margin: int = 84
    zones: Dict[str, SafeZone] = field(default_factory=dict)
    components: List[LayoutComponent] = field(default_factory=list)
    palette: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layout_id": self.layout_id,
            "story_type": self.story_type,
            "canvas": {"width": self.canvas_width, "height": self.canvas_height},
            "outer_safe_margin": self.outer_safe_margin,
            "text_safe_zones": {name: zone.to_dict() for name, zone in self.zones.items()},
            "components": [component.to_dict() for component in self.components],
            "palette": dict(self.palette),
        }


class StoryDirector:
    """Chooses reusable components and a layout family from the creative job."""

    DEFAULT_PALETTE = {
        "cream": "#FFF7EF",
        "white": "#FFFFFF",
        "blush": "#E8B7B2",
        "blush_deep": "#C77C75",
        "espresso": "#3A2724",
        "muted_rose": "#A85E65",
    }

    def plan(self, package: Dict[str, Any]) -> LayoutPlan:
        story_type = str(package.get("story_type", "PRODUCT_HIGHLIGHT"))
        if story_type == "USE_LIFESTYLE":
            return self._lifestyle_plan(story_type, bool(package.get("cta_text")))
        if story_type == "AESTHETIC_EMOTIONAL":
            return self._aesthetic_plan(story_type)
        if story_type == "LIGHT_CTA":
            return self._cta_plan(story_type, bool(package.get("cta_text")))
        return self._editorial_left_plan(story_type, bool(package.get("cta_text")))

    def _editorial_left_plan(self, story_type: str, has_cta: bool) -> LayoutPlan:
        zones = {
            "TOP_PILL_ZONE": SafeZone("TOP_PILL_ZONE", 84, 130, 430, 78),
            "HEADLINE_ZONE": SafeZone("HEADLINE_ZONE", 84, 245, 625, 300),
            "SUPPORT_TEXT_ZONE": SafeZone("SUPPORT_TEXT_ZONE", 84, 570, 525, 175),
            "ANNOTATION_ZONE": SafeZone("ANNOTATION_ZONE", 655, 420, 310, 105),
            "BOTTOM_BENEFIT_ZONE": SafeZone("BOTTOM_BENEFIT_ZONE", 84, 1380, 470, 220),
            "CTA_ZONE": SafeZone("CTA_ZONE", 84, 1570, 390, 100),
        }
        components = [
            LayoutComponent("PILL", "TOP_PILL_ZONE", literal_text="ACHADINHO DE BELEZA"),
            LayoutComponent("HEADLINE", "HEADLINE_ZONE", text_key="headline"),
            LayoutComponent("SUBHEADLINE", "SUPPORT_TEXT_ZONE", text_key="supporting_text"),
        ]
        if story_type == "BENEFIT":
            components.extend((
                LayoutComponent("BENEFIT_BOX", "BOTTOM_BENEFIT_ZONE", text_key="benefit_text"),
                LayoutComponent(
                    "HANDWRITTEN_ANNOTATION",
                    "ANNOTATION_ZONE",
                    literal_text="olha esse detalhe",
                    required=False,
                ),
                LayoutComponent("SPARKLE", "HEADLINE_ZONE", required=False),
            ))
        if has_cta:
            components.append(LayoutComponent("CTA_BOX", "CTA_ZONE", text_key="cta_text"))
        return LayoutPlan(
            layout_id="EDITORIAL_LEFT_V1",
            story_type=story_type,
            zones=zones,
            components=components,
            palette=dict(self.DEFAULT_PALETTE),
        )

    def _lifestyle_plan(self, story_type: str, has_cta: bool) -> LayoutPlan:
        """Canonical Nina Story style: centered editorial type over a warm photo."""
        zones = {
            "HEADLINE_ZONE": SafeZone("HEADLINE_ZONE", 110, 170, 860, 330),
            "SUPPORT_TEXT_ZONE": SafeZone("SUPPORT_TEXT_ZONE", 175, 505, 730, 150),
            "LEFT_DOODLE_ZONE": SafeZone("LEFT_DOODLE_ZONE", 135, 690, 120, 120),
            "RIGHT_DOODLE_ZONE": SafeZone("RIGHT_DOODLE_ZONE", 835, 650, 110, 120),
            "FACT_PILL_ZONE": SafeZone("FACT_PILL_ZONE", 265, 1430, 550, 92),
            "BOTTOM_BENEFIT_ZONE": SafeZone("BOTTOM_BENEFIT_ZONE", 165, 1545, 750, 185),
            "CTA_ZONE": SafeZone("CTA_ZONE", 315, 1745, 450, 90),
        }
        components = [
            LayoutComponent("CENTERED_HEADLINE", "HEADLINE_ZONE", text_key="headline"),
            LayoutComponent("CENTERED_SUBHEADLINE", "SUPPORT_TEXT_ZONE", text_key="supporting_text"),
            LayoutComponent("OUTLINE_HEART", "LEFT_DOODLE_ZONE", required=False),
            LayoutComponent("SPARKLE", "RIGHT_DOODLE_ZONE", required=False),
            LayoutComponent("FACT_PILL", "FACT_PILL_ZONE", literal_text="estrutura de dois níveis"),
            LayoutComponent("CENTERED_BENEFIT_BOX", "BOTTOM_BENEFIT_ZONE", text_key="benefit_text"),
        ]
        if has_cta:
            components.append(LayoutComponent("CTA_BOX", "CTA_ZONE", text_key="cta_text"))
        return LayoutPlan(
            layout_id="NINA_SIGNATURE_CENTER_V1",
            story_type=story_type,
            zones=zones,
            components=components,
            palette=dict(self.DEFAULT_PALETTE),
        )

    def _aesthetic_plan(self, story_type: str) -> LayoutPlan:
        zones = {
            "TOP_PILL_ZONE": SafeZone("TOP_PILL_ZONE", 590, 150, 405, 78),
            "HEADLINE_ZONE": SafeZone("HEADLINE_ZONE", 84, 1220, 700, 280),
            "SUPPORT_TEXT_ZONE": SafeZone("SUPPORT_TEXT_ZONE", 84, 1510, 610, 150),
            "ANNOTATION_ZONE": SafeZone("ANNOTATION_ZONE", 710, 1590, 280, 100),
            "BOTTOM_BENEFIT_ZONE": SafeZone("BOTTOM_BENEFIT_ZONE", 84, 1260, 500, 220),
            "CTA_ZONE": SafeZone("CTA_ZONE", 84, 1690, 390, 90),
        }
        return LayoutPlan(
            layout_id="SOFT_BOTTOM_V1",
            story_type=story_type,
            zones=zones,
            components=[
                LayoutComponent("PILL", "TOP_PILL_ZONE", literal_text="DETALHES QUE ENCANTAM"),
                LayoutComponent("HEADLINE", "HEADLINE_ZONE", text_key="headline"),
                LayoutComponent("SUBHEADLINE", "SUPPORT_TEXT_ZONE", text_key="supporting_text"),
                LayoutComponent("HEART", "ANNOTATION_ZONE", required=False),
                LayoutComponent("SPARKLE", "ANNOTATION_ZONE", required=False),
            ],
            palette=dict(self.DEFAULT_PALETTE),
        )

    def _cta_plan(self, story_type: str, has_cta: bool) -> LayoutPlan:
        plan = self._editorial_left_plan(story_type, has_cta)
        plan.layout_id = "EDITORIAL_CTA_V1"
        return plan
