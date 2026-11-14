"""Deterministic finishing for Nina lifestyle Stories."""

from __future__ import annotations
from app.creative.proportion_policy import validate_portrait_crop

from pathlib import Path
from typing import Any, Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageOps


class LifestyleStoryRenderer:
    FONT_PATH = Path("C:/Windows/Fonts/segoeui.ttf")

    def normalize_base(self, source: Path, destination: Path) -> None:
        image = Image.open(source).convert("RGB")
        validate_portrait_crop(image.size)
        normalized = ImageOps.fit(image, (1080, 1920), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        destination.parent.mkdir(parents=True, exist_ok=True)
        normalized.save(destination, format="PNG", optimize=True)

    def render(
        self,
        base_path: Path,
        plan: Dict[str, Any],
        overlay_path: Path,
        final_path: Path,
    ) -> Dict[str, Any]:
        base = Image.open(base_path).convert("RGBA")
        if base.size != (1080, 1920):
            raise ValueError("Lifestyle base must be 1080x1920")
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        rendered_text = ""
        rendered_bbox: List[int] = []
        if plan.get("text_mode") == "LIGHT_TEXT":
            rendered_text = str(plan.get("optional_text", "")).strip()
            if not rendered_text:
                raise ValueError("LIGHT_TEXT requires optional_text")
            rendered_bbox = list(self._render_light_text(overlay, rendered_text, str(plan.get("time_of_day"))))
        overlay_path.parent.mkdir(parents=True, exist_ok=True)
        overlay.save(overlay_path, format="PNG", optimize=True)
        Image.alpha_composite(base, overlay).convert("RGB").save(final_path, format="PNG", optimize=True)
        return {
            "text_mode": plan.get("text_mode"),
            "rendered_text": rendered_text,
            "rendered_bbox": rendered_bbox,
            "text_overlay_used": bool(rendered_bbox),
            "font_path": str(self.FONT_PATH) if rendered_bbox else "",
            "safe_area": {"x": 60, "y": 150, "width": 960, "height": 1580},
            "output": {
                "base_image": str(base_path),
                "text_overlay": str(overlay_path),
                "story_final": str(final_path),
            },
        }

    def _render_light_text(self, overlay: Image.Image, text: str, time_of_day: str) -> Tuple[int, int, int, int]:
        draw = ImageDraw.Draw(overlay)
        has_droplets = "💦" in text
        display_text = text.replace("💦", "").strip()
        font_size = 58
        max_width = 760 if has_droplets else 820
        while font_size >= 36:
            font = ImageFont.truetype(str(self.FONT_PATH), font_size)
            bbox = draw.textbbox((0, 0), display_text, font=font, stroke_width=1)
            if bbox[2] - bbox[0] <= max_width:
                break
            font_size -= 2
        else:
            raise ValueError("Lifestyle overlay text does not fit")
        width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        positions = {
            "MORNING": (84, 1500),
            "AFTERNOON": (84, 1510),
            "NIGHT": (1080 - 84 - width, 240),
        }
        x, y = positions.get(time_of_day, (84, 1500))
        draw.text((x + 3, y + 4), display_text, font=font, fill=(40, 29, 27, 175), stroke_width=1)
        draw.text((x, y), display_text, font=font, fill=(255, 255, 255, 255), stroke_width=1, stroke_fill=(90, 70, 70, 130))
        extra_width = 0
        if has_droplets:
            drop_x = x + width + 20
            drop_y = y + 8
            color = (92, 181, 232, 255)
            draw.ellipse((drop_x, drop_y + 12, drop_x + 20, drop_y + 38), fill=color)
            draw.polygon(((drop_x + 10, drop_y), (drop_x + 2, drop_y + 19), (drop_x + 18, drop_y + 19)), fill=color)
            draw.ellipse((drop_x + 26, drop_y + 24, drop_x + 42, drop_y + 46), fill=color)
            draw.polygon(((drop_x + 34, drop_y + 13), (drop_x + 28, drop_y + 30), (drop_x + 40, drop_y + 30)), fill=color)
            extra_width = 52
        return (x, y, x + width + extra_width, y + height)
