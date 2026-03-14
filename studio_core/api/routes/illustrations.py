from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from studio_core.core.config import resolve_storage_path
from studio_core.core.models import now_iso
from studio_core.core.storage import update_json_item

router = APIRouter(prefix="/illustrations", tags=["illustrations"])

PROJECTS_FILE = "data/projects.json"


def _safe_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() or ch in {".", "_", "-"} else "_" for ch in str(value or "").strip())


@router.post("/upload")
async def upload_illustration(
    saga_id: str = Form(...),
    project_id: str = Form(...),
    file: UploadFile = File(...)
) -> dict:
    ext = Path(file.filename or "").suffix.lower() or ".png"
    if ext not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise HTTPException(status_code=400, detail="Formato inválido. Usa PNG/JPG/WEBP.")

    target_dir = resolve_storage_path("uploads", "illustrations", saga_id, project_id)
    target_dir.mkdir(parents=True, exist_ok=True)

    file_name = _safe_name(f"{uuid4().hex}{ext}")
    target_path = target_dir / file_name

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Ficheiro vazio.")

    target_path.write_bytes(content)

    try:
        update_json_item(
            PROJECTS_FILE,
            project_id,
            lambda current: {
                **current,
                "illustration_path": str(target_path),
                "updated_at": now_iso()
            }
        )
    except Exception:
        pass

    return {
        "ok": True,
        "result": {
            "file_name": file_name,
            "file_path": str(target_path),
            "relative_folder": str(target_dir)
        }
                            }
    
