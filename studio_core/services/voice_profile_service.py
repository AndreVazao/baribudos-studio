from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.models import now_iso
from studio_core.core.storage import append_json_item, list_json_items, update_json_item

VOICE_PROFILES_FILE = "data/voice_profiles.json"

ALLOWED_VOICE_TYPES = {"narrator", "character", "ambient", "promo", "system"}
ALLOWED_SOURCE_TYPES = {"recorded_human", "cloned_voice", "synthetic_hybrid"}
ALLOWED_CONSENT_STATUS = {"pending", "approved", "restricted", "revoked"}
ALLOWED_CREDIT_VISIBILITY = {"internal_only", "product_only", "product_and_website", "all_promotional"}


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _validate_enum(field_name: str, value: str, allowed: set[str]) -> str:
    clean = _normalize_text(value)
    if clean and clean not in allowed:
        raise ValueError(f"{field_name}_invalid")
    return clean


def _normalize_variation_policy(payload: Dict[str, Any], current: Dict[str, Any] | None = None) -> Dict[str, Any]:
    current = current or {}
    source = _safe_dict(payload.get("voice_variation_policy", current.get("voice_variation_policy")))
    return {
        "allow_variants": bool(source.get("allow_variants", True)),
        "pitch_range_min": int(source.get("pitch_range_min", -2) or -2),
        "pitch_range_max": int(source.get("pitch_range_max", 2) or 2),
        "tone_range_min": int(source.get("tone_range_min", -2) or -2),
        "tone_range_max": int(source.get("tone_range_max", 2) or 2),
        "speed_range_min": float(source.get("speed_range_min", 0.9) or 0.9),
        "speed_range_max": float(source.get("speed_range_max", 1.1) or 1.1),
        "variant_notes": _normalize_text(source.get("variant_notes", "")),
    }


def _normalize_profile(payload: Dict[str, Any], current: Dict[str, Any] | None = None) -> Dict[str, Any]:
    current = current or {}
    display_name = _normalize_text(payload.get("display_name", current.get("display_name")))
    if not display_name:
        raise ValueError("display_name_required")

    owner_person_id = _normalize_text(payload.get("owner_person_id", current.get("owner_person_id")))
    owner_person_name = _normalize_text(payload.get("owner_person_name", current.get("owner_person_name")))
    credited_name = _normalize_text(payload.get("credited_name", current.get("credited_name"))) or owner_person_name or display_name
    voice_type = _validate_enum("voice_type", payload.get("voice_type", current.get("voice_type") or "narrator"), ALLOWED_VOICE_TYPES) or "narrator"
    source_type = _validate_enum("source_type", payload.get("source_type", current.get("source_type") or "recorded_human"), ALLOWED_SOURCE_TYPES) or "recorded_human"
    consent_status = _validate_enum("consent_status", payload.get("consent_status", current.get("consent_status") or "pending"), ALLOWED_CONSENT_STATUS) or "pending"
    credit_visibility = _validate_enum("credit_visibility", payload.get("credit_visibility", current.get("credit_visibility") or "product_and_website"), ALLOWED_CREDIT_VISIBILITY) or "product_and_website"

    return {
        "id": _normalize_text(current.get("id")) or f"voice-profile-{uuid4()}",
        "display_name": display_name,
        "owner_person_id": owner_person_id,
        "owner_person_name": owner_person_name,
        "credited_name": credited_name,
        "voice_type": voice_type,
        "source_type": source_type,
        "clone_provider": _normalize_text(payload.get("clone_provider", current.get("clone_provider"))),
        "language": _normalize_text(payload.get("language", current.get("language"))),
        "accent": _normalize_text(payload.get("accent", current.get("accent"))),
        "gender_hint": _normalize_text(payload.get("gender_hint", current.get("gender_hint"))),
        "age_hint": _normalize_text(payload.get("age_hint", current.get("age_hint"))),
        "consent_status": consent_status,
        "credit_visibility": credit_visibility,
        "allowed_ips": _safe_list(payload.get("allowed_ips", current.get("allowed_ips"))),
        "allowed_sagas": _safe_list(payload.get("allowed_sagas", current.get("allowed_sagas"))),
        "allowed_roles": _safe_list(payload.get("allowed_roles", current.get("allowed_roles"))),
        "default_for_roles": _safe_list(payload.get("default_for_roles", current.get("default_for_roles"))),
        "sample_audio_paths": _safe_list(payload.get("sample_audio_paths", current.get("sample_audio_paths"))),
        "reference_text": _normalize_text(payload.get("reference_text", current.get("reference_text"))),
        "notes": _normalize_text(payload.get("notes", current.get("notes"))),
        "voice_variation_policy": _normalize_variation_policy(payload, current),
        "active": bool(payload.get("active", current.get("active", True))),
        "created_at": current.get("created_at") or now_iso(),
        "updated_at": now_iso(),
    }


def list_voice_profiles() -> List[Dict[str, Any]]:
    return list_json_items(VOICE_PROFILES_FILE)


def get_voice_profile(voice_profile_id: str) -> Dict[str, Any] | None:
    clean = _normalize_text(voice_profile_id)
    for item in list_voice_profiles():
        if _normalize_text(item.get("id")) == clean:
            return item
    return None


def create_voice_profile(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = _normalize_profile(payload)
    return append_json_item(VOICE_PROFILES_FILE, normalized)


def patch_voice_profile(voice_profile_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    current = get_voice_profile(voice_profile_id)
    if not current:
        raise ValueError("voice_profile_not_found")
    return update_json_item(VOICE_PROFILES_FILE, current["id"], lambda item: _normalize_profile(payload, item))


def validate_voice_profile_usage(voice_profile_id: str, ip_slug: str = "", saga_slug: str = "", role: str = "") -> Dict[str, Any]:
    item = get_voice_profile(voice_profile_id)
    if not item:
        raise ValueError("voice_profile_not_found")

    allowed_ips = {_normalize_text(v) for v in _safe_list(item.get("allowed_ips")) if _normalize_text(v)}
    allowed_sagas = {_normalize_text(v) for v in _safe_list(item.get("allowed_sagas")) if _normalize_text(v)}
    allowed_roles = {_normalize_text(v) for v in _safe_list(item.get("allowed_roles")) if _normalize_text(v)}

    clean_ip = _normalize_text(ip_slug)
    clean_saga = _normalize_text(saga_slug)
    clean_role = _normalize_text(role)

    ip_ok = not allowed_ips or clean_ip in allowed_ips
    saga_ok = not allowed_sagas or clean_saga in allowed_sagas
    role_ok = not allowed_roles or clean_role in allowed_roles
    consent_ok = _normalize_text(item.get("consent_status")) == "approved"
    active_ok = bool(item.get("active", False))

    return {
        "ok": True,
        "voice_profile_id": item.get("id"),
        "display_name": item.get("display_name"),
        "usable": bool(ip_ok and saga_ok and role_ok and consent_ok and active_ok),
        "checks": {
            "ip_ok": ip_ok,
            "saga_ok": saga_ok,
            "role_ok": role_ok,
            "consent_ok": consent_ok,
            "active_ok": active_ok,
        },
    }
