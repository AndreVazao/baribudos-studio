from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.audio_cast_preview_service import generate_audio_cast_preview

router = APIRouter(prefix="/audio-cast-preview", tags=["audio-cast-preview"])


@router.post("/{project_id}")
def preview_audio_cast(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return generate_audio_cast_preview(project_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
