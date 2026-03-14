from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from studio_core.core.config import resolve_storage_path
from studio_core.services.ip_runtime_service import load_ip_runtime


LANGUAGE_LABELS = {
    "pt": "anos",
    "pt-PT": "anos",
    "pt-BR": "anos",
    "en": "years",
    "es": "años",
    "fr": "ans",
    "de": "Jahre",
    "it": "anni",
    "nl": "jaar",
    "zh": "岁",
    "ja": "歳"
}


def _hex_to_rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = str(value).strip().lstrip("#")
    if len(value) != 6:
        return (139, 94, 60, alpha)
    r = int(value[0:2], 16)
    g = int(value[2:4], 16)
    b = int(value[4:6], 16)
    return (r, g, b, alpha)


def _safe_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value or "")).strip("_") or "badge"


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/verdanab.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for font_path in candidates:
        if Path(font_path).exists():
            try:
                return ImageFont.truetype(font_path, size=size)
            except Exception:
                pass
    return ImageFont.load_default()


def _fit_font_for_box(text: str, max_width: int, start_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    size = start_size
    while size >= 18:
        font = _get_font(size)
        bbox = font.getbbox(text)
        if (bbox[2] - bbox[0]) <= max_width:
            return font
        size -= 2
    return _get_font(18)


def _draw_outer_glow(base: Image.Image, color: tuple[int, int, int, int]) -> Image.Image:
    glow = Image.new("RGBA", base.size, (255, 255, 255, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((40, 40, base.size[0] - 40, base.size[1] - 40), fill=(color[0], color[1], color[2], 70))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    return Image.alpha_composite(glow, base)


def _draw_wood_badge(draw: ImageDraw.ImageDraw, width: int, height: int, wood_dark: tuple[int, int, int, int], wood_light: tuple[int, int, int, int], gold: tuple[int, int, int, int]) -> None:
    cx = width // 2
    cy = height // 2 + 20
    radius = 250

    draw.ellipse((cx - radius - 20, cy - radius - 20, cx + radius + 20, cy + radius + 20), fill=gold)
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=wood_light)
    draw.ellipse((cx - radius + 38, cy - radius + 38, cx + radius - 38, cy + radius - 38), outline=gold, width=10)
    draw.ellipse((cx - radius + 58, cy - radius + 58, cx + radius - 58, cy + radius - 58), fill=wood_dark)

    draw.ellipse((cx - 52, 24, cx + 52, 128), fill=gold)
    draw.ellipse((cx - 24, 52, cx + 24, 100), fill=(255, 255, 255, 0))


def _draw_leaf(draw: ImageDraw.ImageDraw, x: int, y: int, fill: tuple[int, int, int, int], rotate_left: bool = True) -> None:
    if rotate_left:
        pts = [(x, y), (x - 24, y - 10), (x - 34, y + 8), (x - 8, y + 24)]
    else:
        pts = [(x, y), (x + 24, y - 10), (x + 34, y + 8), (x + 8, y + 24)]
    draw.polygon(pts, fill=fill)


def _draw_star(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int, fill: tuple[int, int, int, int]) -> None:
    pts = [
        (cx, cy - size),
        (cx + int(size * 0.35), cy - int(size * 0.35)),
        (cx + size, cy - int(size * 0.2)),
        (cx + int(size * 0.45), cy + int(size * 0.15)),
        (cx + int(size * 0.6), cy + size),
        (cx, cy + int(size * 0.45)),
        (cx - int(size * 0.6), cy + size),
        (cx - int(size * 0.45), cy + int(size * 0.15)),
        (cx - size, cy - int(size * 0.2)),
        (cx - int(size * 0.35), cy - int(size * 0.35)),
    ]
    draw.polygon(pts, fill=fill)


def _build_age_text(age_range: str, language: str) -> tuple[str, str]:
    return str(age_range).strip(), LANGUAGE_LABELS.get(language, LANGUAGE_LABELS["en"])


def generate_age_badge(
    *,
    saga_id: str,
    age_range: str,
    language: str = "pt-PT",
    output_name: str | None = None,
) -> Dict[str, Any]:
    runtime = load_ip_runtime(saga_id)
    palette = runtime.get("palette", {}) or {}
    colors = (runtime.get("canons", {}).get("age_badge", {}) or {}).get("color_rules", {}) or {}

    width = 720
    height = 720

    wood_dark = _hex_to_rgba(palette.get("character_base", "#8B5E3C"))
    wood_light = _hex_to_rgba("#B8834E")
    gold = _hex_to_rgba(colors.get("accent") or palette.get("accent", "#D4A73C"))
    text_color = _hex_to_rgba(colors.get("text_color", "#F5EED6"))
    leaf_green = _hex_to_rgba(colors.get("secondary") or palette.get("secondary", "#6FA86A"))

    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    _draw_wood_badge(draw, width, height, wood_dark, wood_light, gold)
    img = _draw_outer_glow(img, gold)
    draw = ImageDraw.Draw(img)

    line1, line2 = _build_age_text(age_range, language)

    font1 = _fit_font_for_box(line1, max_width=360, start_size=112)
    font2 = _fit_font_for_box(line2, max_width=280, start_size=70)

    bbox1 = font1.getbbox(line1)
    bbox2 = font2.getbbox(line2)

    w1 = bbox1[2] - bbox1[0]
    w2 = bbox2[2] - bbox2[0]

    draw.text(((width - w1) / 2, 250), line1, font=font1, fill=text_color)
    draw.text(((width - w2) / 2, 390), line2, font=font2, fill=text_color)

    _draw_leaf(draw, 215, 470, leaf_green, rotate_left=True)
    _draw_leaf(draw, 185, 505, leaf_green, rotate_left=True)
    _draw_leaf(draw, 505, 470, leaf_green, rotate_left=False)
    _draw_leaf(draw, 535, 505, leaf_green, rotate_left=False)

    _draw_star(draw, 360, 565, 26, gold)

    output_dir = resolve_storage_path("exports", "age-badges", saga_id, language)
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = output_name or f"{_safe_name(saga_id)}_{_safe_name(age_range)}_{_safe_name(language)}.png"
    file_path = output_dir / file_name
    img.save(file_path, format="PNG")

    return {
        "id": str(uuid4()),
        "saga_id": saga_id,
        "age_range": age_range,
        "language": language,
        "file_name": file_name,
        "file_path": str(file_path),
        "engine": "python-age-badge-generator-multilang"
}
