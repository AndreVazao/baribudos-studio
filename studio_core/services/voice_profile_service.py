from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.config import resolve_storage_path
from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item

PROJECTS_FILE = "data/projects.json"

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _get_project(project_id: str) -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        if _safe_text(_safe_dict(project).get("id", "")) == _safe_text(project_id):
            return _safe_dict(project)
    return None


def _voice_dir(project_id: str) -> Path:
    path = resolve_storage_path("exports", project_id, "voices")
    path.mkdir(parents=True, exist_ok=True)
    return path


def _ext_for(filename: str) -> str:
    ext = Path(_safe_text(filename)).suffix.lower()
    return ext if ext in ALLOWED_EXTENSIONS else ".wav"


def attach_voice_sample(
    *,
    project_id: str,
    source_path: str,
    original_filename: str,
    profile_name: str = "",
    language: str = "",
    is_default: bool = True,
) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    src = Path(_safe_text(source_path)).expanduser().resolve()
    if not src.exists() or not src.is_file():
        raise ValueError("Ficheiro de voz não encontrado.")

    ext = _ext_for(original_filename)
    file_name = f"voice_{uuid4()}{ext}"
    target_path = _voice_dir(project_id) / file_name
    shutil.copy2(src, target_path)

    profile = {
        "id": str(uuid4()),
        "name": _safe_text(profile_name) or "Voice Sample",
        "language": _safe_text(language),
        "file_name": file_name,
        "file_path": str(target_path),
        "is_default": bool(is_default),
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }

    def updater(current: Dict[str, Any]) -> Dict[str, Any]:
        voices = _safe_dict(current.get("voices", {}))
        profiles = _safe_list(voices.get("profiles", []))

        if is_default:
            next_profiles = [{**_safe_dict(item), "is_default": False} for item in profiles]
        else:
            next_profiles = [_safe_dict(item) for item in profiles]

        next_profiles.append(profile)

        return {
            **current,
            "voices": {
                **voices,
                "profiles": next_profiles,
                "default_profile_id": profile["id"] if is_default else _safe_text(voices.get("default_profile_id", "")),
                "updated_at": now_iso(),
            },
            "updated_at": now_iso(),
        }

    updated_project = update_json_item(PROJECTS_FILE, project_id, updater)

    return {
        "ok": True,
        "profile": profile,
        "project": updated_project,
    }


def list_voice_profiles(project_id: str) -> List[Dict[str, Any]]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")
    voices = _safe_dict(project.get("voices", {}))
    profiles = _safe_list(voices.get("profiles", []))
    return [_safe_dict(item) for item in profiles if isinstance(item, dict)]


def set_default_voice_profile(project_id: str, profile_id: str) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    voices = _safe_dict(project.get("voices", {}))
    profiles = _safe_list(voices.get("profiles", []))
    if not profiles:
        raise ValueError("Projeto sem perfis de voz.")

    found = False
    next_profiles = []

    for item in profiles:
        profile = _safe_dict(item)
        is_match = _safe_text(profile.get("id", "")) == _safe_text(profile_id)
        if is_match:
            found = True
        next_profiles.append({
            **profile,
            "is_default": is_match,
            "updated_at": now_iso(),
        })

    if not found:
        raise ValueError("Perfil de voz não encontrado.")

    updated_project = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "voices": {
                **_safe_dict(current.get("voices", {})),
                "profiles": next_profiles,
                "default_profile_id": _safe_text(profile_id),
                "updated_at": now_iso(),
            },
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "project": updated_project,
        "voices": _safe_dict(updated_project.get("voices", {})),
    }


def get_default_voice_sample_path(project_id: str) -> str:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    voices = _safe_dict(project.get("voices", {}))
    default_profile_id = _safe_text(voices.get("default_profile_id", ""))
    profiles = _safe_list(voices.get("profiles", []))

    for item in profiles:
        profile = _safe_dict(item)
        if default_profile_id and _safe_text(profile.get("id", "")) == default_profile_id:
            return _safe_text(profile.get("file_path", ""))

    for item in profiles:
        profile = _safe_dict(item)
        if bool(profile.get("is_default", False)):
            return _safe_text(profile.get("file_path", ""))

    return ""
