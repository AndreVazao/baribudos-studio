from __future__ import annotations

import mimetypes
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

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
from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles
from studio_core.services.ip_route_auth import assert_ip_edit_access, assert_ip_read_access
from studio_core.services.project_route_auth import assert_project_access

router = APIRouter(prefix="/assets", dependencies=[Depends(require_roles("owner", "admin", "editor"))], tags=["assets"])

MAX_ASSET_UPLOAD_BYTES = 50 * 1024 * 1024
ASSET_UPLOAD_CHUNK_BYTES = 1024 * 1024

ASSET_SIGNATURES = {
    ".png": lambda header: header.startswith(b"\x89PNG\r\n\x1a\n"),
    ".jpg": lambda header: header.startswith(b"\xff\xd8\xff"),
    ".jpeg": lambda header: header.startswith(b"\xff\xd8\xff"),
    ".gif": lambda header: header.startswith((b"GIF87a", b"GIF89a")),
    ".webp": lambda header: header.startswith(b"RIFF") and header[8:12] == b"WEBP",
    ".avif": lambda header: len(header) >= 12 and header[4:8] == b"ftyp" and header[8:12] in (b"avif", b"avis"),
    ".pdf": lambda header: header.startswith(b"%PDF-"),
    ".mp3": lambda header: header.startswith(b"ID3") or (len(header) >= 2 and header[0] == 0xFF and (header[1] & 0xE0) == 0xE0),
    ".wav": lambda header: header.startswith(b"RIFF") and header[8:12] == b"WAVE",
    ".ogg": lambda header: header.startswith(b"OggS"),
    ".m4a": lambda header: len(header) >= 12 and header[4:8] == b"ftyp" and header[8:12] in (b"M4A ", b"isom", b"mp42"),
    ".mp4": lambda header: len(header) >= 12 and header[4:8] == b"ftyp" and header[8:12] in (b"isom", b"mp42", b"avc1", b"M4V "),
    ".webm": lambda header: header.startswith(b"\x1a\x45\xdf\xa3"),
    ".epub": lambda header: header.startswith(b"PK\x03\x04") and b"mimetype" in header[:96] and b"application/epub+zip" in header[:128],
}


def _asset_signature_matches(extension: str, header: bytes) -> bool:
    validator = ASSET_SIGNATURES.get(str(extension or "").lower())
    return bool(validator and validator(header))



def _public_asset_url(asset: dict) -> str:
    asset_id = str(asset.get("asset_id", "")).strip()
    if asset_id and str(asset.get("status", "")).lower() == "published":
        return f"/api/public/assets/{asset_id}/file"
    return ""


def _asset_dto(asset: dict) -> dict:
    asset_id = str(asset.get("asset_id", "")).strip()
    safe = {
        key: value
        for key, value in asset.items()
        if key not in {"storage_path", "file_path", "absolute_path", "source_path"}
    }
    return {
        **safe,
        "url": _public_asset_url(asset),
        "file_url": f"/api/assets/{asset_id}/file" if asset_id else "",
    }


def _assert_asset_access(asset: dict, principal: AuthenticatedPrincipal, *, edit: bool = False) -> None:
    if principal.role.lower() in {"owner", "admin"}:
        return
    project_id = str(asset.get("project_id", "")).strip()
    ip_slug = str(asset.get("ip_slug", "")).strip()
    if project_id:
        assert_project_access(project_id, principal)
        if ip_slug:
            if edit:
                assert_ip_edit_access(ip_slug, principal)
            else:
                assert_ip_read_access(ip_slug, principal)
        return
    if ip_slug:
        if edit:
            assert_ip_edit_access(ip_slug, principal)
        else:
            assert_ip_read_access(ip_slug, principal)
        return
    raise HTTPException(status_code=403, detail="Sem acesso a este asset.")


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
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor")),
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
    if principal.role.lower() not in {"owner", "admin"}:
        visible = []
        for item in items:
            try:
                _assert_asset_access(item, principal)
                visible.append(item)
            except HTTPException:
                continue
        items = visible
    return {
        "ok": True,
        "filters": filters,
        "items": [_asset_dto(item) for item in items],
        "count": len(items),
    }


