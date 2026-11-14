"""Prompt builder composing positive and negative prompts with Nina persona constraints."""
from pathlib import Path
from typing import Optional
from app.models.enums import CameraFraming
from app.creative.proportion_policy import proportion_rules, negative_constraints


class PromptBuilder:
    """Builds visual generation prompts for Google Flow or image models."""

    def __init__(self, persona_dir: Optional[Path] = None):
        if persona_dir is None:
            self.persona_dir = Path(__file__).resolve().parents[3] / "data" / "personas" / "nina_v1"
        else:
            self.persona_dir = Path(persona_dir)

        self.base_prompt = self._load_file("base_prompt.txt")
        self.negative_prompt = self._load_file("negative_prompt.txt")

    def _load_file(self, filename: str) -> str:
        target = self.persona_dir / filename
        if target.exists():
            with open(target, "r", encoding="utf-8-sig") as f:
                return f.read().strip()
        return ""

    def build_scene_prompts(
        self,
        framing: CameraFraming,
        nina_action: str,
        product_action: str,
        environment: str = "modern bright kitchen",
    ) -> tuple[str, str]:
        """Constructs positive and negative prompts for a specific scene."""
        framing_desc = {
            CameraFraming.CLOSE_UP: "Close-up portrait shot focusing on facial reaction and natural expression",
            CameraFraming.HALF_BODY: "Medium shot (waist up) showing Nina interacting casually",
            CameraFraming.FULL_BODY: "Wide full-body shot showing Nina in the lifestyle environment",
            CameraFraming.POV_HANDS: "First-person POV shot focusing on hands conservatively presenting the product",
            CameraFraming.PRODUCT_MACRO: "Macro product close-up with Nina slightly blurred in background",
        }.get(framing, "Medium shot showing Nina")

        positive = (
            f"{self.base_prompt}\n\n"
            f"[SCENE SPECIFICATIONS]\n"
            f"- Camera & Framing: {framing_desc}, 9:16 vertical social video aspect ratio.\n"
            f"- Environment: {environment}, soft natural daylight streaming from side window, cozy realistic apartment.\n"
            f"- Character Action: {nina_action}.\n"
            f"- Product Detail: {product_action}.\n"
            f"- Aesthetic & Style: Hyper-realistic raw photography, natural skin pores and micro-textures, cinematic documentary realism, 35mm lens look, no beauty filter, consistent with persona_master.png."
        )

        return positive.strip() + "\n" + proportion_rules(), self.negative_prompt + ", " + negative_constraints()
