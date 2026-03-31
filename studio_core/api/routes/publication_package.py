from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.core.storage import read_json, update_json_item
from studio_core.core.models import now_iso
from studio_core.services.publication_package_service import build_publication_package
from studio_core.services.publication_policy_service import evaluate_project_publication_policy

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
    return {"ok": True, "project_id": project_id, "package": package}


@router.post("/{project_id}/freeze")
def freeze_publication_package(project_id: str, user_name: str = "", user_role: str = "") -> dict:
    if not _can_edit_or_publish(user_role, user_name):
        raise HTTPException(status_code=403, detail="Sem permissão para congelar pacote final.")

    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    if not bool(project.get("ready_for_publish", False)):
        raise HTTPException(status_code=400, detail="Projeto ainda não está marcado como pronto para publicação.")

    package = build_publication_package(project)
    policy = evaluate_project_publication_policy({**project, "publication_package": package, "publication_package_frozen_at": now_iso()})
    if not bool(policy.get("contract", {}).get("required_ok", False)):
        raise HTTPException(status_code=400, detail="Contrato Website ainda não cumpre os campos/ativos obrigatórios para congelar pacote público.")

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "publication_package": package,
            "publication_package_frozen_at": now_iso(),
            "updated_at": now_iso()
        }
    )

    return {
        "ok": True,
        "project_id": project_id,
        "publication_package": updated.get("publication_package", {}),
        "publication_package_frozen_at": updated.get("publication_package_frozen_at")
    }
