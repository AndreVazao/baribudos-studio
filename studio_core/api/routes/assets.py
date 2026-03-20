from __future__ import annotations

import mimetypes
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile

from studio_core.core.config import resolve_storage_path
from studio_core.services.asset_registry_service import (
    archive_asset,
    get_asset_by_id,
    get_assets,
    publish_asset,
    register_asset,
    rollback_asset,
    update_asset,
)
from studio_core.services.cdn_service import resolve_cdn_url

router = APIRouter(prefix="/assets", tags=["assets"])


def _safe_str(value: str | None) -> str:
    return str(value or "").strip()


def _safe_int(value: str | None, default: int = 0) -> int:
    try:
        return int(str(value or "").strip())
    except Exception:
        return default


def _safe_bool(value: str | None, default: bool = False) -> bool:
    normalized = _safe_str(value).lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _build_asset_storage_path(
    ip_slug: str,
    asset_type: str,
    original_filename: str,
    language: str | None = None,
    project_id: str | None = None,
) -> tuple[Path, str]:
    ext = Path(original_filename or "").suffix or ".bin"
    filename = f"{uuid.uuid4().hex}{ext}"

    parts = ["editorial", "assets", _safe_str(ip_slug) or "global", _safe_str(asset_type) or "misc"]
    if _safe_str(language):
        parts.append(_safe_str(language))
    if _safe_str(project_id):
        parts.append(_safe_str(project_id))

    relative_dir = Path(*parts)
    relative_path = relative_dir / filename
    absolute_path = resolve_storage_path(str(relative_path))
    return absolute_path, str(relative_path).replace("\\", "/")


@router.get("")
def list_registered_assets(
    project_id: str | None = Query(default=None),
    ip_slug: str | None = Query(default=None),
    publication_id: str | None = Query(default=None),
    variant_id: str | None = Query(default=None),
    asset_type: str | None = Query(default=None),
    context: str | None = Query(default=None),
    language: str | None = Query(default=None),
    status: str | None = Query(default=None),
    is_primary: bool | None = Query(default=None),
) -> dict:
    filters = {
        "project_id": project_id,
        "ip_slug": ip_slug,
        "publication_id": publication_id,
        "variant_id": variant_id,
        "asset_type": asset_type,
        "context": context,
        "language": language,
        "status": status,
        "is_primary": is_primary,
    }

    items = get_assets(filters)
    return {
        "ok": True,
        "filters": filters,
        "items": items,
        "count": len(items),
    }


@router.get("/{asset_id}")
def get_registered_asset(asset_id: str) -> dict:
    asset = get_asset_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset não encontrado")
    return {
        "ok": True,
        "asset": asset,
    }


@router.post("/register")
def register_asset_record(payload: dict) -> dict:
    asset = register_asset(payload or {})
    return {
        "ok": True,
        "asset": asset,
    }


@router.post("/upload")
async def upload_asset(
    file: UploadFile = File(...),
    ip_slug: str = Form(...),
    asset_type: str = Form(...),
    context: str = Form(...),
    project_id: Optional[str] = Form(default=None),
    series_name: Optional[str] = Form(default=None),
    publication_id: Optional[str] = Form(default=None),
    variant_id: Optional[str] = Form(default=None),
    language: Optional[str] = Form(default=None),
    is_primary: Optional[str] = Form(default="false"),
    priority: Optional[str] = Form(default="0"),
    width: Optional[str] = Form(default=None),
    height: Optional[str] = Form(default=None),
    status: Optional[str] = Form(default="draft"),
) -> dict:
    normalized_ip_slug = _safe_str(ip_slug)
    normalized_asset_type = _safe_str(asset_type)
    normalized_context = _safe_str(context)

    if not normalized_ip_slug:
        raise HTTPException(status_code=400, detail="ip_slug é obrigatório")
    if not normalized_asset_type:
        raise HTTPException(status_code=400, detail="asset_type é obrigatório")
    if not normalized_context:
        raise HTTPException(status_code=400, detail="context é obrigatório")

    absolute_path, relative_path = _build_asset_storage_path(
        ip_slug=normalized_ip_slug,
        asset_type=normalized_asset_type,
        original_filename=file.filename or "asset.bin",
        language=_safe_str(language) or None,
        project_id=_safe_str(project_id) or None,
    )

    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    absolute_path.write_bytes(content)

    mime_type = file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"
    file_size = len(content)

    payload = {
        "project_id": _safe_str(project_id) or None,
        "ip_slug": normalized_ip_slug,
        "series_name": _safe_str(series_name) or None,
        "publication_id": _safe_str(publication_id) or None,
        "variant_id": _safe_str(variant_id) or None,
        "asset_type": normalized_asset_type,
        "context": normalized_context,
        "language": _safe_str(language) or None,
        "is_primary": _safe_bool(is_primary, False),
        "priority": _safe_int(priority, 0),
        "width": _safe_int(width, 0) if _safe_str(width) else None,
        "height": _safe_int(height, 0) if _safe_str(height) else None,
        "mime_type": mime_type,
        "file_size": file_size,
        "storage_path": relative_path,
        "url": resolve_cdn_url(relative_path, 1),
        "status": _safe_str(status) or "draft",
    }

    asset = register_asset(payload)

    asset = update_asset(
        asset["asset_id"],
        {
            "url": resolve_cdn_url(asset.get("storage_path", ""), asset.get("version")),
        },
    ) or asset

    return {
        "ok": True,
        "asset": asset,
    }


@router.post("/{asset_id}/publish")
def publish_registered_asset(asset_id: str) -> dict:
    asset = publish_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset não encontrado")
    asset = update_asset(
        asset_id,
        {
            "url": resolve_cdn_url(asset.get("storage_path", ""), asset.get("version")),
        },
    ) or asset
    return {
        "ok": True,
        "asset": asset,
    }


@router.post("/{asset_id}/archive")
def archive_registered_asset(asset_id: str) -> dict:
    asset = archive_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset não encontrado")
    return {
        "ok": True,
        "asset": asset,
    }


@router.post("/{asset_id}/rollback")
def rollback_registered_asset(asset_id: str) -> dict:
    asset = rollback_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset não encontrado")
    asset = update_asset(
        asset_id,
        {
            "url": resolve_cdn_url(asset.get("storage_path", ""), asset.get("version")),
        },
    ) or asset
    return {
        "ok": True,
        "asset": asset,
}
