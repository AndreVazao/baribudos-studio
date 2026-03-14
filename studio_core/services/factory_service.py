from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item
from studio_core.services.audiobook_service import build_audiobook
from studio_core.services.ebook_service import build_epub
from studio_core.services.language_service import build_language_versions, get_supported_languages
from studio_core.services.publishing_service import publish_package
from studio_core.services.story_service import generate_story, generate_volume_guide
from studio_core.services.video_service import build_series_episode

PROJECTS_FILE = "data/projects.json"


def get_factory_capabilities() -> Dict[str, Any]:
    return {
        "engine": "python-factory-real",
        "story": True,
        "translations": True,
        "epub": True,
        "audiobook": True,
        "video": True,
        "guide": True,
        "publishing": True,
        "supported_languages": get_supported_languages()
    }


def _get_project(project_id: str) -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        if str(project.get("id", "")) == str(project_id):
            return project
    return None


def run_factory(project_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    requested_languages: List[str] = payload.get("languages") or project.get("output_languages") or [project.get("language", "pt-PT")]
    saga_id = str(project.get("saga_slug", "baribudos")).strip()

    create_story = bool(payload.get("createStory", True))
    create_translations = bool(payload.get("createTranslations", True))
    create_epub = bool(payload.get("createEpub", True))
    create_audiobook = bool(payload.get("createAudiobook", True))
    create_series = bool(payload.get("createSeries", True))
    create_guide = bool(payload.get("createGuide", False))
    publish = bool(payload.get("publish", False))

    if create_story:
        story = generate_story({
            "title": project.get("title", "Projeto"),
            "language": project.get("language", "pt-PT"),
            "saga_id": saga_id,
            "saga_name": project.get("saga_name", "Baribudos"),
            "raw_text": (project.get("story") or {}).get("raw_text", "")
        })
    else:
        story = project.get("story", {}) or {}

    language_versions = build_language_versions(story, requested_languages) if create_translations else {
        story.get("language", project.get("language", "pt-PT")): story
    }

    epub_outputs: Dict[str, Any] = {}
    if create_epub:
        for language, localized_story in language_versions.items():
            epub_outputs[language] = build_epub(
                localized_story,
                project_id=project_id,
                project_title=project.get("title", "Projeto"),
                language=language,
                author="André Vazão",
                cover_path=project.get("cover_image") or None,
            )

    audiobook_outputs = build_audiobook(
        language_versions,
        {
            "project_id": project_id,
            "project_title": project.get("title", "Projeto")
        }
    ) if create_audiobook else {}

    series_outputs: Dict[str, Any] = {}
    if create_series:
        for language, localized_story in language_versions.items():
            series_outputs[language] = build_series_episode(
                localized_story,
                {
                    "project_id": project_id,
                    "project_title": project.get("title", "Projeto"),
                    "language": language
                }
            )

    guide_output = generate_volume_guide({
        "project_title": project.get("title", "Projeto"),
        "story": story
    }) if create_guide else None

    publication_outputs = []
    if publish:
        for language in language_versions.keys():
            publication_outputs.append(
                publish_package({
                    "project_id": project_id,
                    "language": language,
                    "channel": "ebook",
                    "requested_by": str(payload.get("userName", "")).strip(),
                    "notes": f"Factory publication for {saga_id}"
                })
            )

    summary = {
        "project_id": project_id,
        "saga_id": saga_id,
        "story_created": create_story,
        "translation_count": len(language_versions),
        "epub_languages": list(epub_outputs.keys()),
        "audiobook_languages": list(audiobook_outputs.keys()),
        "series_languages": list(series_outputs.keys()),
        "guide_created": guide_output is not None,
        "publishing_runs": len(publication_outputs),
        "completed_at": now_iso()
    }

    def updater(current: Dict[str, Any]) -> Dict[str, Any]:
        current_outputs = current.get("outputs", {}) or {}

        return {
            **current,
            "story": story,
            "language_variants": {
                language: {
                    "language": language,
                    "title": localized_story.get("title", current.get("title", "")),
                    "pages": localized_story.get("pages", []),
                    "status": "generated"
                }
                for language, localized_story in language_versions.items()
            },
            "outputs": {
                **current_outputs,
                "epub": epub_outputs,
                "audiobook": audiobook_outputs,
                "video": series_outputs,
                "guide": guide_output,
                "publications": publication_outputs
            },
            "factory": {
                "last_run_id": str(uuid4()),
                "summary": summary
            },
            "updated_at": now_iso()
        }

    update_json_item(PROJECTS_FILE, project_id, updater)

    return {
        "story": story,
        "language_versions": language_versions,
        "epub": epub_outputs,
        "audiobook": audiobook_outputs,
        "video": series_outputs,
        "guide": guide_output,
        "publications": publication_outputs,
        "summary": summary
    }
