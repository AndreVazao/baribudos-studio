from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from studio_core.core.config import resolve_project_path
from studio_core.services.ip_creator_service import can_edit_ip, get_ip_by_slug, update_ip

router = APIRouter(prefix="/ip-branding", tags=["ip-branding"])


def _user_from_form(
    user_id: str = "",
    user_name: str = "",
    user_role: str = ""
) -> dict:
    return {
        "id": str(user_id).strip(),
        "name": str(user_name).strip(),
        "role": str(user_role).strip()
    }


def _safe_file_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() or ch in {".", "_", "-"} else "-" for ch in str(value or "").strip())


def _branding_folder_for_ip(slug: str) -> Path:
    folder = resolve_project_path("public", "brand", "ips", slug)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


@router.get("/{slug}")
def get_ip_branding(slug: str, user_id: str = "", user_name: str = "", user_role: str = "") -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    user = _user_from_form(user_id, user_name, user_role)
    if not can_edit_ip(user, slug):
        raise HTTPException(status_code=403, detail="Sem permissão para ver branding desta IP.")

    return {
        "ok": True,
        "slug": slug,
        "brand_assets": item.get("brand_assets", {})
    }


@router.patch("/{slug}")
def update_ip_branding(slug: str, payload: dict) -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    user = {
        "id": str(payload.get("user_id", "")).strip(),
        "name": str(payload.get("user_name", "")).strip(),
        "role": str(payload.get("user_role", "")).strip()
    }

    if not can_edit_ip(user, slug):
        raise HTTPException(status_code=403, detail="Sem permissão para editar branding desta IP.")

    brand_assets = payload.get("brand_assets") or {}
    if not isinstance(brand_assets, dict):
        raise HTTPException(status_code=400, detail="brand_assets inválido.")

    try:
        updated = update_ip(slug, {"brand_assets": brand_assets})
        return {
            "ok": True,
            "slug": slug,
            "brand_assets": updated.get("brand_assets", {}),
            "ip": updated
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{slug}/upload")
async def upload_ip_brand_asset(
    slug: str,
    asset_type: str = Form(...),
    user_id: str = Form(""),
    user_name: str = Form(""),
    user_role: str = Form(""),
    file: UploadFile = File(...)
) -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    user = _user_from_form(user_id, user_name, user_role)
    if not can_edit_ip(user, slug):
        raise HTTPException(status_code=403, detail="Sem permissão para upload nesta IP.")

    valid_asset_types = {"studio_logo", "series_logo", "seal_logo"}
    if asset_type not in valid_asset_types:
        raise HTTPException(status_code=400, detail="asset_type inválido.")

    ext = Path(file.filename or "").suffix.lower() or ".png"
    if ext not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise HTTPException(status_code=400, detail="Formato inválido. Usa PNG/JPG/WEBP.")

    folder = _branding_folder_for_ip(slug)
    file_name = _safe_file_name(f"{asset_type}-{uuid4().hex}{ext}")
    target = folder / file_name

    content = await file.read()
    target.write_bytes(content)

    relative_path = f"public/brand/ips/{slug}/{file_name}"

    try:
        updated = update_ip(slug, {
            "brand_assets": {
                **(item.get("brand_assets") or {}),
                asset_type: relative_path
            }
        })
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "ok": True,
        "slug": slug,
        "asset_type": asset_type,
        "file_name": file_name,
        "relative_path": relative_path,
        "brand_assets": updated.get("brand_assets", {})
  }
