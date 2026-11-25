from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item
from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles
from studio_core.services.project_authorization import require_project_access

router = APIRouter(prefix="/project-commercial", tags=["project-commercial"])

PROJECTS_FILE = "data/projects.json"


def _safe_dict(value):
    return value if isinstance(value, dict) else {}


def _get_project(project_id: str) -> dict | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        if str(project.get("id", "")) == str(project_id):
            return project
    return None


@router.get("/{project_id}")
def get_project_commercial(
    project_id: str,
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor", "creator")),
) -> dict:
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")
    require_project_access(project, principal)

    return {
        "ok": True,
        "project_id": project_id,
        "commercial": _safe_dict(project.get("commercial")),
    }


@router.patch("/{project_id}")
def patch_project_commercial(
    project_id: str,
    payload: dict,
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor", "creator")),
) -> dict:
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")
    require_project_access(project, principal)

    commercial = payload.get("commercial") if isinstance(payload, dict) and isinstance(payload.get("commercial"), dict) else payload
    if not isinstance(commercial, dict):
        raise HTTPException(status_code=400, detail="commercial inválido.")

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "commercial": {
                **_safe_dict(current.get("commercial")),
                **commercial,
            },
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "project_id": project_id,
        "commercial": _safe_dict(updated.get("commercial")),
    }
