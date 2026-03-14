from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from studio_core.core.config import resolve_project_path, resolve_storage_path


def _load_age_badge_canon(saga_id: str) -> Dict[str, Any]:
    canon_path = resolve_project_path("studio", "sagas", saga_id, "age-badge-canon.json")
    if not canon_path.exists():
        raise FileNotFoundError(f"Age badge canon não encontrado para saga: {saga_id}")
    return json.loads(canon_path.read_text(encoding="utf-8"))


def _hex_to_rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = str(value).strip().lstrip("#")
    if len(value) != 6:
        return (47, 94, 46, alpha)
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


def _draw_pendant_shape(draw: ImageDraw.ImageDraw, width: int, height: int, fill: tuple[int, int, int, int], outline: tuple[int, int, int, int], outline_width: int) -> None:
    left = 36
    top = 54
    right = width - 36
    bottom = height - 68
    tip_x = width // 2
    tip_y = height - 26

    points = [
        (left + 24, top),
        (right - 24, top),
        (right, top + 22),
        (right, bottom - 18),
        (tip_x, tip_y),
        (left, bottom - 18),
        (left, top + 22),
    ]

    draw.rounded_rectangle((left, top, right, bottom - 12), radius=26, fill=fill, outline=outline, width=outline_width)
    draw.polygon(points, fill=fill, outline=outline)

    ring_outer = (width // 2 - 26, 8, width // 2 + 26, 60)
    ring_inner = (width // 2 - 13, 21, width // 2 + 13, 47)
    draw.ellipse(ring_outer, fill=outline)
    draw.ellipse(ring_inner, fill=(255, 255, 255, 0))


def _draw_glow(base: Image.Image, color: tuple[int, int, int, int]) -> Image.Image:
    glow = Image.new("RGBA", base.size, (255, 255, 255, 0))
    glow_draw = ImageDraw.Draw(glow)

    glow_draw.ellipse((70, 70, base.size[0] - 70, base.size[1] - 40), fill=(color[0], color[1], color[2], 70))
    glow = glow.filter(ImageFilter.GaussianBlur(26))
    return Image.alpha_composite(glow, base)


def _draw_leaf(draw: ImageDraw.ImageDraw, x: int, y: int, color: tuple[int, int, int, int], flip: bool = False) -> None:
    if flip:
        pts = [(x, y), (x - 12, y - 7), (x - 18, y + 4), (x - 4, y + 14)]
    else:
        pts = [(x, y), (x + 12, y - 7), (x + 18, y + 4), (x + 4, y + 14)]
    draw.polygon(pts, fill=color)


def _fit_font_for_box(text: str, max_width: int, start_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    size = start_size
    while size >= 18:
        font = _get_font(size)
        bbox = font.getbbox(text)
        if (bbox[2] - bbox[0]) <= max_width:
            return font
        size -= 2
    return _get_font(18)


def generate_age_badge(
    *,
    saga_id: str,
    age_range: str,
    output_name: str | None = None,
) -> Dict[str, Any]:
    canon = _load_age_badge_canon(saga_id)
    color_rules = canon.get("color_rules", {})

    width = 700
    height = 860

    primary = _hex_to_rgba(color_rules.get("primary", "#2F5E2E"))
    secondary = _hex_to_rgba(color_rules.get("secondary", "#6FA86A"))
    accent = _hex_to_rgba(color_rules.get("accent", "#D4A73C"))
    text_color = _hex_to_rgba(color_rules.get("text_color", "#F5EED6"))

    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    _draw_pendant_shape(draw, width, height, fill=secondary, outline=accent, outline_width=12)
    img = _draw_glow(img, accent)
    draw = ImageDraw.Draw(img)

    # inner border
    draw.line([(70, 96), (630, 96)], fill=accent, width=6)
    draw.line([(84, 110), (84, 710)], fill=accent, width=5)
    draw.line([(616, 110), (616, 710)], fill=accent, width=5)

    # text
    parts = str(age_range).strip().split()
    if len(parts) >= 2:
        line1 = parts[0]
        line2 = " ".join(parts[1:])
    else:
        line1 = str(age_range).strip()
        line2 = ""

    font1 = _fit_font_for_box(line1, max_width=440, start_size=120)
    font2 = _fit_font_for_box(line2 or "anos", max_width=360, start_size=90)

    bbox1 = font1.getbbox(line1)
    w1 = bbox1[2] - bbox1[0]
    h1 = bbox1[3] - bbox1[1]

    draw.text(((width - w1) / 2, 250), line1, font=font1, fill=text_color)

    if line2:
        bbox2 = font2.getbbox(line2)
        w2 = bbox2[2] - bbox2[0]
        draw.text(((width - w2) / 2, 400), line2, font=font2, fill=text_color)

    # leaf ornaments
    ornament_y = 545
    leaf_color = accent
    _draw_leaf(draw, 205, ornament_y, leaf_color, flip=False)
    _draw_leaf(draw, 170, ornament_y + 10, leaf_color, flip=False)
    _draw_leaf(draw, 490, ornament_y, leaf_color, flip=True)
    _draw_leaf(draw, 525, ornament_y + 10, leaf_color, flip=True)

    # small star
    star_points = [
        (350, 650), (362, 674), (388, 678), (368, 696), (373, 722),
        (350, 710), (327, 722), (332, 696), (312, 678), (338, 674)
    ]
    draw.polygon(star_points, fill=accent)

    output_dir = resolve_storage_path("exports", "age-badges", saga_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = output_name or f"{_safe_name(saga_id)}_{_safe_name(age_range)}.png"
    file_path = output_dir / file_name
    img.save(file_path, format="PNG")

    return {
        "id": str(uuid4()),
        "saga_id": saga_id,
        "age_range": age_range,
        "file_name": file_name,
        "file_path": str(file_path),
        "engine": "python-age-badge-generator"
  }
