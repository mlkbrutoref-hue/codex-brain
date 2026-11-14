"""Manual Google Flow Provider (primary resilient fallback)."""
from pathlib import Path
from typing import Dict, List, Any
from app.models.creative import Storyboard
from app.providers.visual.base import VisualGenerationProvider
from app.models.flow import (
    FlowOperationRequest, FlowOperationResult, FlowOperationState,
    SceneGenerationRequest, SceneGenerationResult,
)
from app.media.inventory import inspect_take_inventory


class ManualFlowProvider(VisualGenerationProvider):
    """Writes standardized scene prompts for operator/agent input into Google Flow."""

    def prepare_job_prompts(self, job_output_dir: Path, storyboard: Storyboard) -> List[Path]:
        """Writes scene_XX.txt files and workflow instructions."""
        prompts_dir = job_output_dir / "prompts"
        generated_dir = job_output_dir / "generated"

        prompts_dir.mkdir(parents=True, exist_ok=True)
        generated_dir.mkdir(parents=True, exist_ok=True)

        created_files: List[Path] = []

        for scene in storyboard.scenes:
            filename = f"scene_{scene.scene_number:02d}.txt"
            filepath = prompts_dir / filename

            file_content = (
                f"=== SCENE {scene.scene_number:02d} ({scene.duration_seconds:.1f}s) ===\n"
                f"FRAMING: {scene.framing.value}\n"
                f"REFERENCE IMAGE: {scene.reference_image}\n"
                f"PRODUCT REFERENCE: {scene.product_reference_image}\n"
                f"AUDIO CUE: \"{scene.spoken_audio_cue}\"\n\n"
                f"--- [POSITIVE PROMPT] ---\n"
                f"{scene.positive_prompt}\n\n"
                f"--- [NEGATIVE PROMPT] ---\n"
                f"{scene.negative_prompt}\n"
            )

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(file_content)

            created_files.append(filepath)

        # Also write instructions
        readme_path = prompts_dir / "INSTRUCTIONS_FLOW.md"
        instructions = (
            "# Instruções Operacionais para o Google Flow\n\n"
            "1. Abra a sessão do Google Flow.\n"
            "2. Carregue `data/personas/nina_v1/references/persona_master.png` para rosto e `data/personas/nina_v1/references/nina_360_master.png` para corpo. Se só uma for aceita, priorize o 360 para corpo inteiro e registre REVIEW para a limitação.\n"
            "3. Para cada cena (`scene_01.txt`, `scene_02.txt`, etc.):\n"
            "   - Cole o POSITIVE PROMPT no campo de prompt do Flow.\n"
            "   - Cole o NEGATIVE PROMPT no campo de exclusão/negative prompt.\n"
            "   - Gere a imagem ou take de vídeo de alta resolução (9:16 vertical).\n"
            "4. Salve os resultados gerados em:\n"
            f"   `{generated_dir}`\n"
            "   com a nomenclatura `take_01.mp4`, `take_02.mp4` (ou `.png` para imagens âncora).\n"
        )
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(instructions)
        created_files.append(readme_path)

        return created_files

    def check_media_status(self, job_output_dir: Path, expected_scene_count: int) -> Dict[str, Any]:
        """Checks deterministic ordering, extension, size and basic container signature."""
        generated_dir = job_output_dir / "generated"
        inventory = inspect_take_inventory(generated_dir, expected_scene_count)
        return {
            "all_ready": inventory.ready,
            "found_takes": [path.name for path in inventory.ordered_takes],
            "missing_scenes": inventory.missing_scenes,
            "empty_files": inventory.empty_files,
            "invalid_extensions": inventory.invalid_extensions,
            "corrupt_files": inventory.corrupt_files,
            "duplicate_scenes": inventory.duplicate_scenes,
            "message": "Todas as mídias candidatas estão prontas." if inventory.ready else "Inventário de takes inválido.",
        }

    def build_operation(self, job_id, job_output_dir, storyboard, product_reference, nina_reference):
        scenes = []
        for scene in storyboard.scenes:
            scenes.append(SceneGenerationRequest(
                job_id=job_id,
                scene_id=f"scene_{scene.scene_number:02d}",
                prompt=scene.positive_prompt + "\n\nNEGATIVE: " + scene.negative_prompt,
                nina_reference=nina_reference,
                product_reference=product_reference,
                output_path=str(job_output_dir / "generated" / f"take_{scene.scene_number:02d}.mp4"),
                generation_authorized=False,
            ))
        return FlowOperationRequest(job_id=job_id, scenes=scenes, provider="manual_flow")

    def start_operation(self, request):
        # Manual provider never clicks Generate. It returns a handoff state.
        return FlowOperationResult(
            job_id=request.job_id,
            state=FlowOperationState.READY,
            scenes=[SceneGenerationResult(scene.scene_id, FlowOperationState.READY)
                    for scene in request.scenes],
        )
