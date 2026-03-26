from __future__ import annotations

import json
from typing import Any, Dict
from urllib import error, parse, request

from studio_core.services.credential_resolver_service import resolve_credential


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _base_url() -> str:
    value = resolve_credential("BARIBUDOS_WEBSITE_BASE_URL", target="website")
    if not value:
        raise ValueError("website_base_url_missing")
    return value.rstrip("/")


def _studio_key() -> str:
    value = resolve_credential("BARIBUDOS_WEBSITE_PUBLISH_API_KEY", target="website")
    if not value:
        raise ValueError("website_publish_api_key_missing")
    return value


def _request_json(method: str, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    url = f"{_base_url()}{path}"
    http_request = request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-studio-api-key": _studio_key(),
        },
        method=method,
    )

    try:
        with request.urlopen(http_request, timeout=20) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {"ok": True}
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="ignore")
        raise ValueError(f"website_admin_http_error:{exc.code}:{details}") from exc
    except error.URLError as exc:
        raise ValueError(f"website_admin_connection_error:{exc.reason}") from exc


def update_website_product_visibility(product_id: str, active: bool | None = None, featured: bool | None = None) -> Dict[str, Any]:
    product_value = _normalize_text(product_id)
    if not product_value:
        raise ValueError("product_id_missing")

    payload: Dict[str, Any] = {}
    if active is not None:
        payload["active"] = bool(active)
    if featured is not None:
        payload["featured"] = bool(featured)
    if not payload:
        raise ValueError("visibility_payload_missing")

    encoded = parse.quote(product_value, safe="")
    return _request_json("PATCH", f"/api/studio/admin/products/{encoded}/visibility", payload)


def update_website_product_pricing(product_id: str, price_cents: int, currency: str = "EUR") -> Dict[str, Any]:
    product_value = _normalize_text(product_id)
    if not product_value:
        raise ValueError("product_id_missing")
    if int(price_cents) < 0:
        raise ValueError("invalid_price_cents")

    payload = {
        "price_cents": int(price_cents),
        "currency": _normalize_text(currency).upper() or "EUR",
    }
    encoded = parse.quote(product_value, safe="")
    return _request_json("PATCH", f"/api/studio/admin/products/{encoded}/pricing", payload)
