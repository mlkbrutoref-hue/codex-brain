"""Future Flow operator through Antigravity. No call occurs unless explicitly enabled."""
import json
from pathlib import Path

from app.models.creative import Storyboard
from app.models.flow import (
    FlowOperationRequest, FlowOperationResult, FlowOperationState,
    SceneGenerationResult,
)
from app.providers.visual.base import VisualGenerationProvider
from app.providers.visual.manual_flow import ManualFlowProvider


class AntigravityFlowProvider(VisualGenerationProvider):
    def __init__(self, client, *, enabled=False, quota_available=False):
        self.client = client
        self.enabled = enabled
        self.quota_available = quota_available
        self._prompts = ManualFlowProvider()

    def prepare_job_prompts(self, job_output_dir: Path, storyboard: Storyboard):
        return self._prompts.prepare_job_prompts(job_output_dir, storyboard)

    def check_media_status(self, job_output_dir: Path, expected_scene_count: int):
        return self._prompts.check_media_status(job_output_dir, expected_scene_count)

    def build_operation(self, job_id, job_output_dir, storyboard, product_reference, nina_reference):
        operation = self._prompts.build_operation(
            job_id, job_output_dir, storyboard, product_reference, nina_reference
        )
        return FlowOperationRequest(job_id=operation.job_id, scenes=operation.scenes,
                                    provider="antigravity_flow")

    def start_operation(self, request):
        if not self.enabled or not self.quota_available:
            return FlowOperationResult(
                job_id=request.job_id,
                state=FlowOperationState.REVIEW_REQUIRED,
                error_code="BLOCKED_BY_ANTIGRAVITY_QUOTA",
            )
        if not all(scene.generation_authorized for scene in request.scenes):
            return FlowOperationResult(
                job_id=request.job_id,
                state=FlowOperationState.REVIEW_REQUIRED,
                error_code="GENERATION_NOT_AUTHORIZED",
            )

        payload = json.dumps(request.to_dict(), ensure_ascii=False)
        prompt = (
            "Operate Google Flow for this explicitly authorized request. Read the current UI; "
            "do not change billing, plans, credentials or unrelated projects. Return JSON only.\n"
            + payload
        )
        result = self.client.run_prompt(prompt, output_format="json", timeout=600.0)
        if not result.success or not isinstance(result.parsed_json, dict):
            return FlowOperationResult(request.job_id, FlowOperationState.FAILED,
                                       error_code="ANTIGRAVITY_EXECUTION_FAILED")
        envelope = result.parsed_json
        structured = envelope.get("structured_output")
        if envelope.get("status") != "SUCCESS" or not isinstance(structured, dict):
            return FlowOperationResult(request.job_id, FlowOperationState.REVIEW_REQUIRED,
                                       error_code="INVALID_STRUCTURED_OUTPUT")
        try:
            state = FlowOperationState(structured["state"])
            scenes = [SceneGenerationResult(
                scene_id=item["scene_id"], state=FlowOperationState(item["state"]),
                output_path=item.get("output_path"), issues=list(item.get("issues", [])),
            ) for item in structured.get("scenes", [])]
            return FlowOperationResult(request.job_id, state, scenes,
                                       structured.get("error_code"))
        except (KeyError, TypeError, ValueError):
            return FlowOperationResult(request.job_id, FlowOperationState.REVIEW_REQUIRED,
                                       error_code="INVALID_STRUCTURED_OUTPUT")
