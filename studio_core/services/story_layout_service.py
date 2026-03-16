from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item
from studio_core.services.saga_runtime_service import load_saga_runtime

PROJECTS_FILE = "data/projects.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _normalize_text(value: str) -> str:
    return str(value or "").replace("\r\n", "\n").replace("\r", "\n").strip()


def _paragraphs(text: str) -> List[str]:
    raw = _normalize_text(text)
    if not raw:
        return []
    result = [block.strip() for block in raw.split("\n") if block.strip()]
    return result if result else [raw]


def _get_project(project_id: str) -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        if str(project.get("id", "")).strip() == str(project_id).strip():
            return project
    return None


def _resolve_layout_profile(runtime: Dict[str, Any]) -> Dict[str, Any]:
    metadata = _safe_dict(runtime.get("metadata", {}))
    canons = _safe_dict(runtime.get("canons", {}))
    narrative = _safe_dict(canons.get("narrative", {}))
    visual = _safe_dict(canons.get("visual", {}))

    genre = str(metadata.get("genre", "")).strip().lower()
    target_age = str(metadata.get("target_age", "")).strip()

    default_profile = {
        "profile": "general",
        "max_lines_per_page": 12,
        "max_words_per_line": 14,
        "max_paragraphs_per_page": 3,
        "illustration_recommended": False,
        "text_density": "medium",
    }

    if "infantil" in genre or target_age:
        return {
            "profile": "children",
            "max_lines_per_page": 5,
            "max_words_per_line": 10,
            "max_paragraphs_per_page": 2,
            "illustration_recommended": True,
            "text_density": "low",
        }

    if "poesia" in genre:
        return {
            "profile": "poetry",
            "max_lines_per_page": 20,
            "max_words_per_line": 8,
            "max_paragraphs_per_page": 6,
            "illustration_recommended": False,
            "text_density": "variable",
        }

    if "técnico" in genre or "technical" in genre:
        return {
            "profile": "technical",
            "max_lines_per_page": 18,
            "max_words_per_line": 16,
            "max_paragraphs_per_page": 6,
            "illustration_recommended": False,
            "text_density": "high",
        }

    if "romance" in genre or "adulto" in genre:
        return {
            "profile": "adult",
            "max_lines_per_page": 16,
            "max_words_per_line": 14,
            "max_paragraphs_per_page": 4,
            "illustration_recommended": False,
            "text_density": "medium_high",
        }

    page_structure = _safe_dict(visual.get("page_structure", {}))
    if page_structure:
        return {
            "profile": str(page_structure.get("profile", "custom")).strip() or "custom",
            "max_lines_per_page": int(page_structure.get("max_lines_per_page", 12) or 12),
            "max_words_per_line": int(page_structure.get("max_words_per_line", 14) or 14),
            "max_paragraphs_per_page": int(page_structure.get("max_paragraphs_per_page", 3) or 3),
            "illustration_recommended": bool(page_structure.get("illustration_recommended", False)),
            "text_density": str(page_structure.get("text_density", "medium")).strip() or "medium",
        }

    narrative_page_rules = _safe_dict(narrative.get("page_rules", {}))
    if narrative_page_rules:
        return {
            "profile": str(narrative_page_rules.get("profile", "custom")).strip() or "custom",
            "max_lines_per_page": int(narrative_page_rules.get("max_lines_per_page", 12) or 12),
            "max_words_per_line": int(narrative_page_rules.get("max_words_per_line", 14) or 14),
            "max_paragraphs_per_page": int(narrative_page_rules.get("max_paragraphs_per_page", 3) or 3),
            "illustration_recommended": bool(narrative_page_rules.get("illustration_recommended", False)),
            "text_density": str(narrative_page_rules.get("text_density", "medium")).strip() or "medium",
        }

    return default_profile


