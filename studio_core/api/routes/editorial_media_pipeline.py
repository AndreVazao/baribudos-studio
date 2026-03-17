from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.editorial_media_pipeline_service import (
    build_video_package_from_storyboard,
    generate_editorial_illustrations,
)

router = APIRouter(prefix="/editorial-media", tags=["editorial-media"])


@router.post("/generate-illustrations/{project_id}")
def generate_illustrations(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return generate_editorial_illustrations(
            project_id=project_id,
            provider=str(payload.get("provider", "")).strip(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/build-video-package/{project_id}")
def build_video_package(project_id: str) -> dict:
    try:
        return build_video_package_from_storyboard(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
