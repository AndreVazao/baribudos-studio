from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.core.storage import read_json
from studio_core.services.video_service import build_series_episode

router = APIRouter(prefix="/videos", tags=["videos"])
PROJECTS_FILE = "data/projects.json"


def _get_project(project_id: str) -> dict | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        if str(project.get("id", "")) == str(project_id):
            return project
    return None


@router.post("/export/{project_id}")
def export_video(project_id: str, payload: dict) -> dict:
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    story = project.get("story", {}) or {}
    language = str(payload.get("language", story.get("language", "pt-PT"))).strip()

    result = build_series_episode(
        story,
        {
            "project_id": project_id,
            "project_title": project.get("title", "Projeto"),
            "language": language
        }
    )
    return {"ok": True, "result": result}