def _chunk_paragraphs(paragraphs: List[str], max_paragraphs_per_page: int) -> List[List[str]]:
    if not paragraphs:
        return []
    max_paragraphs_per_page = max(1, int(max_paragraphs_per_page or 1))

    pages: List[List[str]] = []
    current: List[str] = []

    for paragraph in paragraphs:
        current.append(paragraph)
        if len(current) >= max_paragraphs_per_page:
            pages.append(current)
            current = []

    if current:
        pages.append(current)

    return pages


def _renumber_pages(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result = []
    for index, item in enumerate(pages, start=1):
        page = _safe_dict(item)
        result.append({
            **page,
            "pageNumber": index,
            "updated_at": now_iso(),
        })
    return result


def auto_paginate_story(project_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    runtime = load_saga_runtime(str(project.get("saga_slug", "baribudos")).strip() or "baribudos")
    layout_profile = _resolve_layout_profile(runtime)

    language = str(payload.get("language", project.get("language", runtime.get("default_language", "pt-PT")))).strip() or "pt-PT"
    story_variants = _safe_dict(project.get("language_variants", {}))
    story = _safe_dict(story_variants.get(language, {}))
    if not story:
        story = _safe_dict(project.get("story", {}))

    raw_text = _normalize_text(payload.get("raw_text", "") or story.get("raw_text", ""))
    if not raw_text:
        raise ValueError("Sem texto para paginar.")

    paragraphs = _paragraphs(raw_text)
    grouped = _chunk_paragraphs(paragraphs, layout_profile.get("max_paragraphs_per_page", 3))

    pages = []
    for index, chunk in enumerate(grouped, start=1):
        pages.append({
            "id": str(uuid4()),
            "pageNumber": index,
            "title": f"Página {index}",
            "text": "\n\n".join(chunk).strip(),
            "layout_mode": "auto",
            "illustration_requested": bool(layout_profile.get("illustration_recommended", False)),
            "scene_requested": False,
            "has_illustration": False,
            "illustration_path": "",
        })

    layout = {
        "id": str(uuid4()),
        "language": language,
        "profile": layout_profile,
        "raw_text": raw_text,
        "pages": pages,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }

    updated_project = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "story_layout": layout,
            "updated_at": now_iso(),
        }
    )

    return {
        "ok": True,
        "layout": layout,
        "project": updated_project,
    }


def get_story_layout(project_id: str) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")
    return _safe_dict(project.get("story_layout", {}))


def update_story_layout_page(project_id: str, page_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    layout = _safe_dict(project.get("story_layout", {}))
    pages = _safe_list(layout.get("pages", []))
    if not pages:
        raise ValueError("Projeto sem story layout.")

    updated = False
    next_pages = []

    for item in pages:
        page = _safe_dict(item)
        if str(page.get("id", "")).strip() != str(page_id).strip():
            next_pages.append(page)
            continue

        next_pages.append({
            **page,
            "title": str(payload.get("title", page.get("title", ""))).strip() or page.get("title", ""),
            "text": _normalize_text(payload.get("text", page.get("text", ""))),
            "layout_mode": str(payload.get("layout_mode", page.get("layout_mode", "manual"))).strip() or "manual",
            "illustration_requested": bool(payload.get("illustration_requested", page.get("illustration_requested", False))),
            "scene_requested": bool(payload.get("scene_requested", page.get("scene_requested", False))),
            "updated_at": now_iso(),
        })
        updated = True

    if not updated:
        raise ValueError("Página não encontrada.")

    updated_project = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "story_layout": {
                **_safe_dict(current.get("story_layout", {})),
                "pages": next_pages,
                "updated_at": now_iso(),
            },
            "updated_at": now_iso(),
        }
    )

    return {
        "ok": True,
        "layout": _safe_dict(updated_project.get("story_layout", {})),
        "project": updated_project,
    }


