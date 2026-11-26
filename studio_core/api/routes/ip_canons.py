from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from studio_core.core.config import resolve_project_path
from studio_core.services.ip_creator_service import get_ip_by_slug
from studio_core.services.auth_principal import AuthenticatedPrincipal
from studio_core.services.ip_route_auth import require_ip_edit_access, require_ip_read_access

router = APIRouter(prefix="/ip-canons", tags=["ip-canons"])

VALID_CANONS = {
    "visual": "visual-canon.json",
    "narrative": "narrative-canon.json",
    "episode": "episode-canon.json",
    "series_arc": "series-arc-canon.json",
    "pedagogical": "pedagogical-canon.json",
    "age_badge": "age-badge-canon.json",
    "characters": "characters-master.json"
}


def _canon_path(slug: str, canon_type: str) -> Path:
    file_name = VALID_CANONS.get(canon_type)
    if not file_name:
        raise ValueError("canon_type inválido.")
    return resolve_project_path("studio", "sagas", slug, file_name)


@router.get("/{slug}/{canon_type}")
def get_ip_canon(slug: str, canon_type: str, principal: AuthenticatedPrincipal = Depends(require_ip_read_access)) -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    try:
        path = _canon_path(str(item.get("slug", slug)), canon_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not path.exists():
        raise HTTPException(status_code=404, detail="Canon não encontrado.")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Erro a ler canon: {exc}") from exc

    return {
        "ok": True,
        "slug": slug,
        "canon_type": canon_type,
        "data": data
    }


@router.patch("/{slug}/{canon_type}")
def update_ip_canon(slug: str, canon_type: str, payload: dict, principal: AuthenticatedPrincipal = Depends(require_ip_edit_access)) -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    data = payload.get("data")
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="O campo data tem de ser um objeto JSON.")

    try:
        path = _canon_path(slug, canon_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "ok": True,
        "slug": slug,
        "canon_type": canon_type,
        "saved_to": str(path),
        "data": data
}
