from __future__ import annotations

from typing import Any, Dict, List

from studio_core.services.audiobook_service import build_audiobook
from studio_core.services.cover_service import build_cover
from studio_core.services.ebook_service import build_epub
from studio_core.services.illustration_integration_service import (
    build_video_frame_sequence,
    enrich_story_pages_with_illustrations,
)
from studio_core.services.saga_runtime_service import load_saga_runtime
from studio_core.services.story_generation_engine import generate_canon_story
from studio_core.services.story_service import generate_volume_guide
from studio_core.services.video_service import build_series_episode


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _resolve_languages(runtime: Dict[str, Any], project: Dict[str, Any], payload: Dict[str, Any]) -> List[str]:
    requested = payload.get("languages")
    if isinstance(requested, list) and requested:
        return [str(item).strip() for item in requested if str(item).strip()]

    project_langs = project.get("output_languages")
    if isinstance(project_langs, list) and project_langs:
        langs = [str(item).strip() for item in project_langs if str(item).strip()]
        if langs:
            return langs

    runtime_langs = runtime.get("output_languages")
    if isinstance(runtime_langs, list) and runtime_langs:
        langs = [str(item).strip() for item in runtime_langs if str(item).strip()]
        if langs:
            return langs

    return [str(project.get("language") or runtime.get("default_language") or "pt-PT").strip() or "pt-PT"]


