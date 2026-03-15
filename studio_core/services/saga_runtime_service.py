from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from studio_core.core.config import resolve_project_path
from studio_core.services.ip_creator_service import get_ip_by_slug


CANON_FILE_MAP = {
    "visual": "visual-canon.json",
    "narrative": "narrative-canon.json",
    "episode": "episode-canon.json",
    "series_arc": "series-arc-canon.json",
    "pedagogical": "pedagogical-canon.json",
    "age_badge": "age-badge-canon.json",
    "characters": "characters-master.json",
}


def _safe_slug(value: str) -> str:
    text = str(value or "").strip().lower()
    cleaned = []
    previous_dash = False

    for ch in text:
        if ch.isalnum():
            cleaned.append(ch)
            previous_dash = False
        else:
            if not previous_dash:
                cleaned.append("-")
                previous_dash = True

    result = "".join(cleaned).strip("-")
    return result or "baribudos"


def _read_json_file(path: Path, default: Any) -> Any:
    if not path.exists() or not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _normalize_list_of_strings(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    result: List[str] = []
    for item in value:
        text = str(item or "").strip()
        if text:
            result.append(text)
    return result


def _normalize_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _resolve_saga_root(slug: str) -> Path:
    return resolve_project_path("studio", "sagas", slug)


def _resolve_public_asset(path_value: str) -> str:
    raw = str(path_value or "").strip()
    if not raw:
        return ""

    if raw.startswith("public/"):
        target = resolve_project_path(raw)
    else:
        target = resolve_project_path("public", raw.lstrip("/"))

    return str(target) if target.exists() else ""


def _normalize_palette(value: Any) -> Dict[str, str]:
    source = _normalize_dict(value)
    return {
        "primary": str(source.get("primary", "#2F5E2E")).strip() or "#2F5E2E",
        "secondary": str(source.get("secondary", "#6FA86A")).strip() or "#6FA86A",
        "accent": str(source.get("accent", source.get("gold", "#D4A73C"))).strip() or "#D4A73C",
        "background": str(source.get("background", source.get("cream", "#F5EED6"))).strip() or "#F5EED6",
        "character_base": str(source.get("character_base", source.get("brown", "#8B5E3C"))).strip() or "#8B5E3C",
    }


def _normalize_brand_assets(value: Any) -> Dict[str, str]:
    source = _normalize_dict(value)
    return {
        "studio_logo": _resolve_public_asset(source.get("studio_logo", "")),
        "series_logo": _resolve_public_asset(source.get("series_logo", "")),
        "seal_logo": _resolve_public_asset(source.get("seal_logo", "")),
    }


def _normalize_metadata(value: Any, fallback_name: str) -> Dict[str, str]:
    source = _normalize_dict(value)
    return {
        "author_default": str(source.get("author_default", "")).strip(),
        "producer": str(source.get("producer", "")).strip(),
        "tagline": str(source.get("tagline", "")).strip(),
        "mission": str(source.get("mission", "")).strip(),
        "target_age": str(source.get("target_age", "")).strip(),
        "series_name": str(source.get("series_name", fallback_name)).strip() or fallback_name,
        "genre": str(source.get("genre", "")).strip(),
        "description": str(source.get("description", "")).strip(),
    }


def _normalize_main_characters(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []

    normalized: List[Dict[str, Any]] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        normalized.append({
            "id": str(item.get("id", f"char-{index}")).strip() or f"char-{index}",
            "name": name,
            "role": str(item.get("role", "")).strip(),
            "description": str(item.get("description", "")).strip(),
            "color": str(item.get("color", "")).strip(),
        })
    return normalized


def _normalize_characters_master(value: Any) -> Dict[str, Any]:
    source = _normalize_dict(value)
    family = source.get("family", [])
    if not isinstance(family, list):
        family = []

    normalized_family: List[Dict[str, Any]] = []
    for index, item in enumerate(family, start=1):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        normalized_family.append({
            "id": str(item.get("id", f"family-{index}")).strip() or f"family-{index}",
            "name": name,
            "role": str(item.get("role", "")).strip(),
            "age": str(item.get("age", "")).strip(),
            "traits": item.get("traits", []) if isinstance(item.get("traits"), list) else [],
            "description": str(item.get("description", "")).strip(),
        })

    return {
        "visual_dna": _normalize_dict(source.get("visual_dna", {})),
        "family": normalized_family,
    }


def _normalize_canons(raw_canons: Dict[str, Any]) -> Dict[str, Any]:
    visual = _normalize_dict(raw_canons.get("visual", {}))
    narrative = _normalize_dict(raw_canons.get("narrative", {}))
    episode = _normalize_dict(raw_canons.get("episode", {}))
    series_arc = _normalize_dict(raw_canons.get("series_arc", {}))
    pedagogical = _normalize_dict(raw_canons.get("pedagogical", {}))
    age_badge = _normalize_dict(raw_canons.get("age_badge", {}))
    characters = _normalize_characters_master(raw_canons.get("characters", {}))

    if "narrative_structure_standard" not in narrative:
        narrative["narrative_structure_standard"] = [
            "simple_introduction",
            "strange_element_or_problem",
            "emotional_questioning",
            "gentle_guidance_or_reflection",
            "progressive_transformation",
            "implicit_moral",
            "final_strong_sentence",
        ]

    if "final_phrase_rule" not in narrative:
        narrative["final_phrase_rule"] = "Na dúvida, escolhe o caminho seguro."

    if "approved_values" not in pedagogical:
        pedagogical["approved_values"] = []

    if "design_rules" not in age_badge:
        age_badge["design_rules"] = {}

    return {
        "visual": visual,
        "narrative": narrative,
        "episode": episode,
        "series_arc": series_arc,
        "pedagogical": pedagogical,
        "age_badge": age_badge,
        "characters": characters,
    }


def _load_raw_canons(slug: str) -> Dict[str, Any]:
    saga_root = _resolve_saga_root(slug)
    return {
        canon_key: _read_json_file(saga_root / file_name, {})
        for canon_key, file_name in CANON_FILE_MAP.items()
    }


def _build_permissions(ip_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "exclusive": bool(ip_data.get("exclusive", False)),
        "visible_to_owner_only": bool(ip_data.get("visible_to_owner_only", False)),
        "editable_by_roles": _normalize_list_of_strings(ip_data.get("editable_by_roles", [])),
        "publishable_by_roles": _normalize_list_of_strings(ip_data.get("publishable_by_roles", [])),
        "allowed_editor_user_ids": _normalize_list_of_strings(ip_data.get("allowed_editor_user_ids", [])),
        "allowed_editor_names": _normalize_list_of_strings(ip_data.get("allowed_editor_names", [])),
        "cloneable": bool(ip_data.get("cloneable", True)),
        "status": str(ip_data.get("status", "draft")).strip() or "draft",
    }


def load_saga_runtime(slug: str) -> Dict[str, Any]:
    saga_slug = _safe_slug(slug)
    ip_data = get_ip_by_slug(saga_slug)
    if not ip_data:
        raise FileNotFoundError(f"Saga/IP não encontrada: {saga_slug}")

    fallback_name = str(ip_data.get("name", saga_slug)).strip() or saga_slug
    raw_canons = _load_raw_canons(saga_slug)
    canons = _normalize_canons(raw_canons)

    runtime = {
        "id": str(ip_data.get("id", "")).strip(),
        "slug": saga_slug,
        "name": fallback_name,
        "owner_id": str(ip_data.get("owner_id", "")).strip(),
        "owner_name": str(ip_data.get("owner_name", "")).strip(),
        "default_language": str(ip_data.get("default_language", "pt-PT")).strip() or "pt-PT",
        "output_languages": _normalize_list_of_strings(ip_data.get("output_languages", [])) or ["pt-PT"],
        "metadata": _normalize_metadata(ip_data.get("metadata", {}), fallback_name),
        "palette": _normalize_palette(ip_data.get("palette", {})),
        "brand_assets": _normalize_brand_assets(ip_data.get("brand_assets", {})),
        "main_characters": _normalize_main_characters(ip_data.get("main_characters", [])),
        "permissions": _build_permissions(ip_data),
        "root_path": str(_resolve_saga_root(saga_slug)),
        "canons": canons,
    }

    runtime["resolved"] = build_saga_runtime_profile(runtime)
    runtime["validation"] = validate_saga_runtime(runtime)
    return runtime


def build_saga_runtime_profile(runtime: Dict[str, Any]) -> Dict[str, Any]:
    metadata = _normalize_dict(runtime.get("metadata", {}))
    canons = _normalize_dict(runtime.get("canons", {}))
    narrative = _normalize_dict(canons.get("narrative", {}))
    pedagogical = _normalize_dict(canons.get("pedagogical", {}))
    visual = _normalize_dict(canons.get("visual", {}))
    characters = _normalize_dict(canons.get("characters", {}))

    approved_values = pedagogical.get("approved_values", [])
    if not isinstance(approved_values, list):
        approved_values = []

    family = characters.get("family", [])
    if not isinstance(family, list):
        family = []

    return {
        "series_name": str(metadata.get("series_name", runtime.get("name", ""))).strip() or str(runtime.get("name", "")),
        "author_default": str(metadata.get("author_default", "")).strip(),
        "producer": str(metadata.get("producer", "")).strip(),
        "tagline": str(metadata.get("tagline", "")).strip(),
        "mission": str(metadata.get("mission", "")).strip(),
        "target_age": str(metadata.get("target_age", "")).strip(),
        "genre": str(metadata.get("genre", "")).strip(),
        "description": str(metadata.get("description", "")).strip(),
        "narrative_structure_standard": narrative.get("narrative_structure_standard", []),
        "final_phrase_rule": narrative.get("final_phrase_rule", "Na dúvida, escolhe o caminho seguro."),
        "approved_values": approved_values,
        "visual_dna": characters.get("visual_dna", {}),
        "family": family,
        "cover_rules": visual.get("cover_rules", {}),
        "environment_rules": visual.get("environment_rules", {}),
        "illustration_rules": visual.get("illustration_rules", {}),
        "emotional_tone": visual.get("emotional_tone", []),
    }


def validate_saga_runtime(runtime: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    slug = str(runtime.get("slug", "")).strip()
    name = str(runtime.get("name", "")).strip()
    metadata = _normalize_dict(runtime.get("metadata", {}))
    palette = _normalize_dict(runtime.get("palette", {}))
    canons = _normalize_dict(runtime.get("canons", {}))
    resolved = _normalize_dict(runtime.get("resolved", {}))

    if not slug:
        errors.append("slug em falta")
    if not name:
        errors.append("name em falta")

    if not metadata.get("series_name"):
        warnings.append("metadata.series_name em falta")
    if not metadata.get("producer"):
        warnings.append("metadata.producer em falta")
    if not metadata.get("author_default"):
        warnings.append("metadata.author_default em falta")
    if not metadata.get("target_age"):
        warnings.append("metadata.target_age em falta")

    for color_key in ["primary", "secondary", "accent", "background", "character_base"]:
        value = str(palette.get(color_key, "")).strip()
        if not value:
            warnings.append(f"palette.{color_key} em falta")

    if not _normalize_dict(canons.get("narrative", {})):
        warnings.append("narrative-canon vazio ou em falta")

    if not _normalize_dict(canons.get("visual", {})):
        warnings.append("visual-canon vazio ou em falta")

    if not resolved.get("narrative_structure_standard"):
        warnings.append("resolved.narrative_structure_standard vazio")

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
}
