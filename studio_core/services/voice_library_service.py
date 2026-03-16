from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.config import resolve_storage_path
from studio_core.core.models import now_iso
from studio_core.core.storage import append_json_item, read_json

VOICE_LIBRARY_FILE = "data/voice_library.json"
ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac"}


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _voice_root() -> Path:
    path = resolve_storage_path("voice_library")
    path.mkdir(parents=True, exist_ok=True)
    return path


def _normalize_ext(filename: str) -> str:
    ext = Path(_safe_text(filename)).suffix.lower()
    return ext if ext in ALLOWED_AUDIO_EXTENSIONS else ".wav"


def add_voice_sample(
    *,
    name: str,
    source_path: str,
    original_filename: str,
    language: str = "",
    notes: str = "",
) -> Dict[str, Any]:
    src = Path(_safe_text(source_path)).expanduser().resolve()
    if not src.exists() or not src.is_file():
        raise ValueError("Ficheiro de voz não encontrado.")

    voice_id = str(uuid4())
    ext = _normalize_ext(original_filename)
    target_dir = _voice_root() / voice_id
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / f"sample{ext}"
    shutil.copy2(src, target_path)

    item = {
        "id": voice_id,
        "name": _safe_text(name) or "Voice Sample",
        "language": _safe_text(language),
        "notes": _safe_text(notes),
        "file_name": target_path.name,
        "file_path": str(target_path),
        "created_at": now_iso(),
    }

    append_json_item(VOICE_LIBRARY_FILE, item)
    return item


def list_voice_samples() -> List[Dict[str, Any]]:
    items = read_json(VOICE_LIBRARY_FILE, [])
    return items if isinstance(items, list) else []


def get_voice_sample(voice_id: str) -> Dict[str, Any] | None:
    for item in list_voice_samples():
        voice = _safe_dict(item)
        if _safe_text(voice.get("id")) == _safe_text(voice_id):
            return voice
    return None
