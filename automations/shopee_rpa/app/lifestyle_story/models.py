"""Contracts for spontaneous, non-commercial lifestyle Stories."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List


class TimeOfDay(str, Enum):
    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"
    NIGHT = "NIGHT"


class LifestyleCategory(str, Enum):
    AUTO = "AUTO"
    SELF_CARE = "SELF_CARE"
    MIRROR_SELFIE = "MIRROR_SELFIE"
    FITNESS = "FITNESS"
    HOME_ROUTINE = "HOME_ROUTINE"
    BED_RELAX = "BED_RELAX"
    SKINCARE = "SKINCARE"
    SPONTANEOUS_MOMENT = "SPONTANEOUS_MOMENT"
    MORNING_ROUTINE = "MORNING_ROUTINE"
    MAKEUP = "MAKEUP"
    FEMALE_LIFESTYLE = "FEMALE_LIFESTYLE"
    STUDY_WORK = "STUDY_WORK"
    OUT_AND_ABOUT = "OUT_AND_ABOUT"
    NIGHT_ROUTINE = "NIGHT_ROUTINE"


class LifestyleStoryType(str, Enum):
    AUTO = "AUTO"
    CONNECTION = "CONNECTION"
    ROUTINE = "ROUTINE"
    LIFESTYLE = "LIFESTYLE"
    PRODUCT = "PRODUCT"
    HYBRID = "HYBRID"


class TextMode(str, Enum):
    AUTO = "AUTO"
    NO_TEXT = "NO_TEXT"
    LIGHT_TEXT = "LIGHT_TEXT"


@dataclass
class LifestyleStoryRequest:
    time_of_day: TimeOfDay
    category: LifestyleCategory = LifestyleCategory.AUTO
    story_type: LifestyleStoryType = LifestyleStoryType.AUTO
    text_mode: TextMode = TextMode.AUTO
    reference_sources: List[str] = field(default_factory=list)
    reference_notes: List[str] = field(default_factory=list)
    optional_text: str = ""
    day_id: str = ""
    product_context: str = ""

    def __post_init__(self) -> None:
        self.time_of_day = self._enum(self.time_of_day, TimeOfDay, "time_of_day")
        self.category = self._enum(self.category, LifestyleCategory, "category")
        self.story_type = self._enum(self.story_type, LifestyleStoryType, "story_type")
        self.text_mode = self._enum(self.text_mode, TextMode, "text_mode")
        self.reference_sources = [item.strip() for item in self.reference_sources if item.strip()]
        self.reference_notes = [item.strip() for item in self.reference_notes if item.strip()]
        self.optional_text = self.optional_text.strip()
        self.product_context = self.product_context.strip()

    @staticmethod
    def _enum(value: Any, enum_type: Any, field_name: str) -> Any:
        if isinstance(value, enum_type):
            return value
        try:
            return enum_type(str(value).upper())
        except ValueError as exc:
            allowed = ", ".join(item.value for item in enum_type)
            raise ValueError(f"{field_name} must be one of: {allowed}") from exc

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LifestyleStoryRequest":
        return cls(
            time_of_day=data.get("time_of_day", ""),
            category=data.get("category", "AUTO"),
            story_type=data.get("story_type", "AUTO"),
            text_mode=data.get("text_mode", "AUTO"),
            reference_sources=list(data.get("reference_sources", [])),
            reference_notes=list(data.get("reference_notes", [])),
            optional_text=str(data.get("optional_text", "")),
            day_id=str(data.get("day_id", "")),
            product_context=str(data.get("product_context", "")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "time_of_day": self.time_of_day.value,
            "category": self.category.value,
            "story_type": self.story_type.value,
            "text_mode": self.text_mode.value,
        }


@dataclass
class LifestyleStoryPlan:
    generator_name: str
    generator_version: str
    time_of_day: str
    category: str
    story_type: str
    text_mode: str
    reference_source: List[str]
    reference_adaptation: str
    scene_concept: str
    location: str
    action: str
    pose: str
    camera_angle: str
    camera_distance: str
    phone_position: str
    body_position: str
    hand_position: str
    wardrobe: str
    hair_state: str
    makeup_state: str
    props: List[str]
    lighting: str
    expression: str
    mood: str
    optional_text: str
    persona_reference_paths: List[str]
    realism_constraints: List[str]
    negative_prompt: str
    final_image_prompt: str
    format_spec: Dict[str, Any]
    scene_signature: str
    anti_monotony: Dict[str, Any]
    validation_status: str
    validation_errors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
