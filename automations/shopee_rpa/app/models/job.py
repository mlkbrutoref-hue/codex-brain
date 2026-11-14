"""Job tracking model representing the production state machine instance."""
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
from datetime import datetime
from app.models.enums import JobState


ALLOWED_TRANSITIONS = {
    JobState.CREATED: {JobState.PRODUCT_LOADED, JobState.FAILED},
    JobState.PRODUCT_LOADED: {JobState.FACTS_READY, JobState.FAILED},
    JobState.FACTS_READY: {JobState.BRIEF_READY, JobState.FAILED},
    JobState.BRIEF_READY: {JobState.HOOKS_READY, JobState.SCRIPT_READY, JobState.FAILED},
    JobState.HOOKS_READY: {JobState.SCRIPT_READY, JobState.FAILED},
    JobState.SCRIPT_READY: {JobState.STORYBOARD_READY, JobState.FAILED},
    JobState.STORYBOARD_READY: {JobState.PROMPTS_READY, JobState.FAILED},
    JobState.PROMPTS_READY: {JobState.WAITING_FOR_GENERATION, JobState.FAILED},
    JobState.WAITING_FOR_GENERATION: {JobState.GENERATING_MEDIA, JobState.REVIEW_REQUIRED, JobState.FAILED},
    JobState.GENERATING_MEDIA: {JobState.MEDIA_READY, JobState.REVIEW_REQUIRED, JobState.FAILED},
    JobState.MEDIA_READY: {JobState.VISUAL_QA, JobState.EDITING, JobState.FAILED},
    JobState.VISUAL_QA: {JobState.EDITING, JobState.REVIEW_REQUIRED, JobState.FAILED},
    JobState.EDITING: {JobState.VALIDATING, JobState.FAILED},
    JobState.VALIDATING: {JobState.PACKAGE_READY, JobState.REVIEW_REQUIRED, JobState.FAILED},
    JobState.REVIEW_REQUIRED: set(),
    JobState.PACKAGE_READY: set(),
    JobState.FAILED: set(),
}


@dataclass
class Job:
    """Production job representing an end-to-end video manufacturing workflow."""
    job_id: str
    state: JobState
    created_at: str
    updated_at: str
    product_id: str
    output_dir: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def transition_to(self, new_state: JobState, error: Optional[str] = None) -> None:
        """Transitions job to a new state and updates timestamp."""
        if new_state not in ALLOWED_TRANSITIONS.get(self.state, set()):
            raise ValueError(f"Invalid job transition: {self.state.value} -> {new_state.value}")
        self.state = new_state
        self.updated_at = datetime.now().isoformat()
        if error:
            self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "state": self.state.value if isinstance(self.state, JobState) else str(self.state),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "product_id": self.product_id,
            "output_dir": self.output_dir,
            "metadata": self.metadata,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Job":
        st = data.get("state", JobState.CREATED.value)
        if isinstance(st, str):
            st = JobState(st)
        return cls(
            job_id=str(data.get("job_id", "")),
            state=st,
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
            product_id=str(data.get("product_id", "")),
            output_dir=str(data.get("output_dir", "")),
            metadata=dict(data.get("metadata", {})),
            error=data.get("error"),
        )
