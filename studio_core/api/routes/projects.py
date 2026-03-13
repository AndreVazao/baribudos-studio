from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.core.models import Project, ProjectCreate, ProjectPatch, now_iso
from studio_core.core.storage import (
    append_json_item,
    list_json_items,
    update_json_item,
)

router = APIRouter(prefix="/projects", tags=["projects"])

PROJECTS_FILE = "data/projects.json"


@router.get("")
def list_projects() -> dict:
    return {"ok": True, "projects": list_json_items(PROJECTS_FILE)}


@router.post("")
def create_project(payload: ProjectCreate) -> dict:
    project = Project(
        title=payload.title.strip(),
        saga_slug=payload.saga_slug.strip(),
        saga_name=payload.saga_name.strip(),
        language=payload.language.strip(),
        output_languages=payload.output_languages or [payload.language.strip()],
        created_by=payload.created_by.strip(),
        story={
            "title": payload.title.strip(),
            "language": payload.language.strip(),
            "pages": [],
            "raw_text": ""
        }
    )

    append_json_item(PROJECTS_FILE, project.model_dump())
    return {"ok": True, "project": project.model_dump()}


@router.patch("/{project_id}")
def patch_project(project_id: str, payload: ProjectPatch) -> dict:
    def updater(current: dict) -> dict:
        updated = {
            **current,
            "updated_at": now_iso(),
        }

        if payload.title is not None:
            updated["title"] = payload.title.strip()

        if payload.saga_slug is not None:
            updated["saga_slug"] = payload.saga_slug.strip()

        if payload.saga_name is not None:
            updated["saga_name"] = payload.saga_name.strip()

        if payload.language is not None:
            updated["language"] = payload.language.strip()

        if payload.output_languages is not None:
            updated["output_languages"] = payload.output_languages

        if payload.status is not None:
            updated["status"] = payload.status

        if payload.editorial_status is not None:
            updated["editorial_status"] = payload.editorial_status

        if payload.front_matter is not None:
            updated["front_matter"] = {
                **current.get("front_matter", {}),
                **payload.front_matter
            }

        if payload.story is not None:
            updated["story"] = {
                **current.get("story", {}),
                **payload.story
            }

        return updated

    try:
        project = update_json_item(PROJECTS_FILE, project_id, updater)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {"ok": True, "project": project}
