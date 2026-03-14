from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont

from studio_core.core.config import resolve_storage_path
from studio_core.services.age_badge_service import generate_age_badge
from studio_core.services.ip_runtime_service import load_ip_runtime


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = str(value).strip().lstrip("#")
    if len(value) != 6:
        return (47, 94, 46)
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def _safe_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value or "")).strip("_") or "cover"


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/verdanab.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size)
            except Exception:
                pass
    return ImageFont.load_default()


def _fit_font(text: str, max_width: int, start_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    size = start_size
    while size >= 18:
        font = _get_font(size)
        bbox = font.getbbox(text)
        if (bbox[2] - bbox[0]) <= max_width:
            return font
        size -= 2
    return _get_font(18)


def _paste_scaled(base: Image.Image, overlay_path: str | None, box: tuple[int, int, int, int]) -> None:
    if not overlay_path:
        return
    path = Path(overlay_path)
    if not path.exists():
        return

    overlay = Image.open(path).convert("RGBA")
    max_w = box[2] - box[0]
    max_h = box[3] - box[1]

    ratio = min(max_w / overlay.width, max_h / overlay.height)
    new_size = (max(1, int(overlay.width * ratio)), max(1, int(overlay.height * ratio)))
    overlay = overlay.resize(new_size, Image.LANCZOS)

    x = box[0] + (max_w - overlay.width) // 2
    y = box[1] + (max_h - overlay.height) // 2
    base.alpha_composite(overlay, (x, y))


def _draw_title(draw: ImageDraw.ImageDraw, title: str, width: int, gold: tuple[int, int, int]) -> None:
    font = _fit_font(title, max_width=width - 180, start_size=88)
    bbox = font.getbbox(title)
    text_w = bbox[2] - bbox[0]
    x = (width - text_w) // 2
    y = 1120
    draw.text((x + 3, y + 3), title, font=font, fill=(60, 40, 20, 160))
    draw.text((x, y), title, font=font, fill=gold)


def _draw_footer(draw: ImageDraw.ImageDraw, width: int, producer: str) -> None:
    font = _fit_font(producer, max_width=width - 120, start_size=34)
    bbox = font.getbbox(producer)
    text_w = bbox[2] - bbox[0]
    x = (width - text_w) // 2
    y = 1490
    draw.text((x, y), producer, font=font, fill=(245, 238, 214, 230))


def build_cover(
    *,
    saga_id: str,
    project_id: str,
    title: str,
    age_range: str,
    illustration_path: str,
    language: str = "pt-PT",
    producer: str | None = None,
    output_name: str | None = None,
) -> Dict[str, Any]:
    runtime = load_ip_runtime(saga_id)
    palette = runtime.get("palette", {}) or {}
    metadata = runtime.get("metadata", {}) or {}
    brand_assets = runtime.get("brand_assets", {}) or {}

    cream = _hex_to_rgb(palette.get("background", "#F5EED6"))
    gold = _hex_to_rgb(palette.get("accent", "#D4A73C"))
    producer_text = str(producer or metadata.get("producer") or "Produzido por Studio").strip()

    width, height = 1600, 1600
    cover = Image.new("RGBA", (width, height), cream + (255,))

    illustration = Image.open(illustration_path).convert("RGBA")
    illustration = illustration.resize((width, height), Image.LANCZOS)
    cover.alpha_composite(illustration, (0, 0))

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 36))
    cover = Image.alpha_composite(cover, overlay)

    badge = generate_age_badge(
        saga_id=saga_id,
        age_range=age_range,
        language=language,
        output_name=f"{_safe_name(saga_id)}_{_safe_name(age_range)}_{_safe_name(language)}.png"
    )

    _paste_scaled(cover, brand_assets.get("series_logo"), (220, 40, 1380, 250))
    _paste_scaled(cover, badge.get("file_path"), (40, 30, 360, 360))
    _paste_scaled(cover, brand_assets.get("seal_logo"), (40, 1260, 360, 1540))
    _paste_scaled(cover, brand_assets.get("studio_logo"), (1180, 1320, 1560, 1540))

    draw = ImageDraw.Draw(cover)
    _draw_title(draw, title, width, gold)
    _draw_footer(draw, width, producer_text)

    output_dir = resolve_storage_path("exports", project_id, "covers")
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = output_name or f"{_safe_name(title)}_cover.png"
    file_path = output_dir / file_name
    cover.save(file_path, format="PNG")

    return {
        "id": str(uuid4()),
        "saga_id": saga_id,
        "project_id": project_id,
        "title": title,
        "age_range": age_range,
        "language": language,
        "producer": producer_text,
        "file_name": file_name,
        "file_path": str(file_path),
        "badge_file_path": badge.get("file_path"),
        "engine": "python-cover-builder"
    }
