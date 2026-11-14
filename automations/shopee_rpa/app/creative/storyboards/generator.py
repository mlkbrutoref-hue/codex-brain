"""Storyboard generator transforming scripts into dynamic scene-by-scene blueprints for any category."""
from typing import List
from app.models.product import Product
from app.models.creative import Script, Storyboard, StoryboardScene
from app.models.enums import CameraFraming
from app.creative.prompts.builder import PromptBuilder


class StoryboardGenerator:
    """Creates a visual storyboard with camera specs and generated prompts tailored dynamically to the product."""

    def __init__(self, prompt_builder: PromptBuilder | None = None):
        self.prompt_builder = prompt_builder or PromptBuilder()

    def detect_environment(self, product: Product) -> str:
        """Determines the appropriate lifestyle setting based on product category and keywords."""
        cat_lower = f"{product.category} {product.title}".lower()

        if any(w in cat_lower for w in ["cozinha", "culinária", "panela", "alimento", "processador", "liquidificador", "airfryer"]):
            return "modern bright Brazilian kitchen with clean wooden countertop and natural sunlight"
        elif any(w in cat_lower for w in ["quarto", "cama", "travesseiro", "dormitório"]):
            return "cozy modern bedroom with organized aesthetic decor and soft natural window light"
        elif any(w in cat_lower for w in ["sala", "almofada", "sofá", "decoraç", "cortina", "tapete"]):
            return "contemporary stylish living room with comfortable sofa, cozy textures and bright ambient daylight"
        elif any(w in cat_lower for w in ["escritório", "mesa", "home office", "estudo", "computador"]):
            return "clean aesthetic home office desk setup with warm natural light"
        elif any(w in cat_lower for w in ["fone", "bluetooth", "audio", "som", "eletrônic", "gadget", "smart"]):
            return "modern lifestyle apartment living area, minimalist aesthetic with soft natural daylight"
        elif any(w in cat_lower for w in ["beleza", "banheiro", "skincare", "maquiagem"]):
            return "bright clean vanity setup with mirror and soft natural daylight"
        else:
            return "bright contemporary lifestyle apartment interior with neutral tones and soft natural daylight"

    def generate(self, job_id: str, script: Script, product: Product) -> Storyboard:
        """Constructs a complete storyboard for the given script and product dynamically."""
        scenes: List[StoryboardScene] = []
        environment = self.detect_environment(product)

        framing_sequence = [
            CameraFraming.HALF_BODY,     # Scene 1: Presentation & Hook
            CameraFraming.POV_HANDS,     # Scene 2: Demonstration of features
            CameraFraming.CLOSE_UP,      # Scene 3: Detail & genuine satisfaction
            CameraFraming.HALF_BODY,     # Scene 4: Friendly closing & CTA
        ]

        title_short = product.title[:40].strip()

        for i, script_scene in enumerate(script.scenes):
            framing = framing_sequence[i % len(framing_sequence)]

            if i == 0:
                nina_action = f"Nina presenting {title_short} beside its official product reference, smiling naturally"
                product_action = f"Preserve the shape and visible details of {title_short} from the official image"
            elif i == 1:
                nina_action = f"Nina points to visible details of {title_short} without claiming unverified operation"
                product_action = f"Close view based only on the official image of {title_short}; invent no materials or parts"
            elif i == 2:
                nina_action = f"Nina presents {title_short} with a neutral, friendly expression"
                product_action = f"{title_short} remains faithful to its official image; make no scale or performance claim"
            else:
                nina_action = script_scene.visual_intent
                product_action = f"{title_short} visible from its official reference in the {environment}"

            pos_prompt, neg_prompt = self.prompt_builder.build_scene_prompts(
                framing=framing,
                nina_action=nina_action,
                product_action=product_action,
                environment=environment,
            )

            scenes.append(
                StoryboardScene(
                    scene_number=script_scene.scene_number,
                    duration_seconds=script_scene.duration_seconds,
                    framing=framing,
                    nina_action=nina_action,
                    product_action=product_action,
                    environment=environment,
                    spoken_audio_cue=script_scene.spoken_text,
                    positive_prompt=pos_prompt,
                    negative_prompt=neg_prompt,
                    reference_image="persona_master.png",
                    product_reference_image=(product.images[0] if product.images else ""),
                )
            )

        total_duration = sum(s.duration_seconds for s in scenes)

        return Storyboard(
            job_id=job_id,
            scenes=scenes,
            total_duration_seconds=round(total_duration, 1),
            aspect_ratio="9:16",
            resolution="1080x1920",
        )
