from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from studio_core.core.models import now_iso
from studio_core.core.storage import append_json_item, read_json, update_json_item
from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles
from studio_core.services.project_authorization import require_project_access
from studio_core.services.publishing_service import publish_package, validate_project_publishability

router = APIRouter(prefix="/publishing", tags=["publishing"])

PROJECTS_FILE = "data/projects.json"
PUBLICATIONS_FILE = "data/publications.json"


def _get_project(project_id: str) -> dict | None:
    projects = read_json(PROJECTS_FILE, [])
    if not isinstance(projects, list):
        return None
    return next((item for item in projects if str(item.get("id", "")) == str(project_id)), None)


@router.get("")
def list_publications(
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor")),
) -> dict:
    publications = read_json(PUBLICATIONS_FILE, [])
    if not isinstance(publications, list):
        publications = []
    if principal.role.strip().lower() == "editor":
        owned_ids = {
            str(project.get("id", ""))
            for project in read_json(PROJECTS_FILE, [])
            if isinstance(project, dict) and str(project.get("created_by", "")) == principal.user_id
        }
        publications = [item for item in publications if str(item.get("project_id", "")) in owned_ids]
    return {"ok": True, "publications": publications}


@router.post("/publish")
def publish_project(
    payload: dict,
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor")),
) -> dict:
    project_id = str(payload.get("project_id", "")).strip()
    language = str(payload.get("language", "pt-PT")).strip()
    channel = str(payload.get("channel", "ebook")).strip()
    notes = str(payload.get("notes", "")).strip()

    if not project_id:
        raise HTTPException(status_code=400, detail="project_id é obrigatório.")

    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")
    require_project_access(project, principal)

    validation = validate_project_publishability(project)
    readiness = validation.get("readiness", {}) or {}
    file_guards = validation.get("file_guards", {}) or {}

    if not readiness.get("ready", False):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Projeto não pode ser publicado. "
                f"Estado atual: {readiness.get('label', 'Não pronto')}. "
                f"Campos em falta: {', '.join(readiness.get('missing_required_fields', [])) or '-'} | "
                f"Outputs em falta: {', '.join(readiness.get('missing_required_outputs', [])) or '-'}"
            ),
        )

    if not bool(project.get("ready_for_publish", False)):
        raise HTTPException(status_code=400, detail="Projeto ainda não está marcado como pronto para publicar.")

    if not validation.get("ok", False):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Bloqueio de integridade ativo. "
                f"Falhas: {', '.join(validation.get('hard_failures', [])) or '-'} | "
                f"cover_ok={file_guards.get('cover_ok', False)} | "
                f"epub_ok={file_guards.get('epub_ok', False)}"
            ),
        )

    publication = publish_package({
        "project_id": project_id,
        "language": language,
        "channel": channel,
        "requested_by": principal.name or principal.user_id,
        "notes": notes,
    })

    append_json_item(PUBLICATIONS_FILE, publication)
    update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "status": "published",
            "commercial": {
                **(current.get("commercial", {}) or {}),
                "commercial_status": "published",
            },
            "last_publication": publication,
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "publication": publication,
        "readiness": readiness,
        "file_guards": file_guards,
    }