@router.get("/{asset_id}")
def get_registered_asset(asset_id: str, principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor"))) -> dict:
    asset = get_asset_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset não encontrado")
    try:
        _assert_asset_access(asset, principal)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Asset não encontrado.") from None
    return {
        "ok": True,
        "asset": _asset_dto(asset),
    }


@router.get("/{asset_id}/file")
def get_registered_asset_file(
    asset_id: str,
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor")),
) -> FileResponse:
    asset = get_asset_by_id(asset_id)
    if not isinstance(asset, dict):
        raise HTTPException(status_code=404, detail="Asset não encontrado.")

    _assert_asset_access(asset, principal)

    relative_path = str(asset.get("storage_path", "")).strip()
    try:
        file_path = resolve_storage_path(relative_path)
    except (OSError, ValueError):
        raise HTTPException(status_code=404, detail="Asset não encontrado.") from None

    allowed_extensions = {
        ".avif", ".epub", ".gif", ".jpeg", ".jpg", ".m4a", ".mp3",
        ".mp4", ".ogg", ".pdf", ".png", ".wav", ".webm", ".webp",
    }
    if file_path.suffix.lower() not in allowed_extensions or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Asset não encontrado.")

    media_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    safe_name = "".join(char for char in file_path.name if char.isalnum() or char in "._-") or "asset"
    inline = media_type.startswith(("image/", "audio/", "video/"))
    disposition = "inline" if inline else "attachment"
    return FileResponse(
        file_path,
        media_type=media_type,
        headers={
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
            "Content-Disposition": f'{disposition}; filename="{safe_name}"',
        },
    )


@router.post("/register")
def register_asset_record(payload: dict, principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor"))) -> dict:
    source = payload or {}
    _assert_asset_access(source, principal, edit=True)
    safe_payload = {**source, "status": "draft", "url": ""}
    asset = register_asset(safe_payload)
    return {
        "ok": True,
        "asset": _asset_dto(asset),
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
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor")),
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
    _assert_asset_access(
        {"project_id": project_id, "ip_slug": normalized_ip_slug},
        principal,
        edit=True,
    )

    absolute_path, relative_path = _build_asset_storage_path(
        ip_slug=normalized_ip_slug,
        asset_type=normalized_asset_type,
        original_filename=file.filename or "asset.bin",
        language=_safe_str(language) or None,
        project_id=_safe_str(project_id) or None,
    )

    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    file_size = 0
    created_file = False
    try:
        with absolute_path.open("xb") as destination:
            created_file = True
            while chunk := await file.read(ASSET_UPLOAD_CHUNK_BYTES):
                file_size += len(chunk)
                if file_size > MAX_ASSET_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Asset excede o limite de {MAX_ASSET_UPLOAD_BYTES // (1024 * 1024)} MB.",
                    )
                destination.write(chunk)
    except Exception:
        # Never delete a path that this request did not successfully create.
        if created_file:
            absolute_path.unlink(missing_ok=True)
        raise
    finally:
        await file.close()

    extension = absolute_path.suffix.lower()
    try:
        with absolute_path.open("rb") as stored_file:
            header = stored_file.read(128)
        if not _asset_signature_matches(extension, header):
            raise HTTPException(status_code=415, detail="Formato de ficheiro não corresponde à extensão permitida.")
    except Exception:
        if created_file:
            absolute_path.unlink(missing_ok=True)
        raise

    mime_type = mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"

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
        "url": "",
        "status": "draft",
    }

    asset = register_asset(payload)

    asset = update_asset(
        asset["asset_id"],
        {
            "url": _public_asset_url(asset),
        },
    ) or asset

    return {
        "ok": True,
        "asset": _asset_dto(asset),
    }


@router.post("/{asset_id}/publish")
def publish_registered_asset(asset_id: str, _principal=Depends(require_roles("owner", "admin"))) -> dict:
    asset = publish_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset não encontrado")
    asset = update_asset(
        asset_id,
        {
            "url": _public_asset_url(asset),
        },
    ) or asset
    return {
        "ok": True,
        "asset": _asset_dto(asset),
    }


@router.post("/{asset_id}/archive")
def archive_registered_asset(asset_id: str, _principal=Depends(require_roles("owner", "admin"))) -> dict:
    asset = archive_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset não encontrado")
    return {
        "ok": True,
        "asset": _asset_dto(asset),
    }


@router.post("/{asset_id}/rollback")
def rollback_registered_asset(asset_id: str, _principal=Depends(require_roles("owner", "admin"))) -> dict:
    asset = rollback_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset não encontrado")
    asset = update_asset(
        asset_id,
        {
            "url": _public_asset_url(asset),
        },
    ) or asset
    return {
        "ok": True,
        "asset": _asset_dto(asset),
}
