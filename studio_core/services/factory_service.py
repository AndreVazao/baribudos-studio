from __future__ import annotations

from typing import Any, Dict

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item
from studio_core.services.project_factory_engine import run_project_factory_engine
from studio_core.services.saga_runtime_service import load_saga_runtime

PROJECTS_FILE = "data/projects.json"


def get_factory_capabilities() -> Dict[str, Any]:
    return {
        "engine": "project-factory-engine-v2",
        "story": True,
        "cover": True,
        "epub": True,
        "audiobook": True,
        "video": True,
        "guide": True,
        "runtime_canon_aware": True,
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

    saga_id = str(project.get("saga_slug", "baribudos")).strip() or "baribudos"
    runtime = load_saga_runtime(saga_id)

    result = run_project_factory_engine(
        runtime=runtime,
        project=project,
        payload=payload or {},
    )

    story = result.get("story", {}) or {}
    language_variants = result.get("language_variants", {}) or {}
    cover_output = result.get("cover")
    ebook_outputs = result.get("ebook", {}) or {}
    audiobook_outputs = result.get("audiobook", {}) or {}
    video_outputs = result.get("video", {}) or {}
    guide_output = result.get("guide")
    summary = result.get("summary", {}) or {}

    update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "story": story,
            "language_variants": language_variants,
            "cover_image": (cover_output or {}).get("file_path", current.get("cover_image", "")),
            "outputs": {
                **(current.get("outputs", {}) or {}),
                "covers": cover_output or (current.get("outputs", {}) or {}).get("covers"),
                "epub": ebook_outputs,
                "audiobook": audiobook_outputs,
                "video": video_outputs,
                "guide": guide_output,
            },
            "factory": {
                "summary": {
                    **summary,
                    "completed_at": now_iso(),
                }
            },
            "updated_at": now_iso(),
        },
    )

    return {
        "story": story,
        "language_variants": language_variants,
        "cover": cover_output,
        "ebook": ebook_outputs,
        "audiobook": audiobook_outputs,
        "video": video_outputs,
        "guide": guide_output,
        "summary": {
            **summary,
            "completed_at": now_iso(),
        },
    }
