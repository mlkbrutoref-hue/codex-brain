"""3:4 layout presets that reuse the single Story layout contracts."""

from __future__ import annotations

from app.carousel.models import SlideType
from app.single_story.layout import LayoutComponent, LayoutPlan, SafeZone, StoryDirector


class CarouselLayoutDirector:
    """Builds a 1080x1440 preset for each supported carousel slide type."""

    WIDTH = 1080
    HEIGHT = 1440

    def plan(self, slide_type: SlideType) -> LayoutPlan:
        if isinstance(slide_type, str):
            slide_type = SlideType(slide_type.upper())
        return {
            SlideType.COVER: self._cover,
            SlideType.PRODUCT: self._product,
            SlideType.CTA: self._cta,
        }[slide_type]()

    def _base(self, layout_id: str, slide_type: SlideType, zones, components) -> LayoutPlan:
        return LayoutPlan(
            layout_id=layout_id,
            story_type=slide_type.value,
            canvas_width=self.WIDTH,
            canvas_height=self.HEIGHT,
            outer_safe_margin=72,
            zones=zones,
            components=components,
            palette=dict(StoryDirector.DEFAULT_PALETTE),
        )

    def _cover(self) -> LayoutPlan:
        zones = {
            "TOP_PILL_ZONE": SafeZone("TOP_PILL_ZONE", 310, 755, 460, 80),
            "HEADLINE_ZONE": SafeZone("HEADLINE_ZONE", 120, 850, 840, 300),
            "SUBHEADLINE_ZONE": SafeZone("SUBHEADLINE_ZONE", 180, 1160, 720, 130),
            "ANNOTATION_ZONE": SafeZone("ANNOTATION_ZONE", 690, 1300, 290, 70),
            "LEFT_DOODLE_ZONE": SafeZone("LEFT_DOODLE_ZONE", 105, 1265, 95, 95),
        }
        return self._base("CAROUSEL_COVER_3X4_V1", SlideType.COVER, zones, [
            LayoutComponent("PILL", "TOP_PILL_ZONE", text_key="top_pill"),
            LayoutComponent("CENTERED_HEADLINE", "HEADLINE_ZONE", text_key="headline"),
            LayoutComponent("CENTERED_SUBHEADLINE", "SUBHEADLINE_ZONE", text_key="subheadline"),
            LayoutComponent("HANDWRITTEN_ANNOTATION", "ANNOTATION_ZONE", text_key="annotation", required=False),
            LayoutComponent("OUTLINE_HEART", "LEFT_DOODLE_ZONE", required=False),
        ])

    def _product(self) -> LayoutPlan:
        zones = {
            "MICRO_HOOK_ZONE": SafeZone("MICRO_HOOK_ZONE", 72, 105, 430, 78),
            "PRODUCT_NAME_ZONE": SafeZone("PRODUCT_NAME_ZONE", 72, 205, 430, 175),
            "ANNOTATION_ZONE": SafeZone("ANNOTATION_ZONE", 730, 400, 275, 100),
            "BENEFIT_ZONE": SafeZone("BENEFIT_ZONE", 125, 1090, 830, 190),
            "RIGHT_DOODLE_ZONE": SafeZone("RIGHT_DOODLE_ZONE", 890, 955, 105, 105),
        }
        return self._base("CAROUSEL_PRODUCT_3X4_V1", SlideType.PRODUCT, zones, [
            LayoutComponent("PILL", "MICRO_HOOK_ZONE", text_key="micro_hook"),
            LayoutComponent("SUBHEADLINE", "PRODUCT_NAME_ZONE", text_key="product_name"),
            LayoutComponent("HANDWRITTEN_ANNOTATION", "ANNOTATION_ZONE", text_key="creator_annotation", required=False),
            LayoutComponent("CENTERED_BENEFIT_BOX", "BENEFIT_ZONE", text_key="benefit"),
            LayoutComponent("SPARKLE", "RIGHT_DOODLE_ZONE", required=False),
        ])

    def _cta(self) -> LayoutPlan:
        zones = {
            "QUESTION_ZONE": SafeZone("QUESTION_ZONE", 120, 250, 840, 330),
            "KEYWORD_ZONE": SafeZone("KEYWORD_ZONE", 210, 620, 660, 145),
            "CTA_ZONE": SafeZone("CTA_ZONE", 265, 805, 550, 100),
            "LEFT_DOODLE_ZONE": SafeZone("LEFT_DOODLE_ZONE", 125, 950, 120, 120),
            "RIGHT_DOODLE_ZONE": SafeZone("RIGHT_DOODLE_ZONE", 845, 960, 110, 110),
        }
        return self._base("CAROUSEL_CTA_3X4_V1", SlideType.CTA, zones, [
            LayoutComponent("CENTERED_HEADLINE", "QUESTION_ZONE", text_key="question"),
            LayoutComponent("CENTERED_SUBHEADLINE", "KEYWORD_ZONE", text_key="keyword"),
            LayoutComponent("CTA_BOX", "CTA_ZONE", text_key="cta"),
            LayoutComponent("OUTLINE_HEART", "LEFT_DOODLE_ZONE", required=False),
            LayoutComponent("SPARKLE", "RIGHT_DOODLE_ZONE", required=False),
        ])
