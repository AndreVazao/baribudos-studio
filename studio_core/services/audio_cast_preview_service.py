from __future__ import annotations

from typing import Any, Dict

from studio_core.core.storage import read_json
from studio_core.services.voice_preview_service import generate_voice_preview
from studio_core.services.voice_library_service import get_voice_sample

PROJECTS_FILE = "data/projects.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _get_project(project_id: str) -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    if not isinstance(projects, list):
        return None

    for project in projects:
        row = _safe_dict(project)
        if _safe_text(row.get("id")) == _safe_text(project_id):
            return row
    return None


def _resolve_character_voice_id(audio_cast: Dict[str, Any], character_name: str) -> str:
    character_name = _safe_text(character_name)
    if not character_name:
        return ""

    if character_name.lower() in {"narrador", "narrator"}:
        narrator = _safe_dict(audio_cast.get("narrator", {}))
        return _safe_text(narrator.get("voice_sample_id"))

    for item in audio_cast.get("characters", []) or []:
        row = _safe_dict(item)
        if _safe_text(row.get("name")).lower() == character_name.lower():
            return _safe_text(row.get("voice_sample_id"))

    narrator = _safe_dict(audio_cast.get("narrator", {}))
    return _safe_text(narrator.get("voice_sample_id"))


def generate_audio_cast_preview(project_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    audio_cast = _safe_dict(project.get("audio_cast", {}))
    character_name = _safe_text(payload.get("character_name", "Narrador")) or "Narrador"
    provider = _safe_text(payload.get("provider", "xtts")) or "xtts"
    language = _safe_text(payload.get("language", project.get("language", "pt-PT"))) or "pt-PT"
    text = _safe_text(payload.get("text", f"Olá. Este é um teste de voz da personagem {character_name}."))

    voice_sample_id = _resolve_character_voice_id(audio_cast, character_name)
    voice_sample = get_voice_sample(voice_sample_id) if voice_sample_id else None

    result = generate_voice_preview({
        "provider": provider,
        "text": text,
        "language": language,
        "voice_sample_id": voice_sample_id,
    })

    return {
        "ok": True,
        "project_id": project_id,
        "character_name": character_name,
        "voice_sample": voice_sample,
        "preview": result.get("preview", {}),
                      }
