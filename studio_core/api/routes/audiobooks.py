from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item
from studio_core.services.audiobook_service import build_audiobook

router = APIRouter(prefix="/audiobooks", tags=["audiobooks"])

PROJECTS_FILE = "data/projects.json"


def _get_project(project_id: str) -> dict | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        if str(project.get("id", "")) == str(project_id):
            return project
    return None


@router.post("/export/{project_id}")
def export_audiobook(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    try:
        language = str(payload.get("language", project.get("language", "pt-PT"))).strip()
        story = (project.get("language_variants", {}) or {}).get(language) or project.get("story", {}) or {}

        result_map = build_audiobook(
            {
                language: {
                    **story,
                    "language": language
                }
            },
            {
                "project_id": project_id,
                "project_title": project.get("title", "Projeto")
            }
        )

        result = result_map.get(language)

        update_json_item(
            PROJECTS_FILE,
            project_id,
            lambda current: {
                **current,
                "outputs": {
                    **(current.get("outputs", {}) or {}),
                    "audiobook": {
                        **((current.get("outputs", {}) or {}).get("audiobook", {}) or {}),
                        language: result
                    }
                },
                "updated_at": now_iso()
            }
        )

        return {"ok": True, "result": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
