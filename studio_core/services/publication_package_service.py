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


def _build_readiness(required_checks: List[Dict[str, Any]], recommended_checks: List[Dict[str, Any]], output_presence: Dict[str, Any]) -> Dict[str, Any]:
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
        "required_outputs_ok":
