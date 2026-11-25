from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from studio_core.services.audio_cast_preview_service import generate_audio_cast_preview
from studio_core.services.project_route_auth import require_project_path_access

router = APIRouter(prefix="/audio-cast-preview", tags=["audio-cast-preview"])


@router.post("/{project_id}")
def preview_audio_cast(project_id: str, payload: dict | None = None, _principal=Depends(require_project_path_access)) -> dict:
    try:
        return generate_audio_cast_preview(project_id, payload or {})
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Não foi possível gerar a pré-visualização do elenco.") from exc
