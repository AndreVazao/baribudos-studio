from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.audio_cast_service import (
    get_audio_cast,
    list_project_character_names,
    save_audio_cast,
)

router = APIRouter(prefix="/audio-cast", tags=["audio-cast"])


@router.get("/{project_id}")
def get_cast(project_id: str) -> dict:
    try:
        return {
            "ok": True,
            "audio_cast": get_audio_cast(project_id),
            "character_names": list_project_character_names(project_id),
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{project_id}")
def save_cast(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return save_audio_cast(project_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