def _build_story_variants(
    *,
    runtime: Dict[str, Any],
    project: Dict[str, Any],
    payload: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    languages = _resolve_languages(runtime, project, payload)
    story_variants: Dict[str, Dict[str, Any]] = {}

    base_story = _safe_dict(project.get("story", {}))
    project_title = str(project.get("title", "Projeto")).strip() or "Projeto"

    for language in languages:
        raw_text = ""
        if language == str(project.get("language", "")).strip():
            raw_text = str(base_story.get("raw_text", "")).strip()

        story_variants[language] = generate_canon_story({
            "saga_id": runtime.get("slug", "baribudos"),
            "title": project_title,
            "language": language,
            "raw_text": raw_text,
            "protagonist": payload.get("protagonist", ""),
            "value_theme": payload.get("value_theme", ""),
        })

    return story_variants


def _build_cover_output(
    *,
    runtime: Dict[str, Any],
    project: Dict[str, Any],
    payload: Dict[str, Any],
) -> Dict[str, Any] | None:
    illustration_path = str(project.get("illustration_path", "")).strip()
    if not illustration_path:
        return None

    metadata = _safe_dict(runtime.get("metadata", {}))
    language = str(project.get("language") or runtime.get("default_language") or "pt-PT").strip() or "pt-PT"
    age_range = str(
        payload.get("age_range")
        or _safe_dict(project.get("commercial", {})).get("target_age")
        or metadata.get("target_age")
        or "4-10"
    ).strip()

    return build_cover(
        saga_id=str(runtime.get("slug", "baribudos")),
        project_id=str(project.get("id", "")).strip(),
        title=str(project.get("title", "Projeto")).strip() or "Projeto",
        age_range=age_range,
        illustration_path=illustration_path,
        language=language,
        producer=str(metadata.get("producer", "")).strip() or None,
        output_name=f"{str(project.get('title', 'projeto')).lower().replace(' ', '_')}_cover.png",
    )


def _build_ebook_outputs(
    *,
    runtime: Dict[str, Any],
    project: Dict[str, Any],
    story_variants: Dict[str, Dict[str, Any]],
    cover_output: Dict[str, Any] | None,
) -> Dict[str, Any]:
    metadata = _safe_dict(runtime.get("metadata", {}))
    project_id = str(project.get("id", "")).strip()
    project_title = str(project.get("title", "Projeto")).strip() or "Projeto"
    cover_path = (cover_output or {}).get("file_path") or project.get("cover_image") or None

    outputs: Dict[str, Any] = {}
    for language, story in story_variants.items():
        illustrated_story = enrich_story_pages_with_illustrations(project, story)
        outputs[language] = build_epub(
            illustrated_story,
            project_id=project_id,
            project_title=project_title,
            language=language,
            author=str(metadata.get("author_default", "")).strip() or "Autor",
            cover_path=cover_path,
            saga_id=str(runtime.get("slug", "baribudos")),
        )
    return outputs


def _build_audiobook_outputs(
    *,
    project: Dict[str, Any],
    story_variants: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    return build_audiobook(
        story_variants,
        {
            "project_id": str(project.get("id", "")).strip(),
            "project_title": str(project.get("title", "Projeto")).strip() or "Projeto",
        },
    )


def _build_video_outputs(
    *,
    project: Dict[str, Any],
    story_variants: Dict[str, Dict[str, Any]],
    cover_output: Dict[str, Any] | None,
    audiobook_outputs: Dict[str, Any],
) -> Dict[str, Any]:
    outputs: Dict[str, Any] = {}
    project_id = str(project.get("id", "")).strip()
    project_title = str(project.get("title", "Projeto")).strip() or "Projeto"
    cover_path = (cover_output or {}).get("file_path") or project.get("cover_image") or ""

    video_sequence = build_video_frame_sequence(project)
    approved_frames = _safe_dict(video_sequence).get("frames", [])

    for language, story in story_variants.items():
        audio_path = _safe_dict(audiobook_outputs.get(language, {})).get("file_path", "")

        if isinstance(approved_frames, list) and approved_frames:
            hero_image = str(_safe_dict(approved_frames[0]).get("image_path", "")).strip() or cover_path
        else:
            hero_image = cover_path

        outputs[language] = build_series_episode(
            story,
            {
                "project_id": project_id,
                "project_title": project_title,
                "language": language,
                "cover_path": hero_image,
                "audio_path": audio_path,
            },
        )
        outputs[language]["storyboard_frames_count"] = len(approved_frames) if isinstance(approved_frames, list) else 0

    return outputs


def _build_language_variants(story_variants: Dict[str, Dict[str, Any]], project_title: str, project: Dict[str, Any]) -> Dict[str, Any]:
    return {
        language: {
            "language": language,
            "title": str(story.get("title", project_title)).strip() or project_title,
            "pages": enrich_story_pages_with_illustrations(project, story).get("pages", []),
            "status": "generated",
            "raw_text": str(story.get("raw_text", "")).strip(),
            "protagonist": str(story.get("protagonist", "")).strip(),
            "value_theme": str(story.get("value_theme", "")).strip(),
            "final_phrase": str(story.get("final_phrase", "")).strip(),
        }
        for language, story in story_variants.items()
    }


def run_project_factory_engine(
    *,
    runtime: Dict[str, Any],
    project: Dict[str, Any],
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    project_title = str(project.get("title", "Projeto")).strip() or "Projeto"

    create_story = bool(payload.get("createStory", True))
    create_cover = bool(payload.get("createCover", True))
    create_epub = bool(payload.get("createEpub", True))
    create_audiobook = bool(payload.get("createAudiobook", True))
    create_series = bool(payload.get("createSeries", True))
    create_guide = bool(payload.get("createGuide", True))

    if create_story:
        story_variants = _build_story_variants(runtime=runtime, project=project, payload=payload)
    else:
        existing_variants = _safe_dict(project.get("language_variants", {}))
        if existing_variants:
            story_variants = existing_variants
        else:
            base_story = _safe_dict(project.get("story", {}))
            language = str(project.get("language") or runtime.get("default_language") or "pt-PT").strip() or "pt-PT"
            story_variants = {language: base_story}

    main_language = str(project.get("language") or runtime.get("default_language") or "pt-PT").strip() or "pt-PT"
    main_story = _safe_dict(story_variants.get(main_language, {}))
    if not main_story and story_variants:
        main_story = _safe_dict(next(iter(story_variants.values())))

    cover_output = _build_cover_output(runtime=runtime, project=project, payload=payload) if create_cover else None
    ebook_outputs = _build_ebook_outputs(runtime=runtime, project=project, story_variants=story_variants, cover_output=cover_output) if create_epub else {}
    audiobook_outputs = _build_audiobook_outputs(project=project, story_variants=story_variants) if create_audiobook else {}
    video_outputs = _build_video_outputs(project=project, story_variants=story_variants, cover_output=cover_output, audiobook_outputs=audiobook_outputs) if create_series else {}

    guide_output = generate_volume_guide({
        "project_title": project_title,
        "story": main_story,
    }) if create_guide else None

    language_variants = _build_language_variants(story_variants, project_title, project)

    return {
        "story": enrich_story_pages_with_illustrations(project, main_story),
        "story_variants": story_variants,
        "language_variants": language_variants,
        "cover": cover_output,
        "ebook": ebook_outputs,
        "audiobook": audiobook_outputs,
        "video": video_outputs,
        "guide": guide_output,
        "summary": {
            "project_id": str(project.get("id", "")).strip(),
            "project_title": project_title,
            "ip_slug": str(runtime.get("slug", "")).strip(),
            "runtime_name": str(runtime.get("name", "")).strip(),
            "languages": list(story_variants.keys()),
            "cover_created": cover_output is not None,
            "ebook_languages": list(ebook_outputs.keys()),
            "audiobook_languages": list(audiobook_outputs.keys()),
            "video_languages": list(video_outputs.keys()),
            "guide_created": guide_output is not None,
            "runtime_validation_ok": bool((runtime.get("validation") or {}).get("ok", False)),
        },
    }


def build_factory_context(ip_slug: str, project_payload: Dict[str, Any]) -> Dict[str, Any]:
    runtime = load_saga_runtime(ip_slug)
    return {
        "ip": {
            "id": runtime.get("id", ""),
            "slug": runtime.get("slug", ""),
            "name": runtime.get("name", ""),
            "owner_id": runtime.get("owner_id", ""),
            "owner_name": runtime.get("owner_name", ""),
        },
        "slug": runtime.get("slug", ""),
        "name": runtime.get("name", ""),
        "default_language": runtime.get("default_language", "pt-PT"),
        "output_languages": runtime.get("output_languages", ["pt-PT"]),
        "metadata": runtime.get("metadata", {}),
        "palette": runtime.get("palette", {}),
        "brand_assets": runtime.get("brand_assets", {}),
        "permissions": runtime.get("permissions", {}),
        "canons": runtime.get("canons", {}),
        "resolved": runtime.get("resolved", {}),
        "validation": runtime.get("validation", {}),
        "main_characters": runtime.get("main_characters", []),
        "project_payload": project_payload,
    }
