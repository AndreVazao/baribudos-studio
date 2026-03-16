from __future__ import annotations

from typing import Any, Dict, List

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item

PROJECTS_FILE = "data/projects.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _get_project(project_id: str) -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        if _safe_text(project.get("id")) == _safe_text(project_id):
            return project
    return None


def get_audio_cast(project_id: str) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")
    return _safe_dict(project.get("audio_cast", {}))


def save_audio_cast(project_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    narrator = _safe_dict(payload.get("narrator", {}))
    characters = _safe_list(payload.get("characters", []))

    normalized_characters = []
    seen = set()

    for item in characters:
        row = _safe_dict(item)
        name = _safe_text(row.get("name"))
        if not name:
            continue

        key = name.lower()
        if key in seen:
            continue
        seen.add(key)

        normalized_characters.append({
            "name": name,
            "voice_sample_id": _safe_text(row.get("voice_sample_id")),
            "provider": _safe_text(row.get("provider")),
            "notes": _safe_text(row.get("notes")),
        })

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "audio_cast": {
                "narrator": {
                    "voice_sample_id": _safe_text(narrator.get("voice_sample_id")),
                    "provider": _safe_text(narrator.get("provider")),
                    "notes": _safe_text(narrator.get("notes")),
                },
                "characters": normalized_characters,
                "updated_at": now_iso(),
            },
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "audio_cast": _safe_dict(updated.get("audio_cast", {})),
        "project": updated,
    }


def list_project_character_names(project_id: str) -> List[str]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    names = set()

    runtime_chars = _safe_list(project.get("main_characters", []))
    for item in runtime_chars:
        if isinstance(item, dict):
            name = _safe_text(item.get("name"))
        else:
            name = _safe_text(item)
        if name:
            names.add(name)

    story = _safe_dict(project.get("story", {}))
    for page in _safe_list(story.get("pages", [])):
        text = _safe_text(_safe_dict(page).get("text"))
        for line in text.splitlines():
            line = line.strip()
            if ":" in line:
                speaker = _safe_text(line.split(":", 1)[0])
                if 1 <= len(speaker) <= 40:
                    names.add(speaker)

    return sorted(names)
