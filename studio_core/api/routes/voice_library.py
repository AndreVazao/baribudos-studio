from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles
from studio_core.services.voice_library_service import add_voice_sample, get_voice_sample, list_voice_samples

def _voice_dto(voice: dict) -> dict:
    return {key: value for key, value in voice.items() if key not in {"file_path", "source_path"}}


MAX_VOICE_UPLOAD_BYTES = 50 * 1024 * 1024
UPLOAD_CHUNK_BYTES = 1024 * 1024

router = APIRouter(
    prefix="/voice-library",
    tags=["voice-library"],
    dependencies=[Depends(require_roles("owner", "admin", "editor", "creator"))],
)


@router.get("")
def list_voices(principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor", "creator"))) -> dict:
    items = list_voice_samples()
    if principal.role.lower() not in {"owner", "admin"}:
        items = [item for item in items if str(item.get("owner_user_id", "")).strip() == principal.user_id]
    return {"ok": True, "voices": [_voice_dto(item) for item in items]}


@router.get("/{voice_id}")
def get_voice(voice_id: str, principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor", "creator"))) -> dict:
    voice = get_voice_sample(voice_id)
    if not voice:
        raise HTTPException(status_code=404, detail="Voice sample não encontrada.")
    if principal.role.lower() not in {"owner", "admin"} and str(voice.get("owner_user_id", "")).strip() != principal.user_id:
        raise HTTPException(status_code=403, detail="Sem acesso a esta amostra de voz.")
    return {"ok": True, "voice": _voice_dto(voice)}


@router.post("/upload")
async def upload_voice(
    name: str = Form(...),
    language: str = Form(""),
    notes: str = Form(""),
    file: UploadFile = File(...),
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor", "creator")),
) -> dict:
    suffix = Path(file.filename or "sample.wav").suffix or ".wav"
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            total_bytes = 0
            while chunk := await file.read(UPLOAD_CHUNK_BYTES):
                total_bytes += len(chunk)
                if total_bytes > MAX_VOICE_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail="Amostra de voz excede o limite de 50 MB.")
                tmp.write(chunk)
        voice = add_voice_sample(
            name=name, language=language, notes=notes, source_path=tmp_path,
            original_filename=file.filename or "sample.wav",
            owner_user_id=principal.user_id,
        )
        return {"ok": True, "voice": _voice_dto(voice)}
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Não foi possível guardar a amostra de voz.") from exc
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)