def add_story_layout_page(project_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    layout = _safe_dict(project.get("story_layout", {}))
    pages = _safe_list(layout.get("pages", []))
    next_number = len(pages) + 1

    new_page = {
        "id": str(uuid4()),
        "pageNumber": next_number,
        "title": str(payload.get("title", f"Página {next_number}")).strip() or f"Página {next_number}",
        "text": _normalize_text(payload.get("text", "")),
        "layout_mode": "manual",
        "illustration_requested": bool(payload.get("illustration_requested", False)),
        "scene_requested": bool(payload.get("scene_requested", False)),
        "has_illustration": False,
        "illustration_path": "",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }

    updated_project = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "story_layout": {
                **_safe_dict(current.get("story_layout", {})),
                "pages": [*_safe_list(_safe_dict(current.get("story_layout", {})).get("pages", [])), new_page],
                "updated_at": now_iso(),
            },
            "updated_at": now_iso(),
        }
    )

    return {
        "ok": True,
        "layout": _safe_dict(updated_project.get("story_layout", {})),
        "project": updated_project,
    }


def remove_story_layout_page(project_id: str, page_id: str) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    layout = _safe_dict(project.get("story_layout", {}))
    pages = _safe_list(layout.get("pages", []))
    if not pages:
        raise ValueError("Projeto sem story layout.")

    filtered = [page for page in pages if str(_safe_dict(page).get("id", "")).strip() != str(page_id).strip()]
    if len(filtered) == len(pages):
        raise ValueError("Página não encontrada.")

    renumbered = _renumber_pages([_safe_dict(item) for item in filtered])

    updated_project = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "story_layout": {
                **_safe_dict(current.get("story_layout", {})),
                "pages": renumbered,
                "updated_at": now_iso(),
            },
            "updated_at": now_iso(),
        }
    )

    return {
        "ok": True,
        "layout": _safe_dict(updated_project.get("story_layout", {})),
        "project": updated_project,
    }


def move_story_layout_page(project_id: str, page_id: str, direction: str) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    layout = _safe_dict(project.get("story_layout", {}))
    pages = [_safe_dict(item) for item in _safe_list(layout.get("pages", []))]
    if not pages:
        raise ValueError("Projeto sem story layout.")

    index = next((i for i, page in enumerate(pages) if str(page.get("id", "")).strip() == str(page_id).strip()), -1)
    if index < 0:
        raise ValueError("Página não encontrada.")

    target = index - 1 if direction == "up" else index + 1 if direction == "down" else -1
    if target < 0 or target >= len(pages):
        return {
            "ok": True,
            "layout": layout,
            "project": project,
        }

    pages[index], pages[target] = pages[target], pages[index]
    pages = _renumber_pages(pages)

    updated_project = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "story_layout": {
                **_safe_dict(current.get("story_layout", {})),
                "pages": pages,
                "updated_at": now_iso(),
            },
            "updated_at": now_iso(),
        }
    )

    return {
        "ok": True,
        "layout": _safe_dict(updated_project.get("story_layout", {})),
        "project": updated_project,
    }


def split_story_layout_page(project_id: str, page_id: str, split_mode: str = "half") -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    layout = _safe_dict(project.get("story_layout", {}))
    pages = [_safe_dict(item) for item in _safe_list(layout.get("pages", []))]
    if not pages:
        raise ValueError("Projeto sem story layout.")

    index = next((i for i, page in enumerate(pages) if str(page.get("id", "")).strip() == str(page_id).strip()), -1)
    if index < 0:
        raise ValueError("Página não encontrada.")

    page = pages[index]
    paragraphs = _paragraphs(_safe_text(page.get("text", "")))
    if len(paragraphs) < 2:
        raise ValueError("A página precisa de pelo menos 2 blocos para dividir.")

    split_at = max(1, len(paragraphs) // 2) if split_mode == "half" else max(1, len(paragraphs) - 1)

    first_text = "\n\n".join(paragraphs[:split_at]).strip()
    second_text = "\n\n".join(paragraphs[split_at:]).strip()

    first_page = {
        **page,
        "text": first_text,
        "updated_at": now_iso(),
    }
    second_page = {
        "id": str(uuid4()),
        "pageNumber": page.get("pageNumber", index + 2),
        "title": f"{_safe_text(page.get('title', 'Página'))} (continuação)",
        "text": second_text,
        "layout_mode": "manual",
        "illustration_requested": bool(page.get("illustration_requested", False)),
        "scene_requested": bool(page.get("scene_requested", False)),
        "has_illustration": False,
        "illustration_path": "",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }

    pages[index:index + 1] = [first_page, second_page]
    pages = _renumber_pages(pages)

    updated_project = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "story_layout": {
                **_safe_dict(current.get("story_layout", {})),
                "pages": pages,
                "updated_at": now_iso(),
            },
            "updated_at": now_iso(),
        }
    )

    return {
        "ok": True,
        "layout": _safe_dict(updated_project.get("story_layout", {})),
        "project": updated_project,
    }


