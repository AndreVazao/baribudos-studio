from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from studio_core.services.auth_principal import require_roles
from studio_core.services.voice_preview_service import generate_voice_preview

router = APIRouter(
    prefix="/voice-preview",
    tags=["voice-preview"],
    dependencies=[Depends(require_roles("owner", "admin", "editor", "creator"))],
)


@router.post("")
def preview_voice(payload: dict | None = None) -> dict:
    try:
        return generate_voice_preview(payload or {})
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Não foi possível gerar a pré-visualização de voz.") from exc
