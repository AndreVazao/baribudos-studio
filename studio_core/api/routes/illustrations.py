from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from studio_core.core.config import resolve_storage_path
from studio_core.core.models import now_iso
from studio_core.core.storage import update_json_item
from studio_core.services.auth_principal import AuthenticatedPrincipal
from studio_core.services.project_route_auth import require_project_form_access

router = APIRouter(prefix="/illustrations", tags=["illustrations"])
PROJECTS_FILE = "data/projects.json"
_ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def _safe_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() or ch in {".", "_", "-"} else "_" for ch in str(value or "").strip())


@router.post("/upload")
async def upload_illustration(
    saga_id: str = Form(...),
    project_id: str = Form(...),
    file: UploadFile = File(...),
    principal: AuthenticatedPrincipal = Depends(require_project_form_access),
) -> dict:
    saga_component = str(saga_id).strip()
    project_component = str(project_id).strip()
    if not saga_component or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for ch in saga_component):
        raise HTTPException(status_code=400, detail="saga_id inválido.")
    ext = Path(file.filename or "").suffix.lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Formato inválido. Usa PNG/JPG/WEBP.")

    target_dir = resolve_storage_path("uploads", "illustrations", saga_component, project_component)
    target_dir.mkdir(parents=True, exist_ok=True)
    file_name = _safe_name(f"{uuid4().hex}{ext}")
    target_path = target_dir / file_name

    content = await file.read(10 * 1024 * 1024 + 1)
    if not content:
        raise HTTPException(status_code=400, detail="Ficheiro vazio.")
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Ficheiro excede o limite de 10 MB.")

    target_path.write_bytes(content)
    try:
        update_json_item(
            PROJECTS_FILE,
            project_component,
            lambda current: {
                **current,
                "illustration_path": str(target_path),
                "updated_at": now_iso(),
            },
        )
    except Exception:
        target_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Não foi possível registar a ilustração no projeto.") from None

    return {"ok": True, "result": {"file_name": file_name, "file_path": str(target_path), "relative_folder": str(target_dir)}}
