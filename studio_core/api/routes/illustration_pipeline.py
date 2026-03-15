from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.illustration_pipeline_service import (
    get_project_illustration_pipeline,
    list_illustration_runs,
    setup_illustration_pipeline,
    update_illustration_frame_status,
)

router = APIRouter(prefix="/illustration-pipeline", tags=["illustration-pipeline"])


@router.get("")
def get_runs() -> dict:
    return {
        "ok": True,
        "runs": list_illustration_runs(),
    }


@router.get("/{project_id}")
def get_pipeline(project_id: str) -> dict:
    try:
        return {
            "ok": True,
            "pipeline": get_project_illustration_pipeline(project_id),
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/setup/{project_id}")
def setup_pipeline(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return setup_illustration_pipeline(project_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{project_id}/frame/{frame_id}")
def update_frame(project_id: str, frame_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return update_illustration_frame_status(
            project_id,
            frame_id,
            status=payload.get("status"),
            approved=payload.get("approved"),
            image_path=payload.get("image_path"),
            uploaded_manually=payload.get("uploaded_manually"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
