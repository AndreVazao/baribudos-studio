from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.core.models import Project, ProjectCreate, ProjectPatch, now_iso
from studio_core.core.storage import append_json_item, list_json_items, update_json_item

router = APIRouter(prefix="/projects", tags=["projects"])

PROJECTS_FILE = "data/projects.json"


def _normalize_name(value: str) -> str:
    return str(value or "").strip().lower()


def _can_view_project(project: dict, user_id: str = "", user_name: str = "", user_role: str = "") -> bool:
    if not bool(project.get("visible_to_owner_only", True)):
        return True

    if not user_id and not user_name:
        return False

    if str(project.get("created_by", "")).strip() == str(user_id).strip():
        return True

    if _normalize_name(project.get("created_by_name", "")) == _normalize_name(user_name):
        return True

    return False


def _can_edit_or_publish(user_role: str, user_name: str) -> bool:
    role = str(user_role or "").strip().lower()
    name = _normalize_name(user_name)
    return role in {"owner", "creator", "admin"} or name in {"andré", "andre", "esposa", "wife", "mama"}


@router.get("")
def list_projects(user_id: str = "", user_name: str = "", user_role: str = "") -> dict:
    projects = list_json_items(PROJECTS_FILE)
    visible = [
        project for project in projects
        if _can_view_project(project, user_id=user_id, user_name=user_name, user_role=user_role)
    ]
    return {"ok": True, "projects": visible}


@router.post("")
def create_project(payload: ProjectCreate) -> dict:
    project = Project(
        title=payload.title.strip(),
        saga_slug=payload.saga_slug.strip(),
        saga_name=payload.saga_name.strip(),
        language=payload.language.strip(),
        output_languages=payload.output_languages or [payload.language.strip()],
        created_by=payload.created_by.strip(),
        created_by_name=payload.created_by_name.strip(),
        visible_to_owner_only=payload.visible_to_owner_only,
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
def patch_project(project_id: str, payload: ProjectPatch, user_name: str = "", user_role: str = "") -> dict:
    if not _can_edit_or_publish(user_role, user_name):
        raise HTTPException(status_code=403, detail="Sem permissão editorial para editar projetos.")

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

        if payload.cover_image is not None:
            updated["cover_image"] = payload.cover_image

        if payload.illustration_path is not None:
            updated["illustration_path"] = payload.illustration_path

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
