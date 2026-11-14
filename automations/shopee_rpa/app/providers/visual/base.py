"""Abstract base interface for visual media generation providers."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any
from app.models.creative import Storyboard
from app.models.flow import FlowOperationRequest, FlowOperationResult


class VisualGenerationProvider(ABC):
    """Base class for visual generators (Google Flow, manual fallback, synthetic mock)."""

    @abstractmethod
    def prepare_job_prompts(self, job_output_dir: Path, storyboard: Storyboard) -> List[Path]:
        """Prepares and writes prompt files for all scenes."""
        pass

    @abstractmethod
    def check_media_status(self, job_output_dir: Path, expected_scene_count: int) -> Dict[str, Any]:
        """Checks if generated media files are present and ready for editing."""
        pass

    @abstractmethod
    def build_operation(
        self,
        job_id: str,
        job_output_dir: Path,
        storyboard: Storyboard,
        product_reference: str,
        nina_reference: str,
    ) -> FlowOperationRequest:
        """Builds a reviewable request without starting generation."""
        pass

    @abstractmethod
    def start_operation(self, request: FlowOperationRequest) -> FlowOperationResult:
        """Starts or hands off an explicitly authorized operation."""
        pass
