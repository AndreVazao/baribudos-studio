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

MAX_ILLUSTRATION_UPLOAD_BYTES = 50 * 1024 * 1024
UPLOAD_CHUNK_BYTES = 1024 * 1024

ALLOWED_IMAGE_SIGNATURES = {
    ".png": lambda header: header.startswith(b"\x89PNG\r\n\x1a\n"),
    ".jpg": lambda header: header.startswith(b"\xff\xd8\xff"),
    ".jpeg": lambda header: header.startswith(b"\xff\xd8\xff"),
    ".webp": lambda header: header.startswith(b"RIFF") and header[8:12] == b"WEBP",
}


def _uploaded_image_signature_matches(extension: str, header: bytes) -> bool:
    validator = ALLOWED_IMAGE_SIGNATURES.get(str(extension or "").lower())
    return bool(validator and validator(header))

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
            tmp_path = tmp.name
            total_bytes = 0
            while chunk := await file.read(UPLOAD_CHUNK_BYTES):
                total_bytes += len(chunk)
                if total_bytes > MAX_ILLUSTRATION_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail="Imagem excede o limite de 50 MB.")
                tmp.write(chunk)

        extension = suffix.lower()
        with Path(tmp_path).open("rb") as uploaded_file:
            header = uploaded_file.read(32)
        if not _uploaded_image_signature_matches(extension, header):
            raise HTTPException(status_code=415, detail="O conteúdo não corresponde a uma imagem PNG, JPEG ou WEBP.")

        return import_generated_frame_image_from_temp_upload(
            project_id=project_id,
            frame_id=frame_id,
            temp_path=tmp_path,
            original_filename=file.filename or f"{frame_id}.png",
            approve=approve,
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Não foi possível importar a imagem gerada.") from exc
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)
