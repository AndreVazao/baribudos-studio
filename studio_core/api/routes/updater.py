from __future__ import annotations

from pathlib import Path, PureWindowsPath

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from studio_core.core.config import resolve_storage_path

from studio_core.services.updater_service import check_for_updates, download_update, get_local_version_info
from studio_core.services.auth_principal import require_roles

router = APIRouter(prefix="/updater", dependencies=[Depends(require_roles("owner", "admin"))], tags=["updater"])


@router.get("/local-version")
def local_version() -> dict:
    return {
        "ok": True,
        "version": get_local_version_info(),
    }


@router.post("/check")
def check_updates(payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return check_for_updates(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/download")
def download_updates(payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return download_update(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc



_ALLOWED_UPDATE_EXTENSIONS = {".exe", ".msi", ".zip", ".dmg", ".pkg", ".apk", ".appimage"}


@router.get("/files/{file_name}")
def download_update_file(file_name: str) -> FileResponse:
    if (
        not file_name
        or file_name in {".", ".."}
        or Path(file_name).name != file_name
        or PureWindowsPath(file_name).name != file_name
        or Path(file_name).suffix.lower() not in _ALLOWED_UPDATE_EXTENSIONS
    ):
        raise HTTPException(status_code=404, detail="Ficheiro de atualização não encontrado.")

    try:
        file_path = resolve_storage_path("updates", file_name)
    except (OSError, ValueError):
        raise HTTPException(status_code=404, detail="Ficheiro de atualização não encontrado.") from None

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Ficheiro de atualização não encontrado.")

    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=file_name,
        headers={
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )
