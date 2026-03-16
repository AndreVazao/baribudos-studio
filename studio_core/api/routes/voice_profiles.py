from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from studio_core.services.voice_profile_service import (
    attach_voice_sample,
    list_voice_profiles,
    set_default_voice_profile,
)

router = APIRouter(prefix="/voice-profiles", tags=["voice-profiles"])


@router.get("/{project_id}")
def get_profiles(project_id: str) -> dict:
    try:
        return {
            "ok": True,
            "profiles": list_voice_profiles(project_id),
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/upload")
async def upload_voice_profile(
    project_id: str = Form(...),
    profile_name: str = Form(""),
    language: str = Form(""),
    is_default: bool = Form(True),
    file: UploadFile = File(...),
) -> dict:
    suffix = Path(file.filename or "voice.wav").suffix or ".wav"

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                tmp.write(chunk)
            tmp_path = tmp.name

        return attach_voice_sample(
            project_id=project_id,
            source_path=tmp_path,
            original_filename=file.filename or "voice.wav",
            profile_name=profile_name,
            language=language,
            is_default=is_default,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/default/{project_id}/{profile_id}")
def set_default(project_id: str, profile_id: str) -> dict:
    try:
        return set_default_voice_profile(project_id, profile_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
