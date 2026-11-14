"""Contracts for one independent vertical product Story creative."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class StoryType(str, Enum):
    """Supported creative jobs for a single, independent Story."""

    AUTO = "AUTO"
    PRODUCT_HIGHLIGHT = "PRODUCT_HIGHLIGHT"
    BENEFIT = "BENEFIT"
    USE_LIFESTYLE = "USE_LIFESTYLE"
    AESTHETIC_EMOTIONAL = "AESTHETIC_EMOTIONAL"
    LIGHT_CTA = "LIGHT_CTA"


@dataclass
class SingleStoryRequest:
    """Minimum factual and visual input for one standalone Story."""

    product_name: str
    confirmed_facts: List[str]
    product_id: str = ""
    product_category: str = ""
    story_type: StoryType = StoryType.AUTO
    content_goal: str = "DISCOVERY"
    product_reference_paths: List[str] = field(default_factory=list)
    style_reference_paths: List[str] = field(default_factory=list)
    use_nina: bool = False
    persona_reference_paths: List[str] = field(default_factory=list)
    visual_evidence: List[str] = field(default_factory=list)
    brand_palette: List[str] = field(default_factory=list)
    style_notes: List[str] = field(default_factory=list)
    external_reference_notes: List[str] = field(default_factory=list)
    trend_signals: List[str] = field(default_factory=list)
    cta_text: str = ""
    caption_requested: bool = True
    hashtags_requested: bool = True

    def __post_init__(self) -> None:
        self.product_name = self.product_name.strip()
        self.confirmed_facts = [fact.strip() for fact in self.confirmed_facts if fact.strip()]
        if isinstance(self.story_type, str):
            try:
                self.story_type = StoryType(self.story_type.upper())
            except ValueError as exc:
                allowed = ", ".join(item.value for item in StoryType)
                raise ValueError(f"story_type must be one of: {allowed}") from exc
        self.content_goal = self.content_goal.strip().upper() or "DISCOVERY"
        if not self.product_name:
            raise ValueError("product_name is required")
        if not self.confirmed_facts:
            raise ValueError("at least one confirmed fact is required")

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["story_type"] = self.story_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SingleStoryRequest":
        return cls(
            product_name=str(data.get("product_name", "")),
            confirmed_facts=list(data.get("confirmed_facts", [])),
            product_id=str(data.get("product_id", "")),
            product_category=str(data.get("product_category", "")),
            story_type=StoryType(str(data.get("story_type", "AUTO")).upper()),
            content_goal=str(data.get("content_goal", "DISCOVERY")),
            product_reference_paths=list(data.get("product_reference_paths", [])),
            style_reference_paths=list(data.get("style_reference_paths", [])),
            use_nina=bool(data.get("use_nina", False)),
            persona_reference_paths=list(data.get("persona_reference_paths", [])),
            visual_evidence=list(data.get("visual_evidence", [])),
            brand_palette=list(data.get("brand_palette", [])),
            style_notes=list(data.get("style_notes", [])),
            external_reference_notes=list(data.get("external_reference_notes", [])),
            trend_signals=list(data.get("trend_signals", [])),
            cta_text=str(data.get("cta_text", "")),
            caption_requested=bool(data.get("caption_requested", True)),
            hashtags_requested=bool(data.get("hashtags_requested", True)),
        )


@dataclass
class SingleStoryCreativePackage:
    """Provider-independent creative package for one Story image."""

    generator_name: str
    generator_version: str
    generator_status: str
    product_name: str
    confirmed_facts: List[str]
    story_type: str
    concept_title: str
    visual_concept: str
    scene_description: str
    composition_direction: str
    product_role: str
    text_hierarchy: Dict[str, str]
    headline: str
    supporting_text: str
    benefit_text: str
    cta_text: str
    decorative_elements: List[str]
    mood_keywords: List[str]
    color_direction: str
    realism_notes: List[str]
    negative_prompt: str
    final_image_prompt: str
    format_spec: Dict[str, Any]
    selection_rationale: str
    trend_application: str
    style_reference_application: str
    product_reference_paths: List[str]
    style_reference_paths: List[str]
    persona_reference_paths: List[str]
    fact_usage: Dict[str, str]
    copy_variants: List[Dict[str, str]]
    caption: str
    hashtags: List[str]
    cover_logic: Optional[str]
    final_image_prompt_ready: bool
    prompt_blockers: List[str]
    validation_status: str
    validation_errors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
