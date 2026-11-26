from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles
from studio_core.services.project_route_auth import assert_project_access
from studio_core.services.job_service import create_job, list_jobs

router = APIRouter(prefix="/jobs", tags=["jobs"])
_JOB_ROLES = ("owner", "admin", "editor", "creator")


@router.get("")
def jobs(
    project_id: str | None = Query(default=None),
    principal: AuthenticatedPrincipal = Depends(require_roles(*_JOB_ROLES)),
):
    if not project_id:
        if principal.role.lower() not in {"owner", "admin"}:
            raise HTTPException(status_code=403, detail="A listagem global de jobs exige owner/admin.")
        return list_jobs()
    assert_project_access(project_id, principal)
    return [job for job in list_jobs() if str(job.get("project_id", "")).strip() == project_id]


@router.post("")
def new_job(
    payload: dict,
    principal: AuthenticatedPrincipal = Depends(require_roles(*_JOB_ROLES)),
):
    project_id = str(payload.get("project_id", "")).strip()
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id é obrigatório.")
    assert_project_access(project_id, principal)
    trusted_payload = {**payload, "project_id": project_id, "created_by": principal.user_id}
    return create_job(payload.get("type"), trusted_payload)
