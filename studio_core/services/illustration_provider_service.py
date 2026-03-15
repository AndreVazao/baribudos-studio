from __future__ import annotations

from typing import Dict, Any
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageDraw

from studio_core.core.config import resolve_storage_path


DEFAULT_PROVIDER = "local_basic"


def generate_placeholder_image(prompt: str, output_path: Path):
    width = 1024
    height = 1024

    img = Image.new("RGB", (width, height), (245, 238, 214))
    draw = ImageDraw.Draw(img)

    text = "Placeholder Illustration"
    draw.text((100, 500), text, fill=(47, 94, 46))

    img.save(output_path)


def generate_local_basic(prompt: str) -> str:
    file_name = f"illustration_{uuid4()}.png"
    output_dir = resolve_storage_path("illustrations")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / file_name
    generate_placeholder_image(prompt, output_path)

    return str(output_path)


def generate_stable_diffusion(prompt: str) -> str:
    # FUTURO: integração com ComfyUI / Automatic1111
    return generate_local_basic(prompt)


def generate_cloud_openai(prompt: str) -> str:
    # FUTURO: integração real
    return generate_local_basic(prompt)


def generate_illustration(
    prompt: str,
    provider: str | None = None,
    saga_style: Dict[str, Any] | None = None
) -> Dict[str, Any]:

    provider = provider or DEFAULT_PROVIDER

    if provider == "stable_diffusion":
        path = generate_stable_diffusion(prompt)

    elif provider == "openai":
        path = generate_cloud_openai(prompt)

    else:
        path = generate_local_basic(prompt)

    return {
        "id": str(uuid4()),
        "provider": provider,
        "prompt": prompt,
        "file_path": path
  }