def move_text_between_pages(project_id: str, from_page_id: str, to_page_id: str, mode: str = "last_paragraph") -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    layout = _safe_dict(project.get("story_layout", {}))
    pages = [_safe_dict(item) for item in _safe_list(layout.get("pages", []))]
    if not pages:
        raise ValueError("Projeto sem story layout.")

    from_index = next((i for i, page in enumerate(pages) if str(page.get("id", "")).strip() == str(from_page_id).strip()), -1)
    to_index = next((i for i, page in enumerate(pages) if str(page.get("id", "")).strip() == str(to_page_id).strip()), -1)

    if from_index < 0 or to_index < 0:
        raise ValueError("Página de origem ou destino não encontrada.")
    if from_index == to_index:
        raise ValueError("Origem e destino não podem ser a mesma página.")

    from_page = pages[from_index]
    to_page = pages[to_index]

    from_parts = _paragraphs(_safe_text(from_page.get("text", "")))
    to_parts = _paragraphs(_safe_text(to_page.get("text", "")))

    if not from_parts:
        raise ValueError("Página de origem sem texto.")

    moved = from_parts.pop(-1) if mode == "last_paragraph" else from_parts.pop(0)

    if mode == "first_paragraph":
        to_parts.insert(0, moved)
    else:
        to_parts.append(moved)

    pages[from_index] = {
        **from_page,
        "text": "\n\n".join(from_parts).strip(),
        "updated_at": now_iso(),
    }
    pages[to_index] = {
        **to_page,
        "text": "\n\n".join(to_parts).strip(),
        "updated_at": now_iso(),
    }
    pages = _renumber_pages(pages)

    updated_project = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "story_layout": {
                **_safe_dict(current.get("story_layout", {})),
                "pages": pages,
                "updated_at": now_iso(),
            },
            "updated_at": now_iso(),
        }
    )

    return {
        "ok": True,
        "layout": _safe_dict(updated_project.get("story_layout", {})),
        "project": updated_project,
    }


def apply_story_layout_to_story(project_id: str, language: str = "") -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    layout = _safe_dict(project.get("story_layout", {}))
    pages = _safe_list(layout.get("pages", []))
    if not pages:
        raise ValueError("Projeto sem story layout.")

    target_language = str(language or layout.get("language") or project.get("language") or "pt-PT").strip() or "pt-PT"

    story_payload = {
        "language": target_language,
        "title": project.get("title", ""),
        "pages": pages,
        "raw_text": "\n\n".join(str(_safe_dict(page).get("text", "")).strip() for page in pages if str(_safe_dict(page).get("text", "")).strip()).strip(),
        "status": "layout_applied",
    }

    updated_project = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "story": story_payload if target_language == str(current.get("language", "pt-PT")).strip() else current.get("story", {}),
            "language_variants": {
                **_safe_dict(current.get("language_variants", {})),
                target_language: {
                    **_safe_dict(_safe_dict(current.get("language_variants", {})).get(target_language, {})),
                    **story_payload,
                },
            },
            "updated_at": now_iso(),
        }
    )

    return {
        "ok": True,
        "story": story_payload,
        "project": updated_project,
    }
