from __future__ import annotations

import mimetypes
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from studio_core.core.config import resolve_storage_path

from studio_core.services.asset_registry_service import (
    build_context_asset_manifest,
    build_ip_asset_manifest,
    build_project_asset_manifest,
    get_asset_by_id,
    get_assets,
)

router = APIRouter(prefix="/public", tags=["public-assets"])

_PUBLIC_ASSET_FIELDS = {
    "asset_id", "project_id", "ip_slug", "series_name", "publication_id", "variant_id",
    "asset_type", "context", "language", "version", "is_primary", "priority",
    "width", "height", "mime_type", "file_size", "url", "status", "created_at",
    "updated_at", "published_at",
}


def _sanitize_public_manifest(value):
    if isinstance(value, list):
        return [_sanitize_public_manifest(item) for item in value]
    if isinstance(value, dict):
        if "asset_id" in value:
            public = {key: item for key, item in value.items() if key in _PUBLIC_ASSET_FIELDS}
            asset_id = str(value.get("asset_id", "")).strip()
            public["url"] = (
                f"/api/public/assets/{asset_id}/file"
                if asset_id and str(value.get("status", "")).lower() == "published"
                else ""
            )
            return public
        return {
            key: _sanitize_public_manifest(item)
            for key, item in value.items()
            if key not in {"storage_path", "file_path", "absolute_path", "source_path"}
        }
    return value


# ==========================================================
# IP ASSET MANIFEST (EDITORIAL)
# ==========================================================
@router.get("/ip/{ip_slug}/assets")
def ip_assets(ip_slug: str) -> dict:
    manifest = build_ip_asset_manifest(ip_slug)
    return _sanitize_public_manifest(manifest)


# ==========================================================
# CONTEXTUAL ASSET MANIFEST
# ==========================================================
@router.get("/assets")
def assets_by_context(
    context: str = Query(...),
    ip_slug: str | None = Query(default=None),
) -> dict:
    manifest = build_context_asset_manifest(
        context=context,
        ip_slug=ip_slug,
    )
    return manifest


# ==========================================================
# PROJECT ASSET MANIFEST
# ==========================================================
@router.get("/project/{project_id}/assets")
def project_assets(project_id: str) -> dict:
    manifest = build_project_asset_manifest(project_id)
    return manifest


# ==========================================================
# LOW LEVEL RAW ACCESS (LEGACY SUPPORT)
# ==========================================================
@router.get("/raw")
def raw_assets(
    ip_slug: str | None = Query(default=None),
    context: str | None = Query(default=None),
    project_id: str | None = Query(default=None),
    asset_type: str | None = Query(default=None),
) -> dict:
    filters = {
        "ip_slug": ip_slug,
        "context": context,
        "project_id": project_id,
        "asset_type": asset_type,
        "status": "published",
    }

    assets = get_assets(filters)

    return {
        "ok": True,
        "filters": filters,
        "assets": _sanitize_public_manifest(assets),
    }


_PUBLIC_FILE_EXTENSIONS = {
    ".avif", ".gif", ".jpeg", ".jpg", ".mp3", ".mp4", ".ogg",
    ".pdf", ".png", ".wav", ".webm", ".webp",
}


@router.get("/assets/{asset_id}/file")
def public_asset_file(asset_id: str) -> FileResponse:
    asset = get_asset_by_id(asset_id)
    if not isinstance(asset, dict) or str(asset.get("status", "")).lower() != "published":
        raise HTTPException(status_code=404, detail="Asset público não encontrado.")

    relative_path = str(asset.get("storage_path", "")).strip()
    if not relative_path:
        raise HTTPException(status_code=404, detail="Asset público não encontrado.")
    try:
        file_path = resolve_storage_path(relative_path)
    except (OSError, ValueError):
        raise HTTPException(status_code=404, detail="Asset público não encontrado.") from None

    if file_path.suffix.lower() not in _PUBLIC_FILE_EXTENSIONS or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Asset público não encontrado.")

    media_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    inline = media_type.startswith(("image/", "audio/", "video/"))
    safe_name = "".join(char for char in file_path.name if char.isalnum() or char in "._-") or "media"
    disposition = "inline" if inline else "attachment"
    return FileResponse(
        file_path,
        media_type=media_type,
        headers={
            "Cache-Control": "public, max-age=300",
            "X-Content-Type-Options": "nosniff",
            "Content-Disposition": f'{disposition}; filename="{safe_name}"',
        },
    )
