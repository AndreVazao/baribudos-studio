from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict
from urllib import error, request

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item
from studio_core.services.publication_package_service import build_publication_package

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


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _build_short_description(description: str, fallback: str = "") -> str:
    text = _normalize_text(fallback) or _normalize_text(description)
    if len(text) <= 180:
        return text
    return f"{text[:177].rstrip()}..."


def _normalize_assets(website_payload: Dict[str, Any], package: Dict[str, Any]) -> Dict[str, Any]:
    assets = _safe_dict(website_payload.get("assets"))
    outputs = _safe_dict(package.get("outputs"))

    primary_logo = _normalize_text(assets.get("primary_logo"))
    secondary_logos = [item for item in _safe_list(assets.get("secondary_logos")) if _normalize_text(item)]

    logos: list[str] = []
    if primary_logo:
        logos.append(primary_logo)
    logos.extend([item for item in secondary_logos if item not in logos])

    downloadable_files: list[str] = []
    epub_outputs = _safe_dict(outputs.get("epub"))
    for item in epub_outputs.values():
        file_path = _normalize_text(_safe_dict(item).get("file_path"))
        if file_path:
            downloadable_files.append(file_path)

    return {
        "cover": assets.get("cover") or "",
        "logos": logos,
        "gallery": _safe_list(assets.get("gallery")),
        "sample_pages": _safe_list(assets.get("sample_pages")),
        "audiobook_preview": assets.get("audiobook_preview") or None,
        "video_trailer": assets.get("video_trailer") or None,
        "downloadable_files": downloadable_files,
    }


def _normalize_payload(package: Dict[str, Any]) -> Dict[str, Any]:
    website_payload = _safe_dict(package.get("website_payload"))
    commercial = _safe_dict(package.get("commercial"))
    editorial = _safe_dict(package.get("editorial"))

    description = _normalize_text(website_payload.get("description"))
    subtitle = _normalize_text(commercial.get("subtitle"))
    short_description = _build_short_description(description, commercial.get("blurb"))
    seo = _safe_dict(website_payload.get("seo"))

    normalized_payload = {
        "project_id": _normalize_text(website_payload.get("project_id")),
        "project_slug": _normalize_text(website_payload.get("project_slug")),
        "ip_slug": _normalize_text(website_payload.get("ip_slug")),
        "ip_name": _normalize_text(website_payload.get("ip_name")),
        "series_name": _normalize_text(website_payload.get("series_name")),
        "language": _normalize_text(website_payload.get("language")) or "pt-PT",
        "title": _normalize_text(website_payload.get("title")),
        "subtitle": subtitle,
        "description": description,
        "short_description": short_description,
        "formats": _safe_list(website_payload.get("formats")),
        "price": website_payload.get("price") if website_payload.get("price") not in {None, ""} else 0,
        "currency": _normalize_text(website_payload.get("currency")) or "EUR",
        "channel": _normalize_text(website_payload.get("channel")) or "website",
        "assets": _normalize_assets(website_payload, package),
        "seo": {
            "title": _normalize_text(seo.get("title")) or _normalize_text(website_payload.get("title")),
            "description": _normalize_text(seo.get("description")) or description,
            "keywords": _safe_list(seo.get("keywords")),
            "canonical_url": _normalize_text(seo.get("canonical_url")),
            "og_image": _normalize_text(seo.get("og_image")),
        },
        "characters": [item for item in _safe_list(website_payload.get("characters")) if _normalize_text(item)],
        "themes": [item for item in _safe_list(website_payload.get("themes")) if _normalize_text(item)],
        "values": [item for item in _safe_list(website_payload.get("values")) if _normalize_text(item)],
        "authors": [item for item in _safe_list(website_payload.get("authors")) if _normalize_text(item)],
        "badges": [item for item in _safe_list(website_payload.get("badges")) if _normalize_text(item)],
        "buy_links": _safe_list(website_payload.get("buy_links")),
    }

    if not normalized_payload["subtitle"]:
        normalized_payload["subtitle"] = _normalize_text(editorial.get("tagline"))

    return normalized_payload


def build_publish_envelope(project_id: str) -> Dict[str, Any]:
    project = _load_project(project_id)
    if not project:
        raise ValueError("project_not_found")

    package = _safe_dict(project.get("publication_package"))
    frozen_at = _normalize_text(project.get("publication_package_frozen_at"))

    if not package:
        raise ValueError("publication_package_not_frozen")

    if not frozen_at:
        raise ValueError("publication_package_missing_freeze_timestamp")

    rebuilt_package = build_publication_package(project)
    website_payload = _normalize_payload(package)
    variant_id = _normalize_text(website_payload.get("project_id"))
    language = _normalize_text(website_payload.get("language")) or "pt-PT"

    final_variant_id = _normalize_text(_safe_dict(package.get("website_payload")).get("variant_id")) or f"{variant_id}:website:{language}:default"
    publication_id = f"{variant_id}:website"

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
            "website": _safe_dict(rebuilt_package.get("website_payload")),
        },
    }

    envelope_bytes = json.dumps(envelope, ensure_ascii=False, sort_keys=True).encode("utf-8")
    envelope["checksum"] = hashlib.sha256(envelope_bytes).hexdigest()
    return envelope


def publish_project_to_website(project_id: str) -> Dict[str, Any]:
    target_url = _normalize_text(os.getenv("BARIBUDOS_WEBSITE_PUBLISH_URL"))
    api_key = _normalize_text(os.getenv("BARIBUDOS_WEBSITE_PUBLISH_API_KEY"))

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

    return {
        "ok": True,
        "project_id": project_id,
        "envelope": envelope,
        "receipt": receipt,
    }


def get_project_publish_status(project_id: str) -> Dict[str, Any]:
    project = _load_project(project_id)
    if not project:
        raise ValueError("project_not_found")

    package = _safe_dict(project.get("publication_package"))
    website_sync = _safe_dict(project.get("website_sync"))

    return {
        "ok": True,
        "project_id": project_id,
        "has_frozen_package": bool(package),
        "publication_package_frozen_at": project.get("publication_package_frozen_at", ""),
        "website_sync": website_sync,
    }
