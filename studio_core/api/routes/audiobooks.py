from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.core.storage import read_json
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
def export_audiobook(project_id: str, payload: dict) -> dict:
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    story = project.get("story", {}) or {}
    language = str(payload.get("language", story.get("language", "pt-PT"))).strip()

    result = build_audiobook(
        {language: story},
        {
            "project_id": project_id,
            "project_title": project.get("title", "Projeto")
        }
    )
    return {"ok": True, "result": result}
