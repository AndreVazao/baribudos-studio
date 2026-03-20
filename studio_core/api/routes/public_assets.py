from __future__ import annotations

from fastapi import APIRouter, Query

from studio_core.services.asset_registry_service import (
    build_context_asset_manifest,
    build_ip_asset_manifest,
    build_project_asset_manifest,
    get_assets,
)

router = APIRouter(prefix="/public", tags=["public-assets"])


# ==========================================================
# IP ASSET MANIFEST (EDITORIAL)
# ==========================================================
@router.get("/ip/{ip_slug}/assets")
def ip_assets(ip_slug: str) -> dict:
    manifest = build_ip_asset_manifest(ip_slug)
    return manifest


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
        "assets": assets,
    }
