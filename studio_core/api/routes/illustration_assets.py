from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from studio_core.core.storage import read_json
from studio_core.services.illustration_asset_service import (
    attach_uploaded_frame_image,
    build_storyboard_manifest,
)

router = APIRouter(prefix="/illustration-assets", tags=["illustration-assets"])

PROJECTS_FILE = "data/projects.json"


def _get_project(project_id: str) -> dict | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        if str(project.get("id", "")) == str(project_id):
            return project
    return None


@router.post("/upload")
async def upload_frame_asset(
    project_id: str = Form(...),
    frame_id: str = Form(...),
    file: UploadFile = File(...),
) -> dict:
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    suffix = Path(file.filename or "frame.png").suffix or ".png"

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                tmp.write(chunk)
            tmp_path = tmp.name

        result = attach_uploaded_frame_image(
            project_id=project_id,
            frame_id=frame_id,
            source_path=tmp_path,
            original_filename=file.filename or f"{frame_id}.png",
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/storyboard/{project_id}")
def get_storyboard_manifest(project_id: str) -> dict:
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    return {
        "ok": True,
        "manifest": build_storyboard_manifest(project),
  }
