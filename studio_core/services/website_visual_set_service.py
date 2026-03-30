from __future__ import annotations

import json
from typing import Any, Dict
from urllib import error, request

from studio_core.core.storage import list_json_items
from studio_core.services.credential_resolver_service import resolve_credential

SAGA_VISUAL_SETS_FILE = "data/saga_visual_sets.json"


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


def export_saga_visual_sets_payload() -> Dict[str, Any]:
    items = list_json_items(SAGA_VISUAL_SETS_FILE)
    return {
        "ok": True,
        "items": items,
        "count": len(items),
    }


def get_website_visual_sets_status() -> Dict[str, Any]:
    return _request_json("GET", "/api/studio/status/visual-sets")
