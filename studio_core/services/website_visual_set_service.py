from __future__ import annotations

import json
from typing import Any, Dict, List
from urllib import error, request

from studio_core.core.storage import list_json_items
from studio_core.services.credential_resolver_service import resolve_credential

SAGA_VISUAL_SETS_FILE = "data/saga_visual_sets.json"


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _base_url() -> str:
    value = resolve_credential("BARIBUDOS_WEBSITE_BASE_URL", target="website")
    if not value:
        raise ValueError("website_base_url_missing")
    return value.rstrip("/")


def _api_key() -> str:
    value = resolve_credential("BARIBUDOS_WEBSITE_PUBLISH_API_KEY", target="website")
    if not value:
        raise ValueError("website_publish_api_key_missing")
    return value


def _request_json(method: str, path: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    body = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8") if payload is not None else None
    http_request = request.Request(
        f"{_base_url()}{path}",
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-studio-api-key": _api_key(),
        },
        method=method,
    )
    try:
        with request.urlopen(http_request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {"ok": True}
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="ignore")
        raise ValueError(f"website_visual_sets_http_error:{exc.code}:{details}") from exc
    except error.URLError as exc:
        raise ValueError(f"website_visual_sets_connection_error:{exc.reason}") from exc


def _load_visual_set(item_id: str) -> Dict[str, Any] | None:
    for item in list_json_items(SAGA_VISUAL_SETS_FILE):
        if _normalize_text(item.get("id")) == _normalize_text(item_id):
            return item
    return None


def export_saga_visual_sets_payload() -> Dict[str, Any]:
    items = list_json_items(SAGA_VISUAL_SETS_FILE)
    return {
        "ok": True,
        "items": items,
        "count": len(items),
    }


def get_website_visual_sets_status() -> Dict[str, Any]:
    return _request_json("GET", "/api/studio/status/visual-sets")


def publish_saga_visual_set_to_website(item_id: str) -> Dict[str, Any]:
    item = _load_visual_set(item_id)
    if not item:
        raise ValueError("saga_visual_set_not_found")

    payload = {
        "id": item.get("id"),
        "saga_slug": item.get("saga_slug"),
        "display_name": item.get("display_name"),
        "active": bool(item.get("active", False)),
        "version": int(item.get("version") or 1),
        "source_of_truth": _normalize_text(item.get("source_of_truth")) or "studio",
        "slots": item.get("slots") if isinstance(item.get("slots"), dict) else {},
        "rotation_policy": item.get("rotation_policy") if isinstance(item.get("rotation_policy"), dict) else {},
    }

    result = _request_json("POST", "/api/studio/admin/visual-sets/upsert", payload)
    return {
        "ok": True,
        "item_id": _normalize_text(item.get("id")),
        "website": result,
    }


def publish_all_saga_visual_sets_to_website() -> Dict[str, Any]:
    items = _safe_list(list_json_items(SAGA_VISUAL_SETS_FILE))
    results = [publish_saga_visual_set_to_website(_normalize_text(item.get("id"))) for item in items if _normalize_text(item.get("id"))]
    return {
        "ok": True,
        "count": len(results),
        "results": results,
    }
