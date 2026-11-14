"""Typed contracts between Python orchestration and future Flow operators."""
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class FlowOperationState(str, Enum):
    READY = "READY"
    LOGIN_REQUIRED = "LOGIN_REQUIRED"
    GENERATING = "GENERATING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


@dataclass(frozen=True)
class SceneGenerationRequest:
    job_id: str
    scene_id: str
    prompt: str
    nina_reference: str
    product_reference: str
    output_path: str
    generation_authorized: bool = False

    def __post_init__(self):
        required = (self.job_id, self.scene_id, self.prompt, self.nina_reference,
                    self.product_reference, self.output_path)
        if any(not value or not str(value).strip() for value in required):
            raise ValueError("Scene generation request has empty required fields")
        if not self.scene_id.startswith("scene_"):
            raise ValueError("scene_id must use scene_XX naming")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SceneGenerationResult:
    scene_id: str
    state: FlowOperationState
    output_path: Optional[str] = None
    issues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["state"] = self.state.value
        return data


@dataclass(frozen=True)
class FlowOperationRequest:
    job_id: str
    scenes: List[SceneGenerationRequest]
    provider: str

    def __post_init__(self):
        if not self.job_id or not self.scenes:
            raise ValueError("Flow operation requires job and scenes")
        if any(scene.job_id != self.job_id for scene in self.scenes):
            raise ValueError("All scenes must belong to the operation job")

    def to_dict(self) -> Dict[str, Any]:
        return {"job_id": self.job_id, "provider": self.provider,
                "scenes": [scene.to_dict() for scene in self.scenes]}


@dataclass(frozen=True)
class FlowOperationResult:
    job_id: str
    state: FlowOperationState
    scenes: List[SceneGenerationResult] = field(default_factory=list)
    error_code: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"job_id": self.job_id, "state": self.state.value,
                "scenes": [scene.to_dict() for scene in self.scenes],
                "error_code": self.error_code}
