from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

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
        row = _safe_dict(project)
        if _safe_text(row.get("id")) == _safe_text(project_id):
            return row
    return None


def _editorial_pages(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    editorial = _safe_dict(project.get("editorial_engine", {}))
    return [_safe_dict(item) for item in _safe_list(editorial.get("pages", []))]


def build_story_from_editorial(project_id: str, language: str = "") -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    pages = _editorial_pages(project)
    if not pages:
        raise ValueError("Sem páginas editoriais.")

    target_language = _safe_text(language or project.get("language", "pt-PT")) or "pt-PT"

    story_pages = []
    for page in pages:
        story_pages.append({
            "id": _safe_text(page.get("id")) or str(uuid4()),
            "pageNumber": int(page.get("page_number", 0) or 0),
            "title": f"Página {int(page.get('page_number', 0) or 0)}",
            "text": _safe_text(page.get("text")),
            "illustration_requested": bool(_safe_dict(page.get("editorial_flags", {})).get("needs_illustration", False)),
            "scene_requested": True,
            "has_illustration": False,
            "illustration_path": "",
        })

    raw_text = "\n\n".join(_safe_text(page.get("text")) for page in pages if _safe_text(page.get("text"))).strip()

    story_payload = {
        "language": target_language,
        "title": _safe_text(project.get("title")),
        "pages": story_pages,
        "raw_text": raw_text,
        "status": "editorial_applied",
        "updated_at": now_iso(),
    }

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "story": story_payload if target_language == _safe_text(current.get("language", "pt-PT")) else current.get("story", {}),
            "language_variants": {
                **_safe_dict(current.get("language_variants", {})),
                target_language: {
                    **_safe_dict(_safe_dict(current.get("language_variants", {})).get(target_language, {})),
                    **story_payload,
                },
            },
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "story": story_payload,
        "project": updated,
    }


def build_illustration_queue_from_editorial(project_id: str) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    pages = _editorial_pages(project)
    if not pages:
        raise ValueError("Sem páginas editoriais.")

    frames = []
    for page in pages:
        flags = _safe_dict(page.get("editorial_flags", {}))
        brief = _safe_dict(page.get("illustration_brief", {}))
        if not bool(flags.get("needs_illustration", False)):
            continue

        frames.append({
            "id": str(uuid4()),
            "page_number": int(page.get("page_number", 0) or 0),
            "title": f"Ilustração página {int(page.get('page_number', 0) or 0)}",
            "prompt": _safe_text(brief.get("prompt_base")),
            "excerpt": _safe_text(brief.get("page_excerpt")),
            "approved": False,
            "image_path": "",
            "created_at": now_iso(),
        })

    pipeline = {
        "id": str(uuid4()),
        "source": "editorial_engine",
        "frames": frames,
        "frames_count": len(frames),
        "updated_at": now_iso(),
    }

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "illustration_pipeline": pipeline,
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "pipeline": pipeline,
        "project": updated,
    }


def build_storyboard_from_editorial(project_id: str) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    pages = _editorial_pages(project)
    if not pages:
        raise ValueError("Sem páginas editoriais.")

    shots = []
    for page in pages:
        page_number = int(page.get("page_number", 0) or 0)
        text = _safe_text(page.get("text"))
        brief = _safe_dict(page.get("illustration_brief", {}))

        shots.append({
            "id": str(uuid4()),
            "scene_number": page_number,
            "shot_title": f"Cena {page_number}",
            "narration": text,
            "visual_prompt": _safe_text(brief.get("prompt_base")),
            "visual_excerpt": _safe_text(brief.get("page_excerpt")),
            "duration_seconds": 6 if len(text) < 220 else 9,
            "transition": "fade",
            "audio_mode": "narration",
        })

    storyboard = {
        "id": str(uuid4()),
        "source": "editorial_engine",
        "title": f"{_safe_text(project.get('title'))} Storyboard",
        "shots": shots,
        "shots_count": len(shots),
        "updated_at": now_iso(),
    }

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "series_storyboard": storyboard,
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "storyboard": storyboard,
        "project": updated,
}
