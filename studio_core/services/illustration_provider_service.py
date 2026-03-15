from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from PIL import Image, ImageDraw

from studio_core.core.config import resolve_storage_path

DEFAULT_PROVIDER = "local_basic"
DEFAULT_COMFYUI_URL = os.getenv("BARIBUDOS_COMFYUI_URL", "http://127.0.0.1:8188").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _http_json(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as res:
        return json.loads(res.read().decode("utf-8"))


def _http_get_json(url: str) -> Dict[str, Any]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=180) as res:
        return json.loads(res.read().decode("utf-8"))


def _download_file(url: str, output_path: Path) -> None:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=300) as res:
        output_path.write_bytes(res.read())


def _generated_dir() -> Path:
    path = resolve_storage_path("illustrations", "generated")
    path.mkdir(parents=True, exist_ok=True)
    return path


def generate_placeholder_image(prompt: str, output_path: Path) -> None:
    width = 1280
    height = 720

    img = Image.new("RGB", (width, height), (245, 238, 214))
    draw = ImageDraw.Draw(img)

    draw.rectangle((40, 40, width - 40, height - 40), outline=(47, 94, 46), width=6)
    draw.text((80, 80), "Baribudos Studio Placeholder", fill=(47, 94, 46))
    draw.text((80, 160), _safe_text(prompt)[:240], fill=(80, 80, 80))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)


def generate_local_basic(prompt: str, saga_style: Dict[str, Any] | None = None) -> str:
    output_path = _generated_dir() / f"illustration_{uuid4()}.png"
    generate_placeholder_image(prompt, output_path)
    return str(output_path)


def _style_to_prompt_suffix(saga_style: Dict[str, Any] | None) -> str:
    style = _safe_dict(saga_style)
    bits = []

    palette = _safe_dict(style.get("palette", {}))
    if palette:
        bits.append(
            "palette "
            f"primary {palette.get('primary', '')}, "
            f"secondary {palette.get('secondary', '')}, "
            f"accent {palette.get('accent', '')}, "
            f"background {palette.get('background', '')}, "
            f"character_base {palette.get('character_base', '')}"
        )

    visual = _safe_dict(style.get("visual", {}))
    if visual:
        for key in ["style", "environment", "lighting", "tone"]:
            text = _safe_text(visual.get(key))
            if text:
                bits.append(f"{key} {text}")

    character_rules = _safe_text(style.get("character_rules"))
    if character_rules:
        bits.append(character_rules)

    return ", ".join(bit for bit in bits if bit).strip()


def _build_comfyui_prompt(prompt: str, saga_style: Dict[str, Any] | None = None) -> str:
    suffix = _style_to_prompt_suffix(saga_style)
    final_prompt = _safe_text(prompt)
    if suffix:
        final_prompt = f"{final_prompt}, {suffix}"
    return final_prompt.strip()


def _comfyui_basic_workflow(prompt: str) -> Dict[str, Any]:
    return {
        "3": {
            "inputs": {
                "seed": int(time.time() * 1000) % 2147483647,
                "steps": 22,
                "cfg": 7,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
            "class_type": "KSampler",
        },
        "4": {
            "inputs": {
                "ckpt_name": "v1-5-pruned-emaonly.safetensors",
            },
            "class_type": "CheckpointLoaderSimple",
        },
        "5": {
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1,
            },
            "class_type": "EmptyLatentImage",
        },
        "6": {
            "inputs": {
                "text": prompt,
                "clip": ["4", 1],
            },
            "class_type": "CLIPTextEncode",
        },
        "7": {
            "inputs": {
                "text": "low quality, blurry, distorted, deformed, extra limbs, bad anatomy, text, watermark",
                "clip": ["4", 1],
            },
            "class_type": "CLIPTextEncode",
        },
        "8": {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2],
            },
            "class_type": "VAEDecode",
        },
        "9": {
            "inputs": {
                "filename_prefix": "baribudos_studio",
                "images": ["8", 0],
            },
            "class_type": "SaveImage",
        },
    }


def _comfyui_history_image_url(base_url: str, history: Dict[str, Any], prompt_id: str) -> str:
    prompt_data = _safe_dict(history.get(prompt_id, {}))
    outputs = _safe_dict(prompt_data.get("outputs", {}))

    for _, node_output in outputs.items():
        node_dict = _safe_dict(node_output)
        images = node_dict.get("images", [])
        if isinstance(images, list) and images:
            img = _safe_dict(images[0])
            filename = _safe_text(img.get("filename"))
            subfolder = _safe_text(img.get("subfolder"))
            img_type = _safe_text(img.get("type", "output")) or "output"
            if filename:
                query = urllib.parse.urlencode({
                    "filename": filename,
                    "subfolder": subfolder,
                    "type": img_type,
                })
                return f"{base_url}/view?{query}"

    return ""


def generate_comfyui(prompt: str, saga_style: Dict[str, Any] | None = None, base_url: str = DEFAULT_COMFYUI_URL) -> str:
    final_prompt = _build_comfyui_prompt(prompt, saga_style=saga_style)
    workflow = _comfyui_basic_workflow(final_prompt)

    response = _http_json(f"{base_url}/prompt", {"prompt": workflow})
    prompt_id = _safe_text(response.get("prompt_id"))
    if not prompt_id:
        raise RuntimeError("ComfyUI não devolveu prompt_id.")

    started = time.time()
    while time.time() - started < 600:
        time.sleep(2)
        history = _http_get_json(f"{base_url}/history/{prompt_id}")
        image_url = _comfyui_history_image_url(base_url, history, prompt_id)
        if image_url:
            output_path = _generated_dir() / f"illustration_{uuid4()}.png"
            _download_file(image_url, output_path)
            return str(output_path)

    raise RuntimeError("Timeout à espera da geração ComfyUI.")


def generate_stable_diffusion(prompt: str, saga_style: Dict[str, Any] | None = None) -> str:
    return generate_comfyui(prompt, saga_style=saga_style)


def generate_cloud_openai(prompt: str, saga_style: Dict[str, Any] | None = None) -> str:
    return generate_local_basic(prompt, saga_style=saga_style)


def generate_illustration(
    prompt: str,
    provider: str | None = None,
    saga_style: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    provider = _safe_text(provider or DEFAULT_PROVIDER) or DEFAULT_PROVIDER

    try:
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
            "ok": True,
        }

    except Exception as exc:
        fallback_path = generate_local_basic(prompt, saga_style=saga_style)
        return {
            "id": str(uuid4()),
            "provider": provider,
            "prompt": prompt,
            "file_path": fallback_path,
            "ok": False,
            "fallback_used": True,
            "error": str(exc),
    }
