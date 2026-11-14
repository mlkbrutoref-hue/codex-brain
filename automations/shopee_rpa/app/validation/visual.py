"""Honest visual-QA result without fabricated precision scores."""
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from app.creative.proportion_policy import anatomy_checks, correction_prompt


class VisualQAStatus(str, Enum):
    NOT_EXECUTED = "NOT_EXECUTED"
    PASS = "PASS"
    REGENERATE = "REGENERATE"
    REVIEW = "REVIEW"


@dataclass(frozen=True)
class VisualQAResult:
    status: VisualQAStatus
    nina_identity: Optional[bool]
    product_identity: Optional[bool]
    anatomy: Optional[bool]
    hands: Optional[bool]
    text_artifacts: Optional[bool]
    photorealism: Optional[bool]
    scene_intent: Optional[bool]
    issues: List[str] = field(default_factory=list)
    regeneration_instructions: List[str] = field(default_factory=list)
    evaluation_method: str = "manual_or_visual_model_review"
    body_proportion_checks: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_checks(cls, *, anatomy_review=None, reviewed_image=None, nina_present=True, **checks):
        names = ("nina_identity", "product_identity", "anatomy", "hands",
                 "text_artifacts", "photorealism", "scene_intent")
        if set(checks) - set(names):
            raise ValueError("Unknown visual QA check")
        values = {name: checks.get(name) for name in names}
        if not checks:
            status = VisualQAStatus.NOT_EXECUTED
        elif any(value is None for value in values.values()):
            status = VisualQAStatus.REVIEW
        elif all(values.values()):
            status = VisualQAStatus.PASS
        else:
            status = VisualQAStatus.REGENERATE
        body = anatomy_checks(anatomy_review, reviewed_image, nina_present=nina_present) if checks else {}
        body_failures = [name for name, item in body.items() if item["status"] == "FAIL"]
        if body_failures:
            status = VisualQAStatus.REGENERATE
        elif status == VisualQAStatus.PASS and any(item["status"] == "REVIEW" for item in body.values()):
            status = VisualQAStatus.REVIEW
        issues = [name for name, value in values.items() if value is False] + body_failures
        return cls(status=status, issues=issues,
                   body_proportion_checks=body,
                   regeneration_instructions=([correction_prompt("Preserve current scene.", body_failures)] if body_failures else [f"Correct {name}" for name in issues]), **values)

    @classmethod
    def not_executed(cls) -> "VisualQAResult":
        return cls.from_checks()
