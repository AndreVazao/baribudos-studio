from __future__ import annotations

import hashlib
import json
from typing import Any, Dict
from urllib import error, request

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item
from studio_core.services.credential_resolver_service import resolve_credential
from studio_core.services.publication_policy_service import evaluate_project_publication_policy
from studio_core.services.website_contract_payload_service import build_website_payload_from_package

PROJECTS_FILE = "data/projects.json"
DEFAULT_SCHEMA_VERSION = "website_ingest_v1"


def _load_project(project_id: str) -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    if not isinstance(projects, list):
        return None
    for project in projects:
        if str(project.get("id", "")) == str(project_id):
            return project
    return None


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def build_publish_envelope(project_id: str) -> Dict[str, Any]:
    project = _load_project(project_id)
    if not project:
        raise ValueError("project_not_found")

    policy = evaluate_project_publication_policy(project)
    if not bool(policy.get("eligible_for_website_publish", False)):
        raise ValueError(f"project_not_publishable:{','.join(policy.get('reasons', []))}")

    package = _safe_dict(project.get("publication_package"))
    frozen_at = _normalize_text(project.get("publication_package_frozen_at"))
    if not package:
        raise ValueError("publication_package_not_frozen")
    if not frozen_at:
        raise ValueError("publication_package_missing_freeze_timestamp")

    website_payload = build_website_payload_from_package(package)
    base_variant_id = _normalize_text(website_payload.get("project_id"))
    language = _normalize_text(website_payload.get("language")) or "pt-PT"
    final_variant_id = _normalize_text(website_payload.get("variant_id")) or f"{base_variant_id}:website:{language}:default"
    publication_id = f"{base_variant_id}:website"

    envelope = {
        "schema_version": DEFAULT_SCHEMA_VERSION,
        "publication_id": publication_id,
        "variant_id": final_variant_id,
        "project_id": _normalize_text(project.get("id")),
        "project_version": frozen_at,
        "published_at": now_iso(),
        "payload": website_payload,
        "related_variants": [],
        "related_projects": [],
        "asset_manifest": _safe_dict(_safe_dict(package.get("assets")).get("public")),
        "branding_pack": _safe_dict(_safe_dict(package.get("assets")).get("branding_resolution")),
        "marketplace_visuals": {
            "website": {
                "hero_background": _safe_dict(website_payload.get("assets")).get("hero_background", ""),
                "promo_banners": _safe_dict(website_payload.get("assets")).get("promo_banners", []),
                "social_cards": _safe_dict(website_payload.get("assets")).get("social_cards", []),
                "campaign_visuals": _safe_dict(website_payload.get("assets")).get("campaign_visuals", []),
            }
        },
    }

    envelope_bytes = json.dumps(envelope, ensure_ascii=False, sort_keys=True).encode("utf-8")
    envelope["checksum"] = hashlib.sha256(envelope_bytes).hexdigest()
    return envelope


def publish_project_to_website(project_id: str) -> Dict[str, Any]:
    target_url = resolve_credential("BARIBUDOS_WEBSITE_PUBLISH_URL", target="website")
    api_key = resolve_credential("BARIBUDOS_WEBSITE_PUBLISH_API_KEY", target="website")

    if not target_url:
        raise ValueError("website_publish_url_missing")
    if not api_key:
        raise ValueError("website_publish_api_key_missing")

    envelope = build_publish_envelope(project_id)
    body = json.dumps(envelope, ensure_ascii=False).encode("utf-8")

    http_request = request.Request(
        target_url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-studio-api-key": api_key,
        },
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            result = json.loads(raw) if raw else {"ok": True}
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="ignore")
        raise ValueError(f"website_publish_http_error:{exc.code}:{details}") from exc
    except error.URLError as exc:
        raise ValueError(f"website_publish_connection_error:{exc.reason}") from exc

    receipt = {
        "ok": bool(result.get("ok", False)),
        "target_url": target_url,
        "schema_version": envelope.get("schema_version"),
        "publication_id": envelope.get("publication_id"),
        "variant_id": envelope.get("variant_id"),
        "checksum": envelope.get("checksum"),
        "published_at": envelope.get("published_at"),
        "response": result,
        "synced_at": now_iso(),
    }

    update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "website_sync": receipt,
            "updated_at": now_iso(),
        },
    )

    return {"ok": True, "project_id": project_id, "envelope": envelope, "receipt": receipt}


def get_project_publish_status(project_id: str) -> Dict[str, Any]:
    project = _load_project(project_id)
    if not project:
        raise ValueError("project_not_found")

    package = _safe_dict(project.get("publication_package"))
    website_sync = _safe_dict(project.get("website_sync"))
    policy = evaluate_project_publication_policy(project)

    return {
        "ok": True,
        "project_id": project_id,
        "has_frozen_package": bool(package),
        "publication_package_frozen_at": project.get("publication_package_frozen_at", ""),
        "website_sync": website_sync,
        "publication_policy": policy,
    }
