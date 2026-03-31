from __future__ import annotations

from typing import Any, Dict, List

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item
from studio_core.services.story_source_service import get_story_source

PROJECTS_FILE = "data/projects.json"


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _get_project(project_id: str) -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    for item in projects:
        if _safe_text(item.get("id")) == _safe_text(project_id):
            return item
    return None


def _resolve_languages(project: Dict[str, Any], payload: Dict[str, Any]) -> List[str]:
    requested = payload.get("languages")
    if isinstance(requested, list) and requested:
        langs = [_safe_text(item) for item in requested if _safe_text(item)]
        if langs:
            return langs
    project_langs = project.get("output_languages")
    if isinstance(project_langs, list) and project_langs:
        langs = [_safe_text(item) for item in project_langs if _safe_text(item)]
        if langs:
            return langs
    base = _safe_text(project.get("language")) or "pt-PT"
    return [base]


def _fake_translate(text: str, target_language: str, source_language: str) -> str:
    clean = _safe_text(text)
    if not clean:
        return ""
    if target_language == source_language:
        return clean
    return f"[{target_language} translation from {source_language}]\n\n{clean}"


def generate_story_translations(project_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    story_source = get_story_source(project_id)
    source_text = _safe_text(story_source.get("story_source_text"))
    source_language = _safe_text(story_source.get("story_source_language")) or _safe_text(project.get("language")) or "pt-PT"
    if not source_text:
        raise ValueError("story_source_text_required")

    languages = _resolve_languages(project, payload)
    current_variants = _safe_dict(project.get("language_variants", {}))
    next_variants = {**current_variants}

    for language in languages:
        translated = _fake_translate(source_text, language, source_language)
        next_variants[language] = {
            **_safe_dict(current_variants.get(language, {})),
            "language": language,
            "title": _safe_text(project.get("title")),
            "raw_text": translated,
            "source_language": source_language,
            "translation_status": "generated",
            "translation_engine": "text-first-base-v1",
            "updated_at": now_iso(),
        }

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "language_variants": next_variants,
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "project_id": project_id,
        "source_language": source_language,
        "languages": languages,
        "language_variants": next_variants,
        "project": updated,
    }


def get_story_translations(project_id: str) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")
    return {
        "ok": True,
        "project_id": project_id,
        "language_variants": _safe_dict(project.get("language_variants", {})),
    }
