"""Creative models: brief, script and storyboard."""
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any
from app.models.enums import ContentFormat, CameraFraming


@dataclass
class CreativeBrief:
    """Strategic brief defining tone, angle and format for the video."""
    job_id: str
    product_id: str
    persona_id: str
    format: ContentFormat
    target_audience: str
    target_angle: str
    hook_angle: str
    key_benefits: List[str] = field(default_factory=list)
    tone: str = "informal, natural, lifestyle creator"
    cta_shopee: str = ""
    cta_instagram: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "product_id": self.product_id,
            "persona_id": self.persona_id,
            "format": self.format.value if isinstance(self.format, ContentFormat) else str(self.format),
            "target_audience": self.target_audience,
            "target_angle": self.target_angle,
            "hook_angle": self.hook_angle,
            "key_benefits": list(self.key_benefits),
            "tone": self.tone,
            "cta_shopee": self.cta_shopee,
            "cta_instagram": self.cta_instagram,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreativeBrief":
        fmt = data.get("format", ContentFormat.ACHADINHO.value)
        if isinstance(fmt, str):
            fmt = ContentFormat(fmt)
        return cls(
            job_id=str(data.get("job_id", "")),
            product_id=str(data.get("product_id", "")),
            persona_id=str(data.get("persona_id", "persona_main_v1")),
            format=fmt,
            target_audience=str(data.get("target_audience", "")),
            target_angle=str(data.get("target_angle", "")),
            hook_angle=str(data.get("hook_angle", "")),
            key_benefits=list(data.get("key_benefits", [])),
            tone=str(data.get("tone", "")),
            cta_shopee=str(data.get("cta_shopee", "")),
            cta_instagram=str(data.get("cta_instagram", "")),
        )


@dataclass
class ScriptScene:
    """Individual spoken line/scene in a script."""
    scene_number: int
    duration_seconds: float
    spoken_text: str
    visual_intent: str
    referenced_fact: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScriptScene":
        return cls(
            scene_number=int(data.get("scene_number", 1)),
            duration_seconds=float(data.get("duration_seconds", 5.0)),
            spoken_text=str(data.get("spoken_text", "")),
            visual_intent=str(data.get("visual_intent", "")),
            referenced_fact=str(data.get("referenced_fact", "")),
        )


@dataclass
class Script:
    """Full spoken script for Nina."""
    format: ContentFormat
    scenes: List[ScriptScene] = field(default_factory=list)
    total_duration_seconds: float = 0.0
    full_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "format": self.format.value if isinstance(self.format, ContentFormat) else str(self.format),
            "scenes": [s.to_dict() for s in self.scenes],
            "total_duration_seconds": self.total_duration_seconds,
            "full_text": self.full_text,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Script":
        fmt = data.get("format", ContentFormat.ACHADINHO.value)
        if isinstance(fmt, str):
            fmt = ContentFormat(fmt)
        return cls(
            format=fmt,
            scenes=[ScriptScene.from_dict(s) for s in data.get("scenes", [])],
            total_duration_seconds=float(data.get("total_duration_seconds", 0.0)),
            full_text=str(data.get("full_text", "")),
        )


@dataclass
class StoryboardScene:
    """Visual take/scene specification for image and video synthesis."""
    scene_number: int
    duration_seconds: float
    framing: CameraFraming
    nina_action: str
    product_action: str
    environment: str
    spoken_audio_cue: str
    positive_prompt: str
    negative_prompt: str
    reference_image: str = "persona_master.png"
    product_reference_image: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_number": self.scene_number,
            "duration_seconds": self.duration_seconds,
            "framing": self.framing.value if isinstance(self.framing, CameraFraming) else str(self.framing),
            "nina_action": self.nina_action,
            "product_action": self.product_action,
            "environment": self.environment,
            "spoken_audio_cue": self.spoken_audio_cue,
            "positive_prompt": self.positive_prompt,
            "negative_prompt": self.negative_prompt,
            "reference_image": self.reference_image,
            "product_reference_image": self.product_reference_image,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoryboardScene":
        framing = data.get("framing", CameraFraming.HALF_BODY.value)
        if isinstance(framing, str):
            framing = CameraFraming(framing)
        return cls(
            scene_number=int(data.get("scene_number", 1)),
            duration_seconds=float(data.get("duration_seconds", 5.0)),
            framing=framing,
            nina_action=str(data.get("nina_action", "")),
            product_action=str(data.get("product_action", "")),
            environment=str(data.get("environment", "")),
            spoken_audio_cue=str(data.get("spoken_audio_cue", "")),
            positive_prompt=str(data.get("positive_prompt", "")),
            negative_prompt=str(data.get("negative_prompt", "")),
            reference_image=str(data.get("reference_image", "persona_master.png")),
            product_reference_image=str(data.get("product_reference_image", "")),
        )


@dataclass
class Storyboard:
    """Complete sequence of scenes ready for visual generation."""
    job_id: str
    scenes: List[StoryboardScene] = field(default_factory=list)
    total_duration_seconds: float = 0.0
    aspect_ratio: str = "9:16"
    resolution: str = "1080x1920"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "scenes": [s.to_dict() for s in self.scenes],
            "total_duration_seconds": self.total_duration_seconds,
            "aspect_ratio": self.aspect_ratio,
            "resolution": self.resolution,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Storyboard":
        return cls(
            job_id=str(data.get("job_id", "")),
            scenes=[StoryboardScene.from_dict(s) for s in data.get("scenes", [])],
            total_duration_seconds=float(data.get("total_duration_seconds", 0.0)),
            aspect_ratio=str(data.get("aspect_ratio", "9:16")),
            resolution=str(data.get("resolution", "1080x1920")),
        )
