from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from studio_core.services.auth_principal import require_roles
from studio_core.services.illustration_pipeline_service import (
    get_project_illustration_pipeline, list_illustration_runs, setup_illustration_pipeline, update_illustration_frame_status,
)
from studio_core.services.project_route_auth import require_project_path_access

router = APIRouter(prefix="/illustration-pipeline", tags=["illustration-pipeline"])


@router.get("", dependencies=[Depends(require_roles("owner", "admin"))])
def get_runs() -> dict:
    return {"ok": True, "runs": list_illustration_runs()}


@router.get("/{project_id}")
def get_pipeline(project_id: str, _principal=Depends(require_project_path_access)) -> dict:
    try:
        return {"ok": True, "pipeline": get_project_illustration_pipeline(project_id)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Não foi possível carregar o pipeline de ilustração.") from exc


@router.post("/setup/{project_id}")
def setup_pipeline(project_id: str, payload: dict | None = None, _principal=Depends(require_project_path_access)) -> dict:
    try:
        return setup_illustration_pipeline(project_id, payload or {})
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Não foi possível configurar o pipeline de ilustração.") from exc


@router.post("/{project_id}/frame/{frame_id}")
def update_frame(project_id: str, frame_id: str, payload: dict | None = None, _principal=Depends(require_project_path_access)) -> dict:
    body = payload or {}
    try:
        return update_illustration_frame_status(
            project_id, frame_id, status=body.get("status"), approved=body.get("approved"),
            image_path=body.get("image_path"), uploaded_manually=body.get("uploaded_manually"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Não foi possível atualizar o frame.") from exc
