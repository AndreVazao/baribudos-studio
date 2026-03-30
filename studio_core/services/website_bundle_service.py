from __future__ import annotations

import json
from typing import Any, Dict
from urllib import error, request

from studio_core.core.storage import list_json_items
from studio_core.services.commerce_group_service import mark_commerce_group_publish_state
from studio_core.services.credential_resolver_service import resolve_credential

COMMERCE_GROUPS_FILE = "data/commerce_groups.json"


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_list(value: Any):
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
        raise ValueError(f"website_bundle_http_error:{exc.code}:{details}") from exc
    except error.URLError as exc:
        raise ValueError(f"website_bundle_connection_error:{exc.reason}") from exc


def _load_group(group_id: str) -> Dict[str, Any] | None:
    for group in list_json_items(COMMERCE_GROUPS_FILE):
        if str(group.get("id", "")) == str(group_id):
            return group
    return None


def publish_commerce_group_to_website(group_id: str) -> Dict[str, Any]:
    group = _load_group(group_id)
    if not group:
        raise ValueError("commerce_group_not_found")

    payload = {
        "group_id": group.get("id"),
        "slug": group.get("slug"),
        "name": group.get("name"),
        "description": group.get("description"),
        "group_type": group.get("group_type") or "bundle",
        "currency": group.get("currency") or "EUR",
        "price_cents": int(group.get("price_cents") or 0),
        "active": bool(group.get("active", False)),
        "featured": bool(group.get("featured", False)),
        "items": [
            {
                "product_id": item.get("product_id"),
                "slug": item.get("slug"),
                "title": item.get("title"),
                "type": item.get("type"),
                "currency": item.get("currency") or "EUR",
                "price_cents": int(item.get("price_cents") or 0),
                "position": int(item.get("position") or index),
            }
            for index, item in enumerate(_safe_list(group.get("items")))
        ],
      }

    result = _request_json("POST", "/api/studio/admin/bundles/upsert", payload)
    mark_commerce_group_publish_state(group_id, result)
    return {
        "ok": True,
        "group_id": group_id,
        "website": result,
    }


def get_website_bundles_status(limit: int = 20) -> Dict[str, Any]:
    return _request_json("GET", f"/api/studio/status/bundles?limit={max(1, min(int(limit), 100))}")
