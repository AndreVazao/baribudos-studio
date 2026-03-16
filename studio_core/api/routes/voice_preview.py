from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.voice_preview_service import generate_voice_preview

router = APIRouter(prefix="/voice-preview", tags=["voice-preview"])


@router.post("")
def preview_voice(payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return generate_voice_preview(payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
