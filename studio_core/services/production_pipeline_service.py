from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.models import now_iso
from studio_core.core.storage import append_json_item, read_json, update_json_item
from studio_core.services.audiobook_service import build_audiobook
from studio_core.services.ebook_service import build_epub
from studio_core.services.project_factory_engine import run_project_factory_engine
from studio_core.services.saga_runtime_service import load_saga_runtime
from studio_core.services.story_generation_engine import generate_canon_story
from studio_core.services.video_service import build_series_episode

PROJECTS_FILE = "data/projects.json"
PRODUCTION_RUNS_FILE = "data/production_runs.json"

PIPELINE_STATES = [
    "draft",
    "running",
    "story_ready",
    "cover_ready",
    "ebook_ready",
    "audio_ready",
    "video_ready",
    "guide_ready",
    "completed",
    "failed",
]


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _get_project(project_id: str) -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        if str(project.get("id", "")).strip() == str(project_id).strip():
            return project
    return None


def _resolve_languages(runtime: Dict[str, Any], project: Dict[str, Any], payload: Dict[str, Any]) -> List[str]:
    requested = payload.get("languages")
    if isinstance(requested, list) and requested:
        langs = [str(item).strip() for item in requested if str(item).strip()]
        if langs:
            return langs

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


def _append_log(logs: List[Dict[str, Any]], message: str, level: str = "info") -> None:
    logs.append({
        "at": now_iso(),
        "level": level,
        "message": str(message).strip(),
    })


