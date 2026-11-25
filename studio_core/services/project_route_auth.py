from __future__ import annotations

from fastapi import Depends, Form, HTTPException, Query

from studio_core.core.storage import read_json
from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles
from studio_core.services.project_authorization import require_project_access

_PROJECT_ROLES = ("owner", "admin", "editor", "creator")


def assert_project_access(project_id: str, principal: AuthenticatedPrincipal) -> AuthenticatedPrincipal:
    projects = read_json("data/projects.json", [])
    project = next(
        (row for row in projects if str(row.get("id", "")).strip() == str(project_id).strip()),
        None,
    )
    if not isinstance(project, dict):
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")
    require_project_access(project, principal)
    return principal


def require_project_path_access(
    project_id: str,
    principal: AuthenticatedPrincipal = Depends(require_roles(*_PROJECT_ROLES)),
) -> AuthenticatedPrincipal:
    return assert_project_access(project_id, principal)


def require_project_form_access(
    project_id: str = Form(...),
    principal: AuthenticatedPrincipal = Depends(require_roles(*_PROJECT_ROLES)),
) -> AuthenticatedPrincipal:
    return assert_project_access(project_id, principal)


def require_project_query_access(
    project_id: str = Query(...),
    principal: AuthenticatedPrincipal = Depends(require_roles(*_PROJECT_ROLES)),
) -> AuthenticatedPrincipal:
    return assert_project_access(project_id, principal)
