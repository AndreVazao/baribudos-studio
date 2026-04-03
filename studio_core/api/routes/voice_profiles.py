from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.voice_profile_service import (
    create_voice_profile,
    list_voice_profiles,
    patch_voice_profile,
    validate_voice_profile_usage,
)

router = APIRouter(prefix="/voice-profiles", tags=["voice-profiles"])


@router.get("")
def get_voice_profiles() -> dict:
    return {
        "ok": True,
        "voice_profiles": list_voice_profiles(),
    }


@router.post("")
def post_voice_profile(payload: dict) -> dict:
    try:
        item = create_voice_profile(payload or {})
        return {
            "ok": True,
            "voice_profile": item,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/{voice_profile_id}")
def patch_profile(voice_profile_id: str, payload: dict) -> dict:
    try:
        item = patch_voice_profile(voice_profile_id, payload or {})
        return {
            "ok": True,
            "voice_profile": item,
        }
    except ValueError as exc:
        status = 404 if str(exc) == "voice_profile_not_found" else 400
        raise HTTPException(status_code=status, detail=str(exc)) from exc


@router.get("/{voice_profile_id}/validate")
def validate_profile(voice_profile_id: str, ip_slug: str = "", saga_slug: str = "", role: str = "") -> dict:
    try:
        return validate_voice_profile_usage(voice_profile_id, ip_slug=ip_slug, saga_slug=saga_slug, role=role)
    except ValueError as exc:
        status = 404 if str(exc) == "voice_profile_not_found" else 400
        raise HTTPException(status_code=status, detail=str(exc)) from exc
