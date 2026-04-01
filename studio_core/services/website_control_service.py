from __future__ import annotations

import json
from typing import Any, Dict
from urllib import error, parse, request

from studio_core.services.credential_resolver_service import resolve_credential


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _request_json(url: str, api_key: str, method: str = "GET") -> Dict[str, Any]:
    http_request = request.Request(
        url,
        headers={
            "x-studio-api-key": api_key,
        },
        method=method,
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
    value = resolve_credential("BARIBUDOS_WEBSITE_BASE_URL", target="website")
    if not value:
        raise ValueError("website_base_url_missing")
    return value.rstrip("/")


def _api_key() -> str:
    value = resolve_credential("BARIBUDOS_WEBSITE_PUBLISH_API_KEY", target="website")
    if not value:
        raise ValueError("website_publish_api_key_missing")
    return value


def get_website_health_status() -> Dict[str, Any]:
    url = f"{_base_url()}/api/studio/status/health"
    return _request_json(url, _api_key())


def get_website_summary_status() -> Dict[str, Any]:
    url = f"{_base_url()}/api/studio/summary"
    return _request_json(url, _api_key())


def get_website_catalog_status(limit: int = 25, active_only: bool = False) -> Dict[str, Any]:
    query = parse.urlencode({
        "limit": max(1, min(int(limit), 100)),
        "active": 1 if active_only else 0,
    })
    url = f"{_base_url()}/api/studio/status/catalog?{query}"
    return _request_json(url, _api_key())


def get_website_publication_status(publication_id: str) -> Dict[str, Any]:
    publication_value = _normalize_text(publication_id)
    if not publication_value:
        raise ValueError("publication_id_missing")
    encoded = parse.quote(publication_value, safe="")
    url = f"{_base_url()}/api/studio/publications/{encoded}/status"
    return _request_json(url, _api_key())


def unpublish_website_publication(publication_id: str) -> Dict[str, Any]:
    publication_value = _normalize_text(publication_id)
    if not publication_value:
        raise ValueError("publication_id_missing")
    encoded = parse.quote(publication_value, safe="")
    url = f"{_base_url()}/api/studio/publications/{encoded}/unpublish"
    return _request_json(url, _api_key(), method="POST")


def revalidate_website_publication(publication_id: str) -> Dict[str, Any]:
    publication_value = _normalize_text(publication_id)
    if not publication_value:
        raise ValueError("publication_id_missing")
    encoded = parse.quote(publication_value, safe="")
    url = f"{_base_url()}/api/studio/publications/{encoded}/revalidate"
    return _request_json(url, _api_key(), method="POST")


def get_website_publication_divergence(publication_id: str, expected_checksum: str = "", expected_project_version: str = "") -> Dict[str, Any]:
    status = get_website_publication_status(publication_id)
    publication = status.get("status") or status.get("publication") or {}
    studio_meta = publication.get("studio_meta") or {}
    actual_checksum = _normalize_text(studio_meta.get("checksum"))
    actual_project_version = _normalize_text(studio_meta.get("project_version"))
    expected_checksum = _normalize_text(expected_checksum)
    expected_project_version = _normalize_text(expected_project_version)

    checksum_matches = bool(expected_checksum) and actual_checksum == expected_checksum
    project_version_matches = bool(expected_project_version) and actual_project_version == expected_project_version

    reasons = []
    if expected_checksum and not checksum_matches:
      reasons.append("checksum_mismatch")
    if expected_project_version and not project_version_matches:
      reasons.append("project_version_mismatch")

    ok = len(reasons) == 0
    return {
      "ok": True,
      "publication_id": publication_id,
      "expected_checksum": expected_checksum,
      "actual_checksum": actual_checksum,
      "expected_project_version": expected_project_version,
      "actual_project_version": actual_project_version,
      "checksum_matches": checksum_matches,
      "project_version_matches": project_version_matches,
      "divergence_ok": ok,
      "reasons": reasons,
      "website_status": status,
    }
