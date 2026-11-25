from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from studio_core.core.storage import read_json
from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles
from studio_core.services.distribution_hub_service import (
    get_distribution_hub_snapshot,
    patch_distribution_hub,
    refresh_distribution_hub,
)
from studio_core.services.project_authorization import require_project_access

router = APIRouter(prefix="/distribution-hub", tags=["distribution-hub"])

PROJECTS_FILE = "data/projects.json"


def _get_project(project_id: str) -> dict | None:
    projects = read_json(PROJECTS_FILE, [])
    if not isinstance(projects, list):
        return None
    return next((item for item in projects if str(item.get("id", "")) == str(project_id)), None)


def _authorize(project_id: str, principal: AuthenticatedPrincipal) -> None:
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")
    require_project_access(project, principal)


@router.get("/{project_id}")
def get_distribution_hub(
    project_id: str,
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor", "creator")),
) -> dict:
    _authorize(project_id, principal)
    try:
        snapshot = get_distribution_hub_snapshot(project_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return {"ok": True, "project_id": project_id, "distribution_hub": snapshot}


@router.post("/{project_id}/refresh")
def refresh_distribution_hub_endpoint(
    project_id: str,
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor", "creator")),
) -> dict:
    _authorize(project_id, principal)
    try:
        snapshot = refresh_distribution_hub(project_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return {"ok": True, "project_id": project_id, "distribution_hub": snapshot}


@router.patch("/{project_id}")
def patch_distribution_hub_endpoint(
    project_id: str,
    payload: dict,
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor", "creator")),
) -> dict:
    _authorize(project_id, principal)
    patch = payload.get("distribution_hub") if isinstance(payload.get("distribution_hub"), dict) else payload
    if not isinstance(patch, dict):
        raise HTTPException(status_code=400, detail="distribution_hub inválido.")

    try:
        snapshot = patch_distribution_hub(project_id, patch)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return {"ok": True, "project_id": project_id, "distribution_hub": snapshot}
