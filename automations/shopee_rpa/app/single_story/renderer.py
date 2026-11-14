"""Deterministic Pillow renderer for exact Story typography and graphics."""

from __future__ import annotations
from app.creative.proportion_policy import validate_portrait_crop

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageStat

from app.single_story.layout import LayoutPlan, SafeZone, TextLayoutError


@dataclass
class FittedText:
    text: str
    lines: List[str]
    font: ImageFont.FreeTypeFont
    font_size: int
    line_height: int
    width: int
    height: int


class FontResolver:
    """Resolves stable Windows fonts with explicit semantic roles."""

    DEFAULTS = {
        "headline": Path("C:/Windows/Fonts/georgiab.ttf"),
        "secondary": Path("C:/Windows/Fonts/georgiai.ttf"),
        "body": Path("C:/Windows/Fonts/georgia.ttf"),
        "annotation": Path("C:/Windows/Fonts/segoepr.ttf"),
        "ui": Path("C:/Windows/Fonts/segoeuib.ttf"),
    }

    def resolve(self, role: str) -> Path:
        path = self.DEFAULTS[role]
        if not path.is_file():
            raise FileNotFoundError(f"Required font is missing: {path}")
        return path


class StoryTypographyRenderer:
    """Renders exact text, reusable components and vector accents."""

    def __init__(self, font_resolver: FontResolver | None = None) -> None:
        self.fonts = font_resolver or FontResolver()

    def normalize_base(self, source: Path, destination: Path, size: Tuple[int, int] = (1080, 1920)) -> None:
        image = Image.open(source).convert("RGB")
        validate_portrait_crop(image.size, size)
        normalized = ImageOps.fit(image, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        destination.parent.mkdir(parents=True, exist_ok=True)
        normalized.save(destination, format="PNG", optimize=True)

    def render(
        self,
        base_path: Path,
        package: Dict[str, Any],
        plan: LayoutPlan,
        overlay_path: Path,
        final_path: Path,
    ) -> Dict[str, Any]:
        base = Image.open(base_path).convert("RGBA")
        if base.size != (plan.canvas_width, plan.canvas_height):
            raise ValueError(f"base image must be {plan.canvas_width}x{plan.canvas_height}")
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        rendered: List[Dict[str, Any]] = []

        for component in plan.components:
            zone = plan.zones[component.zone_name]
            text = component.literal_text or str(package.get(component.text_key, "")).strip()
            if component.text_key and not text:
                if component.required:
                    raise TextLayoutError(f"TEXT_LAYOUT_FAIL: missing {component.text_key}")
                continue
            result = self._render_component(
                draw,
                base,
                component.component_type,
                zone,
                text,
                plan,
                component.style_variant,
            )
            if result:
                result.update({
                    "component_type": component.component_type,
                    "zone_name": component.zone_name,
                    "source_key": component.text_key or None,
                    "source_text": text or None,
                })
                rendered.append(result)

        overlay_path.parent.mkdir(parents=True, exist_ok=True)
        overlay.save(overlay_path, format="PNG", optimize=True)
        final = Image.alpha_composite(base, overlay).convert("RGB")
        final.save(final_path, format="PNG", optimize=True)
        return {
            **plan.to_dict(),
            "text_layout_status": "PASS",
            "rendered_components": rendered,
            "output": {
                "base_image": str(base_path),
                "text_overlay": str(overlay_path),
                "story_final": str(final_path),
            },
        }

    def _render_component(
        self,
        draw: ImageDraw.ImageDraw,
        base: Image.Image,
        component_type: str,
        zone: SafeZone,
        text: str,
        plan: LayoutPlan,
        style_variant: str = "default",
    ) -> Dict[str, Any]:
        palette = plan.palette
        if component_type == "PILL":
            return self._render_pill(draw, zone, text, palette)
        if component_type == "HEADLINE":
            return self._render_headline(draw, base, zone, text, palette)
        if component_type == "CENTERED_HEADLINE":
            return self._render_centered_headline(draw, zone, text, palette)
        if component_type == "SUBHEADLINE":
            return self._render_subheadline(
                draw, base, zone, text, palette, force_panel=style_variant == "panel"
            )
        if component_type == "CENTERED_SUBHEADLINE":
            return self._render_centered_subheadline(draw, zone, text, palette)
        if component_type == "BENEFIT_BOX":
            return self._render_benefit(draw, zone, text, palette)
        if component_type == "CENTERED_BENEFIT_BOX":
            return self._render_centered_benefit(draw, zone, text, palette)
        if component_type == "FACT_PILL":
            return self._render_fact_pill(draw, zone, text, palette)
        if component_type == "CTA_BOX":
            return self._render_cta(draw, zone, text, palette)
        if component_type == "HANDWRITTEN_ANNOTATION":
            return self._render_annotation(draw, zone, text, palette)
        if component_type == "SPARKLE":
            self._draw_sparkle(draw, zone.right - 42, zone.y + 36, 18, self._rgba(palette["blush_deep"]))
            return self._shape_result(zone, "vector sparkle")
        if component_type == "HEART":
            self._draw_heart(draw, zone.x + 35, zone.y + 25, 30, self._rgba(palette["muted_rose"]))
            return self._shape_result(zone, "vector heart")
        if component_type == "OUTLINE_HEART":
            self._draw_outline_heart(draw, zone, self._rgba(palette["blush"]), width=7)
            return self._shape_result(zone, "outline heart doodle")
        if component_type == "ARROW":
            self._draw_arrow(draw, zone, self._rgba(palette["muted_rose"]))
            return self._shape_result(zone, "vector arrow")
        if component_type == "SMALL_ICON":
            draw.ellipse((zone.x, zone.y, zone.x + 42, zone.y + 42), outline=self._rgba(palette["espresso"]), width=4)
            return self._shape_result(zone, "vector icon")
        raise ValueError(f"Unsupported component type: {component_type}")

    def _render_pill(self, draw: ImageDraw.ImageDraw, zone: SafeZone, text: str, palette: Dict[str, str]) -> Dict[str, Any]:
        padding_x, padding_y = 26, 15
        fitted = self._fit_text(text.upper(), "ui", zone.width - 2 * padding_x, zone.height - 2 * padding_y, 31, 22, 1, 1.05)
        width = min(zone.width, fitted.width + 2 * padding_x)
        height = min(zone.height, fitted.height + 2 * padding_y)
        box = (zone.x, zone.y, zone.x + width, zone.y + height)
        draw.rounded_rectangle(box, radius=height // 2, fill=self._rgba(palette["blush"], 242))
        text_x = zone.x + (width - fitted.width) // 2
        text_y = zone.y + (height - fitted.height) // 2 - 2
        draw.multiline_text((text_x, text_y), "\n".join(fitted.lines), font=fitted.font, fill=self._rgba(palette["espresso"]), spacing=0)
        return self._text_result(zone, box, fitted, self.fonts.resolve("ui"), 8.0, "opaque blush pill")

    def _render_headline(self, draw: ImageDraw.ImageDraw, base: Image.Image, zone: SafeZone, text: str, palette: Dict[str, str]) -> Dict[str, Any]:
        fitted = self._fit_text(text, "headline", zone.width, zone.height, 94, 58, 3, 0.94)
        color, ratio, strategy = self._choose_text_color(base, zone, palette)
        if ratio < 4.5:
            self._draw_soft_backdrop(draw, zone, palette)
            color = self._rgba(palette["espresso"])
            ratio = 10.2
            strategy = "soft cream backdrop"
        y = zone.y + max(0, (zone.height - fitted.height) // 2)
        draw.multiline_text(
            (zone.x, y),
            "\n".join(fitted.lines),
            font=fitted.font,
            fill=color,
            spacing=max(0, fitted.line_height - fitted.font_size),
            stroke_width=1,
            stroke_fill=self._rgba("#FFF7EF", 95),
        )
        box = (zone.x, y, zone.x + fitted.width, y + fitted.height)
        return self._text_result(zone, box, fitted, self.fonts.resolve("headline"), ratio, strategy)

    def _render_subheadline(
        self,
        draw: ImageDraw.ImageDraw,
        base: Image.Image,
        zone: SafeZone,
        text: str,
        palette: Dict[str, str],
        *,
        force_panel: bool = False,
    ) -> Dict[str, Any]:
        fitted = self._fit_text(text, "secondary", zone.width - 34, zone.height - 22, 43, 31, 4, 1.14)
        color, ratio, strategy = self._choose_text_color(base, zone, palette)
        if force_panel or ratio < 4.5:
            draw.rounded_rectangle((zone.x - 18, zone.y - 10, zone.right, zone.bottom), radius=24, fill=self._rgba(palette["cream"], 215))
            color = self._rgba(palette["espresso"])
            ratio = 9.8
            strategy = "planned translucent cream panel" if force_panel else "translucent cream box"
        y = zone.y + max(0, (zone.height - fitted.height) // 2)
        draw.multiline_text((zone.x, y), "\n".join(fitted.lines), font=fitted.font, fill=color, spacing=max(0, fitted.line_height - fitted.font_size))
        box = (zone.x, y, zone.x + fitted.width, y + fitted.height)
        return self._text_result(zone, box, fitted, self.fonts.resolve("secondary"), ratio, strategy)

    def _render_centered_headline(
        self,
        draw: ImageDraw.ImageDraw,
        zone: SafeZone,
        text: str,
        palette: Dict[str, str],
    ) -> Dict[str, Any]:
        fitted = self._fit_text(text, "headline", zone.width, zone.height, 104, 58, 4, 0.9)
        x = zone.x + (zone.width - fitted.width) // 2
        y = zone.y + (zone.height - fitted.height) // 2
        spacing = max(0, fitted.line_height - fitted.font_size)
        rendered = "\n".join(fitted.lines)
        draw.multiline_text(
            (x + 3, y + 5),
            rendered,
            font=fitted.font,
            fill=self._rgba(palette["espresso"], 150),
            spacing=spacing,
            align="center",
        )
        draw.multiline_text(
            (x, y),
            rendered,
            font=fitted.font,
            fill=self._rgba(palette["white"]),
            spacing=spacing,
            align="center",
            stroke_width=1,
            stroke_fill=self._rgba(palette["espresso"], 90),
        )
        box = (x, y, x + fitted.width, y + fitted.height)
        return self._text_result(
            zone, box, fitted, self.fonts.resolve("headline"), 7.2, "white editorial type with cocoa shadow"
        )

    def _render_centered_subheadline(
        self,
        draw: ImageDraw.ImageDraw,
        zone: SafeZone,
        text: str,
        palette: Dict[str, str],
    ) -> Dict[str, Any]:
        fitted = self._fit_text(text, "body", zone.width, zone.height, 45, 30, 3, 1.04)
        x = zone.x + (zone.width - fitted.width) // 2
        y = zone.y + (zone.height - fitted.height) // 2
        rendered = "\n".join(fitted.lines)
        draw.multiline_text(
            (x + 2, y + 3), rendered, font=fitted.font,
            fill=self._rgba(palette["espresso"], 155), spacing=3, align="center"
        )
        draw.multiline_text(
            (x, y), rendered, font=fitted.font,
            fill=self._rgba(palette["white"]), spacing=3, align="center"
        )
        box = (x, y, x + fitted.width, y + fitted.height)
        return self._text_result(
            zone, box, fitted, self.fonts.resolve("body"), 6.8, "centered white type with cocoa shadow"
        )

    def _render_fact_pill(
        self,
        draw: ImageDraw.ImageDraw,
        zone: SafeZone,
        text: str,
        palette: Dict[str, str],
    ) -> Dict[str, Any]:
        icon_width = 58
        fitted = self._fit_text(text, "body", zone.width - icon_width - 54, zone.height - 26, 34, 25, 2, 1.0)
        box = (zone.x, zone.y, zone.right, zone.bottom)
        draw.rounded_rectangle(box, radius=zone.height // 2, fill=self._rgba(palette["blush"], 248))
        ix = zone.x + 28
        iy = zone.y + 25
        color = self._rgba(palette["espresso"])
        draw.rounded_rectangle((ix, iy, ix + 34, iy + 18), radius=4, outline=color, width=3)
        draw.rounded_rectangle((ix + 5, iy + 25, ix + 39, iy + 43), radius=4, outline=color, width=3)
        draw.line((ix + 17, iy + 18, ix + 17, iy + 25), fill=color, width=3)
        x = zone.x + icon_width + 24
        y = zone.y + (zone.height - fitted.height) // 2 - 1
        draw.multiline_text((x, y), "\n".join(fitted.lines), font=fitted.font, fill=color, spacing=0)
        return self._text_result(
            zone, (x, y, x + fitted.width, y + fitted.height), fitted,
            self.fonts.resolve("body"), 8.0, "opaque blush factual pill"
        )

    def _render_centered_benefit(
        self,
        draw: ImageDraw.ImageDraw,
        zone: SafeZone,
        text: str,
        palette: Dict[str, str],
    ) -> Dict[str, Any]:
        fitted = self._fit_text(text, "body", zone.width - 100, zone.height - 42, 42, 29, 3, 1.08)
        box = (zone.x, zone.y, zone.right, zone.bottom)
        draw.rounded_rectangle(box, radius=52, fill=self._rgba(palette["white"], 248))
        x = zone.x + (zone.width - fitted.width) // 2
        y = zone.y + (zone.height - fitted.height) // 2
        draw.multiline_text(
            (x, y), "\n".join(fitted.lines), font=fitted.font,
            fill=self._rgba(palette["espresso"]), spacing=max(0, fitted.line_height - fitted.font_size),
            align="center"
        )
        return self._text_result(
            zone, (x, y, x + fitted.width, y + fitted.height), fitted,
            self.fonts.resolve("body"), 11.0, "opaque white rounded benefit box"
        )

    def _render_benefit(self, draw: ImageDraw.ImageDraw, zone: SafeZone, text: str, palette: Dict[str, str]) -> Dict[str, Any]:
        inset = 32
        fitted = self._fit_text(text, "body", zone.width - inset * 2, zone.height - inset * 2, 39, 29, 4, 1.16)
        box = (zone.x, zone.y, zone.right, zone.bottom)
        draw.rounded_rectangle(box, radius=34, fill=self._rgba(palette["cream"], 236), outline=self._rgba(palette["blush_deep"], 225), width=3)
        draw.rounded_rectangle((zone.x + 18, zone.y + 26, zone.x + 27, zone.bottom - 26), radius=5, fill=self._rgba(palette["blush_deep"]))
        y = zone.y + (zone.height - fitted.height) // 2
        draw.multiline_text((zone.x + inset + 12, y), "\n".join(fitted.lines), font=fitted.font, fill=self._rgba(palette["espresso"]), spacing=max(0, fitted.line_height - fitted.font_size))
        text_box = (zone.x + inset + 12, y, zone.x + inset + 12 + fitted.width, y + fitted.height)
        return self._text_result(zone, text_box, fitted, self.fonts.resolve("body"), 10.0, "opaque cream benefit box")

    def _render_cta(self, draw: ImageDraw.ImageDraw, zone: SafeZone, text: str, palette: Dict[str, str]) -> Dict[str, Any]:
        fitted = self._fit_text(text, "ui", zone.width - 52, zone.height - 28, 34, 25, 2, 1.05)
        box = (zone.x, zone.y, zone.right, zone.bottom)
        draw.rounded_rectangle(box, radius=zone.height // 2, fill=self._rgba(palette["espresso"], 245))
        x = zone.x + (zone.width - fitted.width) // 2
        y = zone.y + (zone.height - fitted.height) // 2 - 2
        draw.multiline_text((x, y), "\n".join(fitted.lines), font=fitted.font, fill=self._rgba(palette["white"]), spacing=0)
        return self._text_result(zone, (x, y, x + fitted.width, y + fitted.height), fitted, self.fonts.resolve("ui"), 11.0, "espresso CTA pill")

    def _render_annotation(self, draw: ImageDraw.ImageDraw, zone: SafeZone, text: str, palette: Dict[str, str]) -> Dict[str, Any]:
        fitted = self._fit_text(text, "annotation", zone.width - 70, zone.height, 37, 27, 2, 1.0)
        x, y = zone.x, zone.y
        draw.multiline_text((x, y), "\n".join(fitted.lines), font=fitted.font, fill=self._rgba(palette["muted_rose"]), spacing=0, stroke_width=1, stroke_fill=self._rgba(palette["cream"], 180))
        return self._text_result(zone, (x, y, x + fitted.width, y + fitted.height), fitted, self.fonts.resolve("annotation"), 4.8, "handwritten with light stroke")

    def _fit_text(
        self,
        text: str,
        role: str,
        max_width: int,
        max_height: int,
        max_size: int,
        min_size: int,
        max_lines: int,
        line_height_factor: float,
    ) -> FittedText:
        if not text.strip():
            raise TextLayoutError("TEXT_LAYOUT_FAIL: empty text")
        font_path = self.fonts.resolve(role)
        measure = ImageDraw.Draw(Image.new("RGB", (4, 4)))
        for size in range(max_size, min_size - 1, -2):
            font = ImageFont.truetype(str(font_path), size=size)
            try:
                lines = self._wrap_words(measure, text, font, max_width)
            except TextLayoutError:
                # A token may be too wide at the current size and still fit at
                # a smaller allowed size, so keep the auto-fit search going.
                continue
            if len(lines) > max_lines:
                continue
            line_height = max(size, int(size * line_height_factor))
            widths = [self._text_width(measure, line, font) for line in lines]
            height = line_height * len(lines)
            if max(widths, default=0) <= max_width and height <= max_height:
                return FittedText(text, lines, font, size, line_height, max(widths, default=0), height)
        raise TextLayoutError(
            f"TEXT_LAYOUT_FAIL: copy does not fit {max_width}x{max_height} above minimum {min_size}px"
        )

    def _wrap_words(self, draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        lines: List[str] = []
        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()
            current = ""
            for word in words:
                candidate = f"{current} {word}".strip()
                if self._text_width(draw, candidate, font) <= max_width:
                    current = candidate
                else:
                    if not current or self._text_width(draw, word, font) > max_width:
                        raise TextLayoutError(f"TEXT_LAYOUT_FAIL: unbreakable token '{word}'")
                    lines.append(current)
                    current = word
            if current:
                lines.append(current)
        return lines

    @staticmethod
    def _text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
        box = draw.textbbox((0, 0), text, font=font)
        return box[2] - box[0]

    def _choose_text_color(self, base: Image.Image, zone: SafeZone, palette: Dict[str, str]) -> Tuple[Tuple[int, int, int, int], float, str]:
        crop = base.crop((zone.x, zone.y, zone.right, zone.bottom)).convert("RGB").resize((24, 24))
        mean = ImageStat.Stat(crop).mean
        bg = tuple(int(value) for value in mean)
        dark = self._hex_rgb(palette["espresso"])
        light = self._hex_rgb(palette["white"])
        dark_ratio = self._contrast_ratio(dark, bg)
        light_ratio = self._contrast_ratio(light, bg)
        if dark_ratio >= light_ratio:
            return (*dark, 255), dark_ratio, "adaptive dark text"
        return (*light, 255), light_ratio, "adaptive light text"

    def _draw_soft_backdrop(self, draw: ImageDraw.ImageDraw, zone: SafeZone, palette: Dict[str, str]) -> None:
        draw.rounded_rectangle(
            (zone.x - 24, zone.y - 20, zone.right + 18, zone.bottom + 16),
            radius=36,
            fill=self._rgba(palette["cream"], 205),
        )

    @staticmethod
    def _draw_sparkle(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int, color: Tuple[int, int, int, int]) -> None:
        points = [(cx, cy - radius), (cx + 5, cy - 5), (cx + radius, cy), (cx + 5, cy + 5), (cx, cy + radius), (cx - 5, cy + 5), (cx - radius, cy), (cx - 5, cy - 5)]
        draw.polygon(points, fill=color)

    @staticmethod
    def _draw_heart(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: Tuple[int, int, int, int]) -> None:
        r = size // 3
        draw.ellipse((x, y, x + 2 * r, y + 2 * r), fill=color)
        draw.ellipse((x + r, y, x + 3 * r, y + 2 * r), fill=color)
        draw.polygon([(x, y + r), (x + 3 * r, y + r), (x + 3 * r // 2, y + 3 * r)], fill=color)

    @staticmethod
    def _draw_outline_heart(
        draw: ImageDraw.ImageDraw,
        zone: SafeZone,
        color: Tuple[int, int, int, int],
        width: int,
    ) -> None:
        font = ImageFont.truetype("C:/Windows/Fonts/seguisym.ttf", size=min(zone.width, zone.height) - 12)
        glyph = "♡"
        bounds = draw.textbbox((0, 0), glyph, font=font, stroke_width=max(1, width // 4))
        glyph_width = bounds[2] - bounds[0]
        glyph_height = bounds[3] - bounds[1]
        x = zone.x + (zone.width - glyph_width) // 2
        y = zone.y + (zone.height - glyph_height) // 2 - bounds[1]
        draw.text(
            (x, y), glyph, font=font, fill=color,
            stroke_width=max(1, width // 4), stroke_fill=color,
        )

    @staticmethod
    def _draw_arrow(draw: ImageDraw.ImageDraw, zone: SafeZone, color: Tuple[int, int, int, int]) -> None:
        start = (zone.x + zone.width - 55, zone.y + 55)
        end = (zone.right + 55, zone.bottom + 150)
        draw.line((start, end), fill=color, width=5)
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        for offset in (2.55, -2.55):
            point = (end[0] + int(24 * math.cos(angle + offset)), end[1] + int(24 * math.sin(angle + offset)))
            draw.line((end, point), fill=color, width=5)

    @staticmethod
    def _shape_result(zone: SafeZone, description: str) -> Dict[str, Any]:
        return {
            "rendered_bbox": [zone.x, zone.y, zone.right, zone.bottom],
            "description": description,
            "overflow": False,
            "contrast_ratio": None,
        }

    @staticmethod
    def _text_result(zone: SafeZone, box: Sequence[int], fitted: FittedText, font_path: Path, ratio: float, strategy: str) -> Dict[str, Any]:
        overflow = box[0] < zone.x or box[1] < zone.y or box[2] > zone.right or box[3] > zone.bottom
        return {
            "rendered_bbox": list(box),
            "overflow": overflow,
            "font_path": str(font_path),
            "font_size": fitted.font_size,
            "line_height": fitted.line_height,
            "lines": fitted.lines,
            "contrast_ratio": round(ratio, 2),
            "contrast_strategy": strategy,
        }

    @staticmethod
    def _rgba(hex_color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
        return (*StoryTypographyRenderer._hex_rgb(hex_color), alpha)

    @staticmethod
    def _hex_rgb(hex_color: str) -> Tuple[int, int, int]:
        value = hex_color.lstrip("#")
        return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))  # type: ignore[return-value]

    @staticmethod
    def _relative_luminance(color: Tuple[int, int, int]) -> float:
        channels = []
        for channel in color:
            value = channel / 255.0
            channels.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    @classmethod
    def _contrast_ratio(cls, first: Tuple[int, int, int], second: Tuple[int, int, int]) -> float:
        a, b = cls._relative_luminance(first), cls._relative_luminance(second)
        lighter, darker = max(a, b), min(a, b)
        return (lighter + 0.05) / (darker + 0.05)
