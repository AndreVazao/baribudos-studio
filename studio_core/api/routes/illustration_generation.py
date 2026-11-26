from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles
from studio_core.services.illustration_generation_service import (
    export_illustration_prompt_package,
    import_generated_frame_image_from_temp_upload,
    list_illustration_jobs,
    queue_illustration_generation,
    update_illustration_job,
)
from studio_core.services.project_route_auth import (
    assert_project_access,
    require_project_form_access,
    require_project_path_access,
)

_PROJECT_ROLES = ("owner", "admin", "editor", "creator")
router = APIRouter(
    prefix="/illustration-generation",
    tags=["illustration-generation"],
    dependencies=[Depends(require_roles(*_PROJECT_ROLES))],
)


@router.get("")
def get_jobs(
    project_id: str = "",
    principal: AuthenticatedPrincipal = Depends(require_roles(*_PROJECT_ROLES)),
) -> dict:
    if project_id:
        assert_project_access(project_id, principal)
    elif principal.role.strip().lower() not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="A listagem global de jobs exige owner/admin.")
    return {"ok": True, "jobs": list_illustration_jobs(project_id)}


@router.post("/queue/{project_id}")
def queue_generation(
    project_id: str,
    payload: dict | None = None,
    _principal=Depends(require_project_path_access),
) -> dict:
    try:
        return queue_illustration_generation(project_id, payload or {})
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Não foi possível colocar a geração em fila.") from exc


@router.get("/package/{project_id}")
def get_prompt_package(
    project_id: str,
    _principal=Depends(require_project_path_access),
) -> dict:
    try:
        return export_illustration_prompt_package(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Não foi possível exportar o pacote de prompts.") from exc


@router.post("/job/{job_id}")
def patch_job(
    job_id: str,
    payload: dict | None = None,
    principal: AuthenticatedPrincipal = Depends(require_roles(*_PROJECT_ROLES)),
) -> dict:
    job = next(
        (row for row in list_illustration_jobs() if str(row.get("id", "")).strip() == str(job_id).strip()),
        None,
    )
    if not isinstance(job, dict):
        raise HTTPException(status_code=404, detail="Job não encontrado.")
    assert_project_access(str(job.get("project_id", "")), principal)
    try:
        return update_illustration_job(job_id, payload or {})
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Não foi possível atualizar o job.") from exc


@router.post("/import")
async def import_generated_image(
    project_id: str = Form(...),
    frame_id: str = Form(...),
    approve: bool = Form(True),
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
        raise HTTPException(status_code=400, detail="Não foi possível importar a imagem gerada.") from exc
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)
