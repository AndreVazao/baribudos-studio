from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from PIL import Image, ImageDraw

from studio_core.core.config import resolve_storage_path


DEFAULT_PROVIDER = "local_basic"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def generate_placeholder_image(prompt: str, output_path: Path) -> None:
    width = 1280
    height = 720

    img = Image.new("RGB", (width, height), (245, 238, 214))
    draw = ImageDraw.Draw(img)

    draw.rectangle((50, 50, width - 50, height - 50), outline=(47, 94, 46), width=8)
    draw.text((80, 90), "Placeholder Illustration", fill=(47, 94, 46))
    draw.text((80, 170), str(prompt or "")[:220], fill=(90, 90, 90))

    img.save(output_path)


def generate_local_basic(prompt: str, saga_style: Dict[str, Any] | None = None) -> str:
    file_name = f"illustration_{uuid4()}.png"
    output_dir = resolve_storage_path("illustrations", "generated")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / file_name
    generate_placeholder_image(prompt, output_path)
    return str(output_path)


def generate_stable_diffusion(prompt: str, saga_style: Dict[str, Any] | None = None) -> str:
    return generate_local_basic(prompt, saga_style=saga_style)


def generate_cloud_openai(prompt: str, saga_style: Dict[str, Any] | None = None) -> str:
    return generate_local_basic(prompt, saga_style=saga_style)


def generate_illustration(
    prompt: str,
    provider: str | None = None,
    saga_style: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    provider = str(provider or DEFAULT_PROVIDER).strip() or DEFAULT_PROVIDER

    if provider == "stable_diffusion":
        path = generate_stable_diffusion(prompt, saga_style=saga_style)
    elif provider == "openai":
        path = generate_cloud_openai(prompt, saga_style=saga_style)
    else:
        path = generate_local_basic(prompt, saga_style=saga_style)

    return {
        "id": str(uuid4()),
        "provider": provider,
        "prompt": prompt,
        "file_path": path,
    }
