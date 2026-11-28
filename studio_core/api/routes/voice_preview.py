from __future__ import annotations

import json
import time
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from studio_core.core.config import resolve_storage_path

from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles
from studio_core.services.voice_library_service import get_voice_sample
from studio_core.services.voice_preview_service import generate_voice_preview

VOICE_PREVIEW_TTL_SECONDS = 900


def _read_preview_metadata(preview_id: str) -> dict | None:
    try:
        path = resolve_storage_path("voice_previews", f"voice_preview_{preview_id}.json")
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, ValueError, TypeError):
        return None


def _voice_dto(voice: dict | None):
    if not isinstance(voice, dict):
        return None
    return {key: value for key, value in voice.items() if key not in {"file_path", "source_path"}}


router = APIRouter(
    prefix="/voice-preview",
    tags=["voice-preview"],
    dependencies=[Depends(require_roles("owner", "admin", "editor", "creator"))],
)


@router.post("")
def preview_voice(
    payload: dict | None = None,
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor", "creator")),
) -> dict:
    safe_payload = payload or {}
    voice_sample_id = str(safe_payload.get("voice_sample_id", "")).strip()
    if voice_sample_id:
        sample = get_voice_sample(voice_sample_id)
        if not sample:
            raise HTTPException(status_code=404, detail="Voice sample não encontrada.")
        if principal.role.lower() not in {"owner", "admin"} and str(sample.get("owner_user_id", "")).strip() != principal.user_id:
            raise HTTPException(status_code=403, detail="Sem consentimento ou acesso a esta amostra de voz.")

    try:
        result = generate_voice_preview(safe_payload, owner_user_id=principal.user_id)
        result["voice_sample"] = _voice_dto(result.get("voice_sample"))
        preview = result.get("preview")
        if isinstance(preview, dict):
            result["preview"] = {key: value for key, value in preview.items() if key not in {"speaker_wav", "file_path", "source_path"}}
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Não foi possível gerar a pré-visualização de voz.") from exc



@router.get("/{preview_id}/file")
def get_voice_preview_file(
    preview_id: str,
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor", "creator")),
) -> FileResponse:
    try:
        normalized_id = str(UUID(preview_id))
        file_path = resolve_storage_path("voice_previews", f"voice_preview_{normalized_id}.wav")
    except (ValueError, OSError):
        raise HTTPException(status_code=404, detail="Preview não encontrado.") from None

    metadata = _read_preview_metadata(normalized_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Preview não encontrado.")
    try:
        age_seconds = time.time() - float(metadata.get("created_at", 0))
    except (TypeError, ValueError):
        age_seconds = VOICE_PREVIEW_TTL_SECONDS + 1
    if age_seconds < 0 or age_seconds > VOICE_PREVIEW_TTL_SECONDS:
        raise HTTPException(status_code=404, detail="Preview expirado.")
    if principal.role.lower() not in {"owner", "admin"} and str(metadata.get("owner_user_id", "")) != principal.user_id:
        raise HTTPException(status_code=404, detail="Preview não encontrado.")

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Preview não encontrado.")

    return FileResponse(
        file_path,
        media_type="audio/wav",
        headers={
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
            "Content-Disposition": "inline; filename=\"voice-preview.wav\"",
        },
    )
