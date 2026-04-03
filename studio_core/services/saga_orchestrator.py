from __future__ import annotations

from typing import Dict, Any, List
from uuid import uuid4

from studio_core.services.saga_runtime_service import load_saga_runtime
from studio_core.services.story_generation_engine import generate_canon_story


def _safe_dict(v: Any) -> Dict[str, Any]:
    return v if isinstance(v, dict) else {}


def _safe_list(v: Any) -> List[Any]:
    return v if isinstance(v, list) else []


def _resolve_languages(runtime: Dict[str, Any], payload: Dict[str, Any]) -> List[str]:
    payload_langs = payload.get("output_languages")
    if isinstance(payload_langs, list) and payload_langs:
        return payload_langs

    runtime_langs = runtime.get("output_languages")
    if isinstance(runtime_langs, list) and runtime_langs:
        return runtime_langs

    return [runtime.get("default_language", "pt-PT")]


def _generate_multilang_story(runtime: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    languages = _resolve_languages(runtime, payload)

    stories = {}
    for lang in languages:
        lang_payload = dict(payload)
        lang_payload["language"] = lang
        story = generate_canon_story(lang_payload)
        stories[lang] = story

    return stories


def _create_editorial_manifest(runtime: Dict[str, Any], stories: Dict[str, Any]) -> Dict[str, Any]:
    resolved = _safe_dict(runtime.get("resolved"))
    metadata = _safe_dict(runtime.get("metadata"))

    return {
        "id": str(uuid4()),
        "series_name": resolved.get("series_name"),
        "mission": resolved.get("mission"),
        "target_age": resolved.get("target_age"),
        "genre": resolved.get("genre"),
        "tagline": resolved.get("tagline"),
        "author_default": metadata.get("author_default"),
        "producer": metadata.get("producer"),
        "languages": list(stories.keys()),
    }


def _build_project_structure(runtime: Dict[str, Any], stories: Dict[str, Any]) -> Dict[str, Any]:
    project_id = str(uuid4())

    return {
        "project_id": project_id,
        "ip_slug": runtime.get("slug"),
        "stories": stories,
        "status": "draft",
        "outputs": {
            "ebook": {},
            "audiobook": {},
            "series": {},
        },
    }


def run_saga_pipeline(payload: Dict[str, Any]) -> Dict[str, Any]:
    saga_id = payload.get("saga_id", "baribudos")
    runtime = load_saga_runtime(saga_id)
    stories = _generate_multilang_story(runtime, payload)
    manifest = _create_editorial_manifest(runtime, stories)
    project = _build_project_structure(runtime, stories)

    return {
        "runtime": runtime,
        "manifest": manifest,
        "project": project,
    }
