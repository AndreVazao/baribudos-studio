from __future__ import annotations

import json
import os
from typing import Any, Dict
from urllib import error, parse, request


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _request_json(url: str, api_key: str) -> Dict[str, Any]:
    http_request = request.Request(
        url,
        headers={
            "x-studio-api-key": api_key,
        },
        method="GET",
    )

    try:
        with request.urlopen(http_request, timeout=20) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {"ok": True}
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="ignore")
        raise ValueError(f"website_control_http_error:{exc.code}:{details}") from exc
    except error.URLError as exc:
        raise ValueError(f"website_control_connection_error:{exc.reason}") from exc


def _base_url() -> str:
    value = _normalize_text(os.getenv("BARIBUDOS_WEBSITE_BASE_URL"))
    if not value:
        raise ValueError("website_base_url_missing")
    return value.rstrip("/")


def _api_key() -> str:
    value = _normalize_text(os.getenv("BARIBUDOS_WEBSITE_PUBLISH_API_KEY"))
    if not value:
        raise ValueError("website_publish_api_key_missing")
    return value


def get_website_summary_status() -> Dict[str, Any]:
    url = f"{_base_url()}/api/studio/status/summary"
    return _request_json(url, _api_key())


def get_website_catalog_status(limit: int = 25, active_only: bool = False) -> Dict[str, Any]:
    query = parse.urlencode({
        "limit": max(1, min(int(limit), 100)),
        "active": 1 if active_only else 0,
    })
    url = f"{_base_url()}/api/studio/status/catalog?{query}"
    return _request_json(url, _api_key())
