from __future__ import annotations

from typing import Any, Dict, List

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item
from studio_core.services.voice_profile_service import get_voice_profile

PROJECTS_FILE = "data/projects.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _get_project(project_id: str) -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        if _safe_text(project.get("id")) == _safe_text(project_id):
            return project
    return None


def get_product_credits(project_id: str) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")
    return _safe_dict(project.get("product_credits", {}))


def _voice_credit_name_from_profile_id(voice_profile_id: str) -> str:
    profile = get_voice_profile(voice_profile_id)
    if not profile:
        return ""
    return _safe_text(profile.get("credited_name")) or _safe_text(profile.get("owner_person_name")) or _safe_text(profile.get("display_name"))


def rebuild_product_credits(project_id: str) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    audio_cast = _safe_dict(project.get("audio_cast", {}))
    narrator = _safe_dict(audio_cast.get("narrator", {}))
    characters = _safe_list(audio_cast.get("characters", []))

    written_by = []
    produced_by = []
    narration_by = []
    voices_by = []
    character_voices_by = []

    owner_name = _safe_text(project.get("created_by_name"))
    if owner_name:
        written_by.append(owner_name)
        produced_by.append(owner_name)

    narrator_credit = _voice_credit_name_from_profile_id(_safe_text(narrator.get("voice_profile_id")))
    if narrator_credit:
        narration_by.append(narrator_credit)
        voices_by.append(narrator_credit)

    for item in characters:
        row = _safe_dict(item)
        char_name = _safe_text(row.get("name"))
        credit_name = _voice_credit_name_from_profile_id(_safe_text(row.get("voice_profile_id")))
        if not credit_name:
            continue
        if credit_name not in voices_by:
            voices_by.append(credit_name)
        character_voices_by.append({
            "character_name": char_name,
            "credited_name": credit_name,
            "voice_profile_id": _safe_text(row.get("voice_profile_id")),
        })

    credits = {
        "created_by": [owner_name] if owner_name else [],
        "written_by": written_by,
        "produced_by": produced_by,
        "voices_by": voices_by,
        "narration_by": narration_by,
        "character_voices_by": character_voices_by,
        "illustrations_by": _safe_list(_safe_dict(project.get("product_credits", {})).get("illustrations_by")),
        "sound_design_by": _safe_list(_safe_dict(project.get("product_credits", {})).get("sound_design_by")),
        "editing_by": _safe_list(_safe_dict(project.get("product_credits", {})).get("editing_by")),
        "special_thanks": _safe_list(_safe_dict(project.get("product_credits", {})).get("special_thanks")),
        "updated_at": now_iso(),
    }

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "product_credits": credits,
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "product_credits": _safe_dict(updated.get("product_credits", {})),
        "project": updated,
    }


def patch_product_credits(project_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    current = _safe_dict(project.get("product_credits", {}))
    merged = {
        **current,
        "created_by": _safe_list(payload.get("created_by", current.get("created_by"))),
        "written_by": _safe_list(payload.get("written_by", current.get("written_by"))),
        "produced_by": _safe_list(payload.get("produced_by", current.get("produced_by"))),
        "voices_by": _safe_list(payload.get("voices_by", current.get("voices_by"))),
        "narration_by": _safe_list(payload.get("narration_by", current.get("narration_by"))),
        "character_voices_by": _safe_list(payload.get("character_voices_by", current.get("character_voices_by"))),
        "illustrations_by": _safe_list(payload.get("illustrations_by", current.get("illustrations_by"))),
        "sound_design_by": _safe_list(payload.get("sound_design_by", current.get("sound_design_by"))),
        "editing_by": _safe_list(payload.get("editing_by", current.get("editing_by"))),
        "special_thanks": _safe_list(payload.get("special_thanks", current.get("special_thanks"))),
        "updated_at": now_iso(),
    }

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda item: {
            **item,
            "product_credits": merged,
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "product_credits": _safe_dict(updated.get("product_credits", {})),
        "project": updated,
    }
