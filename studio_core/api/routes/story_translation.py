from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from studio_core.services.project_route_auth import require_project_path_access

from studio_core.services.story_translation_service import (
    generate_story_translations,
    get_story_translations,
)

router = APIRouter(prefix="/story-translation", tags=["story-translation"])


@router.get("/{project_id}")
def read_translations(project_id: str, _principal=Depends(require_project_path_access)) -> dict:
    try:
        return get_story_translations(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{project_id}/generate")
def generate_translations(project_id: str, payload: dict | None = None, _principal=Depends(require_project_path_access)) -> dict:
    try:
        return generate_story_translations(project_id, payload or {})
    except ValueError as exc:
        status = 404 if str(exc) == "Projeto não encontrado." else 400
        raise HTTPException(status_code=status, detail=str(exc)) from exc
