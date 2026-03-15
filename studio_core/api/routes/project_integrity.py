from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item
from studio_core.services.project_integrity_service import audit_project_integrity, repair_project_structure

router = APIRouter(prefix="/project-integrity", tags=["project-integrity"])

PROJECTS_FILE = "data/projects.json"


def _normalize_name(value: str) -> str:
    return str(value or "").strip().lower()


def _can_edit(user_role: str, user_name: str) -> bool:
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
def get_project_integrity(project_id: str) -> dict:
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    audit = audit_project_integrity(project)
    return {"ok": True, "audit": audit}


@router.post("/{project_id}/repair")
def repair_project(project_id: str, user_name: str = "", user_role: str = "") -> dict:
    if not _can_edit(user_role, user_name):
        raise HTTPException(status_code=403, detail="Sem permissão para reparar projeto.")

    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    repaired = repair_project_structure(project)

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **repaired,
            "updated_at": now_iso()
        }
    )

    return {
        "ok": True,
        "project": updated,
        "audit": audit_project_integrity(updated)
  }