def _update_project_outputs(
    project_id: str,
    *,
    story: Dict[str, Any] | None = None,
    language_variants: Dict[str, Any] | None = None,
    cover: Dict[str, Any] | None = None,
    ebook: Dict[str, Any] | None = None,
    audiobook: Dict[str, Any] | None = None,
    video: Dict[str, Any] | None = None,
    guide: Dict[str, Any] | None = None,
    production: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    def updater(current: Dict[str, Any]) -> Dict[str, Any]:
        current_outputs = _safe_dict(current.get("outputs", {}))

        next_outputs = {
            **current_outputs,
            "covers": cover if cover is not None else current_outputs.get("covers"),
            "epub": ebook if ebook is not None else current_outputs.get("epub", {}),
            "audiobook": audiobook if audiobook is not None else current_outputs.get("audiobook", {}),
            "video": video if video is not None else current_outputs.get("video", {}),
            "guide": guide if guide is not None else current_outputs.get("guide"),
        }

        return {
            **current,
            "story": story if story is not None else current.get("story", {}),
            "language_variants": language_variants if language_variants is not None else current.get("language_variants", {}),
            "cover_image": (cover or {}).get("file_path", current.get("cover_image", "")),
            "outputs": next_outputs,
            "production": production if production is not None else current.get("production", {}),
            "updated_at": now_iso(),
        }

    return update_json_item(PROJECTS_FILE, project_id, updater)


def _build_story_variants(runtime: Dict[str, Any], project: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    languages = _resolve_languages(runtime, project, payload)
    project_title = str(project.get("title", "Projeto")).strip() or "Projeto"
    base_story = _safe_dict(project.get("story", {}))

    result: Dict[str, Dict[str, Any]] = {}
    for language in languages:
        raw_text = ""
        if language == str(project.get("language", "")).strip():
            raw_text = str(base_story.get("raw_text", "")).strip()

        result[language] = generate_canon_story({
            "saga_id": runtime.get("slug", "baribudos"),
            "title": project_title,
            "language": language,
            "raw_text": raw_text,
            "protagonist": payload.get("protagonist", ""),
            "value_theme": payload.get("value_theme", ""),
        })

    return result


def _build_language_variants(story_variants: Dict[str, Dict[str, Any]], project_title: str) -> Dict[str, Any]:
    return {
        language: {
            "language": language,
            "title": str(story.get("title", project_title)).strip() or project_title,
            "pages": _safe_list(story.get("pages", [])),
            "status": "generated",
            "raw_text": str(story.get("raw_text", "")).strip(),
            "protagonist": str(story.get("protagonist", "")).strip(),
            "value_theme": str(story.get("value_theme", "")).strip(),
            "final_phrase": str(story.get("final_phrase", "")).strip(),
        }
        for language, story in story_variants.items()
    }


def _run_manual_outputs(
    runtime: Dict[str, Any],
    project: Dict[str, Any],
    story_variants: Dict[str, Dict[str, Any]],
    payload: Dict[str, Any],
    logs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    metadata = _safe_dict(runtime.get("metadata", {}))
    project_id = str(project.get("id", "")).strip()
    project_title = str(project.get("title", "Projeto")).strip() or "Projeto"
    project_language = str(project.get("language") or runtime.get("default_language") or "pt-PT").strip() or "pt-PT"
    current_outputs = _safe_dict(project.get("outputs", {}))
    cover_output = _safe_dict(current_outputs.get("covers", {})) or None

    output_story_language = project_language
    main_story = _safe_dict(story_variants.get(output_story_language, {}))
    if not main_story and story_variants:
        output_story_language = next(iter(story_variants.keys()))
        main_story = _safe_dict(story_variants[output_story_language])

    result = {
        "story": main_story,
        "story_variants": story_variants,
        "language_variants": _build_language_variants(story_variants, project_title),
        "cover": cover_output,
        "ebook": _safe_dict(current_outputs.get("epub", {})),
        "audiobook": _safe_dict(current_outputs.get("audiobook", {})),
        "video": _safe_dict(current_outputs.get("video", {})),
        "guide": current_outputs.get("guide"),
    }

    if bool(payload.get("createEpub", False)):
        _append_log(logs, "A gerar EPUB.")
        ebook_outputs: Dict[str, Any] = {}
        for language, story in story_variants.items():
            ebook_outputs[language] = build_epub(
                story,
                project_id=project_id,
                project_title=project_title,
                language=language,
                author=str(metadata.get("author_default", "")).strip() or "Autor",
                cover_path=(cover_output or {}).get("file_path") or project.get("cover_image") or None,
                saga_id=str(runtime.get("slug", "baribudos")),
            )
        result["ebook"] = ebook_outputs
        _append_log(logs, "EPUB gerado.")

    if bool(payload.get("createAudiobook", False)):
        _append_log(logs, "A gerar audiobook.")
        result["audiobook"] = build_audiobook(
            story_variants,
            {
                "project_id": project_id,
                "project_title": project_title,
            },
        )
        _append_log(logs, "Audiobook gerado.")

    if bool(payload.get("createSeries", False)):
        _append_log(logs, "A gerar vídeo/série.")
        video_outputs: Dict[str, Any] = {}
        audiobook_outputs = _safe_dict(result.get("audiobook", {}))
        for language, story in story_variants.items():
            audio_path = _safe_dict(audiobook_outputs.get(language, {})).get("file_path", "")
            video_outputs[language] = build_series_episode(
                story,
                {
                    "project_id": project_id,
                    "project_title": project_title,
                    "language": language,
                    "cover_path": (cover_output or {}).get("file_path") or project.get("cover_image", ""),
                    "audio_path": audio_path,
                },
            )
        result["video"] = video_outputs
        _append_log(logs, "Vídeo/série gerado.")

    return result


def run_production_pipeline(project_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    runtime = load_ip_runtime(str(project.get("saga_slug", "baribudos")).strip() or "baribudos")
    run_id = str(uuid4())
    logs: List[Dict[str, Any]] = []
    state = "running"

    mode = str(payload.get("mode", "auto")).strip().lower()
    if mode not in {"auto", "manual"}:
        mode = "auto"

    _append_log(logs, f"Pipeline iniciado em modo '{mode}'.")
    _append_log(logs, f"Runtime carregado: {runtime.get('name', '')} ({runtime.get('slug', '')}).")

    try:
        if mode == "auto":
            _append_log(logs, "A executar factory engine automática.")
            result = run_project_factory_engine(
                runtime=runtime,
                project=project,
                payload={
                    "createStory": payload.get("createStory", True),
                    "createCover": payload.get("createCover", True),
                    "createEpub": payload.get("createEpub", True),
                    "createAudiobook": payload.get("createAudiobook", True),
                    "createSeries": payload.get("createSeries", True),
                    "createGuide": payload.get("createGuide", True),
                    "languages": payload.get("languages"),
                    "age_range": payload.get("age_range", ""),
                    "protagonist": payload.get("protagonist", ""),
                    "value_theme": payload.get("value_theme", ""),
                },
            )
            state = "completed"
            _append_log(logs, "Factory automática concluída.")
        else:
            _append_log(logs, "A gerar story variants para modo manual.")
            story_variants = _build_story_variants(runtime, project, payload)
            result = _run_manual_outputs(runtime, project, story_variants, payload, logs)
            state = "completed"
            _append_log(logs, "Pipeline manual concluída.")

        production_summary = {
            "run_id": run_id,
            "mode": mode,
            "state": state,
            "runtime_slug": runtime.get("slug", ""),
            "runtime_name": runtime.get("name", ""),
            "logs": logs,
            "summary": result.get("summary", {}),
            "completed_at": now_iso(),
        }

        updated_project = _update_project_outputs(
            project_id,
            story=result.get("story"),
            language_variants=result.get("language_variants"),
            cover=result.get("cover"),
            ebook=result.get("ebook"),
            audiobook=result.get("audiobook"),
            video=result.get("video"),
            guide=result.get("guide"),
            production=production_summary,
        )

        append_json_item(PRODUCTION_RUNS_FILE, {
            "id": run_id,
            "project_id": project_id,
            "mode": mode,
            "state": state,
            "runtime_slug": runtime.get("slug", ""),
            "runtime_name": runtime.get("name", ""),
            "logs": logs,
            "created_at": now_iso(),
        })

        return {
            "ok": True,
            "run_id": run_id,
            "mode": mode,
            "state": state,
            "runtime": {
                "slug": runtime.get("slug", ""),
                "name": runtime.get("name", ""),
                "validation": runtime.get("validation", {}),
            },
            "logs": logs,
            "result": result,
            "project": updated_project,
        }

    except Exception as exc:
        state = "failed"
        _append_log(logs, f"Falha no pipeline: {exc}", level="error")

        append_json_item(PRODUCTION_RUNS_FILE, {
            "id": run_id,
            "project_id": project_id,
            "mode": mode,
            "state": state,
            "runtime_slug": runtime.get("slug", ""),
            "runtime_name": runtime.get("name", ""),
            "logs": logs,
            "created_at": now_iso(),
        })

        update_json_item(
            PROJECTS_FILE,
            project_id,
            lambda current: {
                **current,
                "production": {
                    "run_id": run_id,
                    "mode": mode,
                    "state": state,
                    "runtime_slug": runtime.get("slug", ""),
                    "runtime_name": runtime.get("name", ""),
                    "logs": logs,
                    "updated_at": now_iso(),
                },
                "updated_at": now_iso(),
            },
        )

        raise


def list_production_runs() -> List[Dict[str, Any]]:
    runs = read_json(PRODUCTION_RUNS_FILE, [])
    return runs if isinstance(runs, list) else []
    
