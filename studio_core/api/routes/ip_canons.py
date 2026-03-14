from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from studio_core.core.config import resolve_project_path
from studio_core.services.ip_creator_service import can_edit_ip, get_ip_by_slug

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


def _user_from_payload_or_query(payload: dict | None = None, user_id: str = "", user_name: str = "", user_role: str = "") -> dict:
    payload = payload or {}
    return {
        "id": str(payload.get("user_id", user_id)).strip(),
        "name": str(payload.get("user_name", user_name)).strip(),
        "role": str(payload.get("user_role", user_role)).strip()
    }


def _canon_path(slug: str, canon_type: str) -> Path:
    file_name = VALID_CANONS.get(canon_type)
    if not file_name:
        raise ValueError("canon_type inválido.")
    return resolve_project_path("studio", "sagas", slug, file_name)


@router.get("/{slug}/{canon_type}")
def get_ip_canon(slug: str, canon_type: str, user_id: str = "", user_name: str = "", user_role: str = "") -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    user = _user_from_payload_or_query(user_id=user_id, user_name=user_name, user_role=user_role)
    if not can_edit_ip(user, slug):
        raise HTTPException(status_code=403, detail="Sem permissão para ver este canon.")

    try:
        path = _canon_path(slug, canon_type)
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
def update_ip_canon(slug: str, canon_type: str, payload: dict) -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    user = _user_from_payload_or_query(payload)
    if not can_edit_ip(user, slug):
        raise HTTPException(status_code=403, detail="Sem permissão para editar este canon.")

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
