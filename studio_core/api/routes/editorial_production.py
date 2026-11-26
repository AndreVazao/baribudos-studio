from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from studio_core.services.editorial_production_bridge_service import (
    build_illustration_queue_from_editorial,
    build_story_from_editorial,
    build_storyboard_from_editorial,
)
from studio_core.services.auth_principal import require_roles
from studio_core.services.project_route_auth import require_project_path_access

router = APIRouter(prefix="/editorial-production", dependencies=[Depends(require_roles("owner", "admin", "editor"))], tags=["editorial-production"])


@router.post("/story/{project_id}")
def editorial_to_story(project_id: str, payload: dict | None = None, _principal=Depends(require_project_path_access)) -> dict:
    payload = payload or {}
    try:
        return build_story_from_editorial(project_id, str(payload.get("language", "")).strip())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/illustrations/{project_id}")
def editorial_to_illustrations(project_id: str, _principal=Depends(require_project_path_access)) -> dict:
    try:
        return build_illustration_queue_from_editorial(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/storyboard/{project_id}")
def editorial_to_storyboard(project_id: str, _principal=Depends(require_project_path_access)) -> dict:
    try:
        return build_storyboard_from_editorial(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
