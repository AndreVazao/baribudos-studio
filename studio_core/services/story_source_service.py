from __future__ import annotations

from typing import Any, Dict

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item

PROJECTS_FILE = "data/projects.json"
ALLOWED_SOURCE_TYPES = {"pasted_text", "imported_text", "external_chat_origin"}


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _get_project(project_id: str) -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    for item in projects:
        if _safe_text(item.get("id")) == _safe_text(project_id):
            return item
    return None


def get_story_source(project_id: str) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")
    return _safe_dict(project.get("story_source", {}))


def save_story_source(project_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    source_type = _safe_text(payload.get("story_source_type") or payload.get("source_type") or "pasted_text") or "pasted_text"
    if source_type not in ALLOWED_SOURCE_TYPES:
        raise ValueError("story_source_type_invalid")

    story_source = {
        "story_source_text": _safe_text(payload.get("story_source_text") or payload.get("text")),
        "story_source_language": _safe_text(payload.get("story_source_language") or payload.get("language") or project.get("language") or "pt-PT"),
        "story_source_type": source_type,
        "story_source_notes": _safe_text(payload.get("story_source_notes") or payload.get("notes")),
        "text_locked": bool(payload.get("text_locked", _safe_dict(project.get("story_source", {})).get("text_locked", False))),
        "text_approved": bool(payload.get("text_approved", _safe_dict(project.get("story_source", {})).get("text_approved", False))),
        "updated_at": now_iso(),
    }

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "story_source": story_source,
            "updated_at": now_iso(),
        },
    )
    return {"ok": True, "story_source": _safe_dict(updated.get("story_source", {})), "project": updated}


def lock_story_text(project_id: str, approved: bool = False) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    current = _safe_dict(project.get("story_source", {}))
    if not _safe_text(current.get("story_source_text")):
        raise ValueError("story_source_text_required")

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda item: {
            **item,
            "story_source": {
                **_safe_dict(item.get("story_source", {})),
                "text_locked": True,
                "text_approved": bool(approved),
                "updated_at": now_iso(),
            },
            "updated_at": now_iso(),
        },
    )
    return {"ok": True, "story_source": _safe_dict(updated.get("story_source", {})), "project": updated}


def get_story_source_gate(project_id: str) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    story_source = _safe_dict(project.get("story_source", {}))
    has_text = bool(_safe_text(story_source.get("story_source_text")))
    text_locked = bool(story_source.get("text_locked", False))
    text_approved = bool(story_source.get("text_approved", False))

    return {
        "ok": True,
        "project_id": project_id,
        "story_source_gate": {
            "has_text": has_text,
            "text_locked": text_locked,
            "text_approved": text_approved,
            "ready_for_text_first_pipeline": bool(has_text and text_locked),
            "label": "Text-first pronto" if (has_text and text_locked) else "Texto ainda não bloqueado",
        },
    }
