from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from studio_core.services.auth_principal import require_roles
from studio_core.services.voice_library_service import add_voice_sample, get_voice_sample, list_voice_samples

router = APIRouter(
    prefix="/voice-library",
    tags=["voice-library"],
    dependencies=[Depends(require_roles("owner", "admin", "editor", "creator"))],
)


@router.get("")
def list_voices() -> dict:
    return {"ok": True, "voices": list_voice_samples()}


@router.get("/{voice_id}")
def get_voice(voice_id: str) -> dict:
    voice = get_voice_sample(voice_id)
    if not voice:
        raise HTTPException(status_code=404, detail="Voice sample não encontrada.")
    return {"ok": True, "voice": voice}


@router.post("/upload")
async def upload_voice(
    name: str = Form(...),
    language: str = Form(""),
    notes: str = Form(""),
    file: UploadFile = File(...),
) -> dict:
    suffix = Path(file.filename or "sample.wav").suffix or ".wav"
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            while chunk := await file.read(1024 * 1024):
                tmp.write(chunk)
            tmp_path = tmp.name
        voice = add_voice_sample(
            name=name, language=language, notes=notes, source_path=tmp_path,
            original_filename=file.filename or "sample.wav",
        )
        return {"ok": True, "voice": voice}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Não foi possível guardar a amostra de voz.") from exc
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)
