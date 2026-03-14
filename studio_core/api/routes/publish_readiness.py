from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item
from studio_core.services.publication_package_service import build_publication_package

router = APIRouter(prefix="/publish-readiness", tags=["publish-readiness"])

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
def get_publish_readiness(project_id: str) -> dict:
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    package = build_publication_package(project)
    return {
        "ok": True,
        "project_id": project_id,
        "readiness": package.get("checks", {}).get("readiness", {}),
        "ready_for_publish": bool(project.get("ready_for_publish", False)),
    }


@router.post("/{project_id}/mark-ready")
def mark_ready(project_id: str, user_name: str = "", user_role: str = "") -> dict:
    if not _can_edit_or_publish(user_role, user_name):
        raise HTTPException(status_code=403, detail="Sem permissão para marcar como pronto.")

    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    package = build_publication_package(project)
    readiness = package.get("checks", {}).get("readiness", {}) or {}

    if not readiness.get("ready", False):
        raise HTTPException(
            status_code=400,
            detail=f"Projeto ainda não está pronto. Estado: {readiness.get('label', 'Não pronto')}."
        )

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "ready_for_publish": True,
            "ready_for_publish_at": now_iso(),
            "updated_at": now_iso()
        }
    )

    return {
        "ok": True,
        "project_id": project_id,
        "ready_for_publish": updated.get("ready_for_publish", False),
        "ready_for_publish_at": updated.get("ready_for_publish_at", "")
    }


@router.post("/{project_id}/unmark-ready")
def unmark_ready(project_id: str, user_name: str = "", user_role: str = "") -> dict:
    if not _can_edit_or_publish(user_role, user_name):
        raise HTTPException(status_code=403, detail="Sem permissão para remover prontidão.")

    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "ready_for_publish": False,
            "updated_at": now_iso()
        }
    )

    return {
        "ok": True,
        "project_id": project_id,
        "ready_for_publish": updated.get("ready_for_publish", False)
}
