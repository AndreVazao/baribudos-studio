from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.core.storage import read_json
from studio_core.services.publication_package_freeze_service import (
    build_freeze_snapshot,
    freeze_publication_package_operationally,
)
from studio_core.services.publication_package_service import build_publication_package

router = APIRouter(prefix="/publication-package", tags=["publication-package"])

PROJECTS_FILE = "data/projects.json"


def _normalize_name(value: str) -> str:
    return str(value or "").strip().lower()


def _can_edit_or_publish(user_role: str, user_name: str) -> bool:
    role = str(user_role or "").strip().lower()
    name = _normalize_name(user_name)
    return role in {"owner", "creator", "admin"} or name in {"andré", "andre", "esposa", "wife", "mama"}


def _get_project(project_id: str) -> dict | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        if str(project.get("id", "")) == str(project_id):
            return project
    return None


@router.get("/{project_id}")
def get_publication_package(project_id: str) -> dict:
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    package = build_publication_package(project)
    return {
        "ok": True,
        "project_id": project_id,
        "package": package,
        "frozen_at": project.get("publication_package_frozen_at", ""),
        "freeze": project.get("publication_package_freeze", {}),
    }


@router.get("/{project_id}/freeze-preview")
def get_publication_package_freeze_preview(project_id: str) -> dict:
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    snapshot = build_freeze_snapshot(project)
    return {
        "ok": True,
        "project_id": project_id,
        "freeze_preview": snapshot,
    }


@router.post("/{project_id}/freeze")
def freeze_publication_package(project_id: str, user_name: str = "", user_role: str = "") -> dict:
    if not _can_edit_or_publish(user_role, user_name):
        raise HTTPException(status_code=403, detail="Sem permissão para congelar pacote final.")

    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    try:
        return freeze_publication_package_operationally(project_id, user_name=user_name, user_role=user_role)
    except ValueError as exc:
        message = str(exc)
        if message == "project_not_found":
            raise HTTPException(status_code=404, detail="Projeto não encontrado.") from exc
        if message == "project_not_ready_for_publish":
            raise HTTPException(status_code=400, detail="Projeto ainda não está marcado como pronto para publicação.") from exc
        if message == "website_contract_not_ready":
            raise HTTPException(status_code=400, detail="Contrato Website ainda não cumpre os campos/ativos obrigatórios para congelar pacote público.") from exc
        raise HTTPException(status_code=400, detail=message) from exc
