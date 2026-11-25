from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from studio_core.services.auth_principal import require_roles
from studio_core.services.illustration_asset_service import (
    attach_uploaded_frame_image,
    build_storyboard_manifest,
)
from studio_core.services.project_route_auth import (
    require_project_form_access,
    require_project_path_access,
)

router = APIRouter(
    prefix="/illustration-assets",
    tags=["illustration-assets"],
    dependencies=[Depends(require_roles("owner", "admin", "editor", "creator"))],
)


@router.post("/upload")
async def upload_frame_asset(
    project_id: str = Form(...),
    frame_id: str = Form(...),
    file: UploadFile = File(...),
    _principal=Depends(require_project_form_access),
) -> dict:
    suffix = Path(file.filename or "frame.png").suffix or ".png"
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            while chunk := await file.read(1024 * 1024):
                tmp.write(chunk)
            tmp_path = tmp.name

        return attach_uploaded_frame_image(
            project_id=project_id,
            frame_id=frame_id,
            source_path=tmp_path,
            original_filename=file.filename or f"{frame_id}.png",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Não foi possível guardar o asset de ilustração.") from exc
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)


@router.get("/storyboard/{project_id}")
def get_storyboard_manifest(
    project_id: str,
    _principal=Depends(require_project_path_access),
) -> dict:
    from studio_core.core.storage import read_json

    projects = read_json("data/projects.json", [])
    project = next(
        (row for row in projects if str(row.get("id", "")).strip() == str(project_id).strip()),
        None,
    )
    if not isinstance(project, dict):
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")
    return {"ok": True, "manifest": build_storyboard_manifest(project)}
