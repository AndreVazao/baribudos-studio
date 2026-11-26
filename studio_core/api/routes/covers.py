from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from studio_core.core.models import now_iso
from studio_core.core.storage import update_json_item
from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles
from studio_core.services.project_route_auth import assert_project_access
from studio_core.services.cover_service import build_cover

router = APIRouter(prefix="/covers", tags=["covers"])
PROJECTS_FILE = "data/projects.json"


@router.post("/build")
def create_cover(
    payload: dict,
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor", "creator")),
) -> dict:
    project_id = str(payload.get("project_id", "")).strip()
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id é obrigatório.")
    assert_project_access(project_id, principal)
    saga_id = str(payload.get("saga_id", "baribudos")).strip()
    if not saga_id or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for ch in saga_id):
        raise HTTPException(status_code=400, detail="saga_id inválido.")

    try:
        result = build_cover(
            saga_id=saga_id,
            project_id=project_id,
            title=str(payload.get("title", "Nova História")).strip(),
            age_range=str(payload.get("age_range", "4-10")).strip(),
            language=str(payload.get("language", "pt-PT")).strip(),
            illustration_path=str(payload.get("illustration_path", "")).strip(),
            producer="Baribudos Studio",
            output_name=payload.get("output_name"),
        )
        update_json_item(
            PROJECTS_FILE,
            project_id,
            lambda current: {
                **current,
                "cover_image": result.get("file_path", ""),
                "outputs": {**(current.get("outputs", {}) or {}), "covers": result},
                "updated_at": now_iso(),
            },
        )
        return {"ok": True, "result": result}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
