from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item

router = APIRouter(prefix="/project-commercial", tags=["project-commercial"])

PROJECTS_FILE = "data/projects.json"


def _normalize_name(value: str) -> str:
    return str(value or "").strip().lower()


def _can_edit_or_publish(user_role: str, user_name: str) -> bool:
    role = str(user_role or "").strip().lower()
    name = _normalize_name(user_name)
    return role in {"owner", "creator", "admin"} or name in {"andré", "andre", "esposa", "wife", "mama"}


def _get_project(project_id: str) -> dict | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        if str(project.get("id", "")) == str(project_id):
            return project
    return None


@router.get("/{project_id}")
def get_project_commercial(project_id: str) -> dict:
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    return {
        "ok": True,
        "project_id": project_id,
        "commercial": project.get("commercial", {})
    }


@router.patch("/{project_id}")
def patch_project_commercial(project_id: str, payload: dict, user_name: str = "", user_role: str = "") -> dict:
    if not _can_edit_or_publish(user_role, user_name):
        raise HTTPException(status_code=403, detail="Sem permissão comercial/editorial.")

    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    commercial = payload.get("commercial") or {}
    if not isinstance(commercial, dict):
        raise HTTPException(status_code=400, detail="commercial inválido.")

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "commercial": {
                **(current.get("commercial", {}) or {}),
                **commercial
            },
            "updated_at": now_iso()
        }
    )

    return {
        "ok": True,
        "project_id": project_id,
        "commercial": updated.get("commercial", {})
  }
