from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from studio_core.services.project_route_auth import require_project_path_access
from studio_core.services.auth_principal import AuthenticatedPrincipal

from studio_core.services.story_source_service import (
    get_story_source,
    get_story_source_gate,
    lock_story_text,
    save_story_source,
)

router = APIRouter(prefix="/story-source", tags=["story-source"])


@router.get("/{project_id}")
def read_story_source(project_id: str, _principal=Depends(require_project_path_access)) -> dict:
    try:
        return {"ok": True, "story_source": get_story_source(project_id)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{project_id}")
def write_story_source(project_id: str, payload: dict | None = None, _principal=Depends(require_project_path_access)) -> dict:
    try:
        return save_story_source(project_id, payload or {})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{project_id}/lock")
def lock_text(project_id: str, approved: bool = False, principal: AuthenticatedPrincipal = Depends(require_project_path_access)) -> dict:
    if principal.role.lower() not in {"owner", "admin", "creator"}:
        raise HTTPException(status_code=403, detail="Sem permissão para bloquear ou aprovar o texto.")
    try:
        return lock_story_text(project_id, approved=approved)
    except ValueError as exc:
        status = 404 if str(exc) == "Projeto não encontrado." else 400
        raise HTTPException(status_code=status, detail=str(exc)) from exc


@router.get("/{project_id}/gate")
def read_story_source_gate(project_id: str, _principal=Depends(require_project_path_access)) -> dict:
    try:
        return get_story_source_gate(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
