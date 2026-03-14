from __future__ import annotations

from typing import Any, Dict, List

from studio_core.core.models import now_iso
from studio_core.services.ip_runtime_service import load_ip_runtime


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


def _has_value(value: Any) -> bool:
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, dict):
        return len(value) > 0
    return bool(_normalize_str(value))


def _check_required_fields(commercial: Dict[str, Any]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for field in REQUIRED_COMMERCIAL_FIELDS:
        items.append({
            "field": field,
            "required": True,
            "ok": _has_value(commercial.get(field)),
            "value": commercial.get(field),
        })
    return items


def _check_recommended_fields(commercial: Dict[str, Any]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for field in RECOMMENDED_COMMERCIAL_FIELDS:
        items.append({
            "field": field,
            "required": False,
            "ok": _has_value(commercial.get(field)),
            "value": commercial.get(field),
        })
    return items


def _extract_output_presence(outputs: Dict[str, Any]) -> Dict[str, Any]:
    covers = outputs.get("covers")
    epub = outputs.get("epub") or {}
    audiobook = outputs.get("audiobook") or {}
    video = outputs.get("video") or {}
    guide = outputs.get("guide")

    return {
        "covers": bool(covers and covers.get("file_path")),
        "epub": any(bool(item and item.get("file_path")) for item in epub.values()),
        "audiobook": any(bool(item and item.get("file_path")) for item in audiobook.values()),
        "video": any(bool(item and item.get("file_path")) for item in video.values()),
        "guide": bool(guide),
    }


def _build_readiness(required_checks: List[Dict[str, Any]], output_presence: Dict[str, Any]) -> Dict[str, Any]:
    required_fields_ok = all(item["ok"] for item in required_checks)
    required_outputs_ok = all(bool(output_presence.get(name)) for name in REQUIRED_OUTPUT_GROUPS)

    missing_required_fields = [item["field"] for item in required_checks if not item["ok"]]
    missing_required_outputs = [name for name in REQUIRED_OUTPUT_GROUPS if not output_presence.get(name)]

    ready = required_fields_ok and required_outputs_ok

    return {
        "ready": ready,
        "required_fields_ok": required_fields_ok,
        "required_outputs_ok": required_outputs_ok,
        "missing_required_fields": missing_required_fields,
        "missing_required_outputs": missing_required_outputs,
    }


def build_publication_package(project: Dict[str, Any]) -> Dict[str, Any]:
    saga_id = _normalize_str(project.get("saga_slug", "baribudos"))
    runtime = load_ip_runtime(saga_id)
    metadata = runtime.get("metadata", {}) or {}
    commercial = project.get("commercial", {}) or {}
    outputs = project.get("outputs", {}) or {}

    required_checks = _check_required_fields(commercial)
    recommended_checks = _check_recommended_fields(commercial)
    output_presence = _extract_output_presence(outputs)
    readiness = _build_readiness(required_checks, output_presence)

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
            "default_language": runtime.get("default_language", "pt-PT"),
            "output_languages": runtime.get("output_languages", []),
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
        },
        "outputs": outputs,
        "checks": {
            "required_fields": required_checks,
            "recommended_fields": recommended_checks,
            "output_presence": output_presence,
            "readiness": readiness,
        }
}
