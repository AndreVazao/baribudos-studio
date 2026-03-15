from __future__ import annotations

from typing import Any, Dict, List

from studio_core.core.models import now_iso
from studio_core.services.saga_runtime_service import load_saga_runtime


REQUIRED_COMMERCIAL_FIELDS = [
    "internal_code",
    "price",
    "currency",
    "commercial_status",
]

RECOMMENDED_COMMERCIAL_FIELDS = [
    "isbn",
    "asin",
    "subtitle",
    "blurb",
]

REQUIRED_OUTPUT_GROUPS = [
    "covers",
    "epub",
]

OPTIONAL_OUTPUT_GROUPS = [
    "audiobook",
    "video",
    "guide",
]


def _normalize_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _has_value(value: Any) -> bool:
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, dict):
        return len(value) > 0
    return bool(_normalize_str(value))


def _check_required_fields(commercial: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            "field": field,
            "required": True,
            "ok": _has_value(commercial.get(field)),
            "value": commercial.get(field),
        }
        for field in REQUIRED_COMMERCIAL_FIELDS
    ]


def _check_recommended_fields(commercial: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            "field": field,
            "required": False,
            "ok": _has_value(commercial.get(field)),
            "value": commercial.get(field),
        }
        for field in RECOMMENDED_COMMERCIAL_FIELDS
    ]


def _extract_output_presence(outputs: Dict[str, Any]) -> Dict[str, Any]:
    covers = _safe_dict(outputs.get("covers", {}))
    epub = _safe_dict(outputs.get("epub", {}))
    audiobook = _safe_dict(outputs.get("audiobook", {}))
    video = _safe_dict(outputs.get("video", {}))
    guide = outputs.get("guide")

    return {
        "covers": bool(covers and covers.get("file_path")),
        "epub": any(bool(_safe_dict(item).get("file_path")) for item in epub.values()),
        "audiobook": any(bool(_safe_dict(item).get("file_path")) for item in audiobook.values()),
        "video": any(bool(_safe_dict(item).get("file_path")) for item in video.values()),
        "guide": bool(guide),
    }


def _build_readiness(
    required_checks: List[Dict[str, Any]],
    recommended_checks: List[Dict[str, Any]],
    output_presence: Dict[str, Any],
) -> Dict[str, Any]:
    required_fields_ok = all(item["ok"] for item in required_checks)
    required_outputs_ok = all(bool(output_presence.get(name)) for name in REQUIRED_OUTPUT_GROUPS)

    missing_required_fields = [item["field"] for item in required_checks if not item["ok"]]
    missing_required_outputs = [name for name in REQUIRED_OUTPUT_GROUPS if not output_presence.get(name)]
    missing_recommended_fields = [item["field"] for item in recommended_checks if not item["ok"]]

    required_ok = required_fields_ok and required_outputs_ok
    recommended_ok = len(missing_recommended_fields) == 0

    if required_ok and recommended_ok:
        status = "green"
        label = "Pronto para publicar"
    elif required_ok:
        status = "yellow"
        label = "Quase pronto"
    else:
        status = "red"
        label = "Não pronto"

    score = 0
    total = len(required_checks) + len(recommended_checks) + len(REQUIRED_OUTPUT_GROUPS) + len(OPTIONAL_OUTPUT_GROUPS)

    for item in required_checks:
        if item["ok"]:
            score += 1
    for item in recommended_checks:
        if item["ok"]:
            score += 1
    for name in REQUIRED_OUTPUT_GROUPS:
        if output_presence.get(name):
            score += 1
    for name in OPTIONAL_OUTPUT_GROUPS:
        if output_presence.get(name):
            score += 1

    percent = round((score / total) * 100) if total else 0

    return {
        "ready": status == "green",
        "status": status,
        "label": label,
        "score_percent": percent,
        "required_fields_ok": required_fields_ok,
        "required_outputs_ok": required_outputs_ok,
        "missing_required_fields": missing_required_fields,
        "missing_required_outputs": missing_required_outputs,
        "missing_recommended_fields": missing_recommended_fields,
    }


def build_publication_package(project: Dict[str, Any]) -> Dict[str, Any]:
    saga_id = _normalize_str(project.get("saga_slug", "baribudos")) or "baribudos"
    runtime = load_saga_runtime(saga_id)
    metadata = _safe_dict(runtime.get("metadata", {}))
    resolved = _safe_dict(runtime.get("resolved", {}))
    commercial = _safe_dict(project.get("commercial", {}))
    outputs = _safe_dict(project.get("outputs", {}))

    required_checks = _check_required_fields(commercial)
    recommended_checks = _check_recommended_fields(commercial)
    output_presence = _extract_output_presence(outputs)
    readiness = _build_readiness(required_checks, recommended_checks, output_presence)

    return {
        "generated_at": now_iso(),
        "project": {
            "id": project.get("id"),
            "title": project.get("title"),
            "language": project.get("language"),
            "output_languages": project.get("output_languages", []),
            "saga_slug": project.get("saga_slug"),
            "saga_name": project.get("saga_name"),
            "created_by": project.get("created_by"),
            "created_by_name": project.get("created_by_name"),
            "status": project.get("status"),
            "editorial_status": project.get("editorial_status"),
            "ready_for_publish": bool(project.get("ready_for_publish", False)),
        },
        "runtime": {
            "slug": runtime.get("slug", ""),
            "name": runtime.get("name", ""),
            "default_language": runtime.get("default_language", "pt-PT"),
            "output_languages": runtime.get("output_languages", []),
            "validation": runtime.get("validation", {}),
        },
        "editorial": {
            "author_default": metadata.get("author_default", ""),
            "producer": metadata.get("producer", ""),
            "tagline": metadata.get("tagline", ""),
            "mission": metadata.get("mission", ""),
            "target_age": metadata.get("target_age", ""),
            "series_name": metadata.get("series_name", ""),
            "genre": metadata.get("genre", ""),
            "description": metadata.get("description", ""),
            "resolved_series_name": resolved.get("series_name", ""),
            "resolved_final_phrase": resolved.get("final_phrase_rule", ""),
        },
        "commercial": {
            "internal_code": commercial.get("internal_code", ""),
            "isbn": commercial.get("isbn", ""),
            "asin": commercial.get("asin", ""),
            "price": commercial.get("price", ""),
            "currency": commercial.get("currency", "EUR"),
            "collection_seal": commercial.get("collection_seal", ""),
            "marketplaces": commercial.get("marketplaces", []),
            "commercial_status": commercial.get("commercial_status", "draft"),
            "channels": commercial.get("channels", []),
            "keywords": commercial.get("keywords", []),
            "subtitle": commercial.get("subtitle", ""),
            "blurb": commercial.get("blurb", ""),
        },
        "assets": {
            "cover_image": project.get("cover_image", ""),
            "illustration_path": project.get("illustration_path", ""),
            "brand_assets": runtime.get("brand_assets", {}),
            "palette": runtime.get("palette", {}),
        },
        "outputs": outputs,
        "checks": {
            "required_fields": required_checks,
            "recommended_fields": recommended_checks,
            "output_presence": output_presence,
            "readiness": readiness,
        },
        }
