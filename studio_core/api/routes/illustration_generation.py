from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from studio_core.services.illustration_generation_service import (
    export_illustration_prompt_package,
    import_generated_frame_image_from_temp_upload,
    list_illustration_jobs,
    queue_illustration_generation,
    update_illustration_job,
)

router = APIRouter(prefix="/illustration-generation", tags=["illustration-generation"])


@router.get("")
def get_jobs(project_id: str = "") -> dict:
    return {
        "ok": True,
        "jobs": list_illustration_jobs(project_id),
    }


@router.post("/queue/{project_id}")
def queue_generation(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return queue_illustration_generation(project_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/package/{project_id}")
def get_prompt_package(project_id: str) -> dict:
    try:
        return export_illustration_prompt_package(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/job/{job_id}")
def patch_job(job_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return update_illustration_job(job_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/import")
async def import_generated_image(
    project_id: str = Form(...),
    frame_id: str = Form(...),
    approve: bool = Form(True),
    file: UploadFile = File(...),
) -> dict:
    suffix = Path(file.filename or "frame.png").suffix or ".png"

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                tmp.write(chunk)
            tmp_path = tmp.name

        return import_generated_frame_image_from_temp_upload(
            project_id=project_id,
            frame_id=frame_id,
            temp_path=tmp_path,
            original_filename=file.filename or f"{frame_id}.png",
            approve=approve,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
