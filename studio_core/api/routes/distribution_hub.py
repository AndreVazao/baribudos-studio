from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, write_json

router = APIRouter(prefix="/distribution", tags=["distribution"])

PROJECTS_FILE = "data/projects.json"
DISTRIBUTION_FILE = "data/distribution_channel_states.json"

ALLOWED_STATUSES = {"draft", "planned", "queued", "ready", "published", "failed"}
ALLOWED_CHANNELS = {"website", "amazon_kdp", "youtube", "audio"}


def _normalize_name(value: str) -> str:
    return str(value or "").strip().lower()


def _can_edit_or_publish(user_role: str, user_name: str) -> bool:
    role = str(user_role or "").strip().lower()
    name = _normalize_name(user_name)
    return role in {"owner", "creator", "admin"} or name in {"andré", "andre", "esposa", "wife", "mama"}


def _read_projects() -> list[dict]:
    data = read_json(PROJECTS_FILE, [])
    return data if isinstance(data, list) else []


def _read_states() -> list[dict]:
    data = read_json(DISTRIBUTION_FILE, [])
    return data if isinstance(data, list) else []


def _write_states(items: list[dict]) -> list[dict]:
    write_json(DISTRIBUTION_FILE, items)
    return items


def _get_project(project_id: str) -> dict | None:
    for project in _read_projects():
        if str(project.get("id", "")) == str(project_id):
            return project
    return None


def _find_state(items: list[dict], project_id: str, channel_id: str) -> dict | None:
    for item in items:
        if str(item.get("project_id", "")) == str(project_id) and str(item.get("channel_id", "")) == str(channel_id):
            return item
    return None


def _build_default_state(project_id: str, channel_id: str) -> dict:
    timestamp = now_iso()
    return {
        "id": f"{project_id}:{channel_id}",
        "project_id": str(project_id),
        "channel_id": str(channel_id),
        "status": "draft",
        "attempt_count": 0,
        "last_attempt_at": "",
        "last_error": "",
        "ready_at": "",
        "published_at": "",
        "notes": "",
        "payload_snapshot_json": {},
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def _ensure_state(project_id: str, channel_id: str) -> dict:
    if channel_id not in ALLOWED_CHANNELS:
        raise HTTPException(status_code=400, detail="channel_id inválido.")

    items = _read_states()
    current = _find_state(items, project_id, channel_id)
    if current:
        return current

    created = _build_default_state(project_id, channel_id)
    items.append(created)
    _write_states(items)
    return created


def _replace_state(project_id: str, channel_id: str, updater) -> dict:
    items = _read_states()
    updated_item = None
    found = False
    next_items: list[dict] = []

    for item in items:
        if str(item.get("project_id", "")) == str(project_id) and str(item.get("channel_id", "")) == str(channel_id):
            updated_item = updater(item)
            next_items.append(updated_item)
            found = True
        else:
            next_items.append(item)

    if not found:
        base = _build_default_state(project_id, channel_id)
        updated_item = updater(base)
        next_items.append(updated_item)

    _write_states(next_items)
    return updated_item


@router.get("/projects/{project_id}/channels")
def list_distribution_channels(project_id: str) -> dict:
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    items = _read_states()
    results = [item for item in items if str(item.get("project_id", "")) == str(project_id)]

    existing_channels = {str(item.get("channel_id", "")) for item in results}
    for channel_id in sorted(ALLOWED_CHANNELS):
        if channel_id not in existing_channels:
            results.append(_build_default_state(project_id, channel_id))

    return {
        "ok": True,
        "project_id": project_id,
        "channels": results,
    }


@router.get("/projects/{project_id}/channels/{channel_id}")
def get_distribution_channel(project_id: str, channel_id: str) -> dict:
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    state = _ensure_state(project_id, channel_id)
    return {
        "ok": True,
        "project_id": project_id,
        "channel": state,
    }


@router.patch("/projects/{project_id}/channels/{channel_id}")
def patch_distribution_channel(project_id: str, channel_id: str, payload: Dict[str, Any], user_name: str = "", user_role: str = "") -> dict:
    if not _can_edit_or_publish(user_role, user_name):
        raise HTTPException(status_code=403, detail="Sem permissão para operar canais de distribuição.")

    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    status = payload.get("status")
    if status is not None and status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail="status inválido.")

    notes = payload.get("notes")
    payload_snapshot_json = payload.get("payload_snapshot_json")
    if payload_snapshot_json is not None and not isinstance(payload_snapshot_json, dict):
        raise HTTPException(status_code=400, detail="payload_snapshot_json inválido.")

    updated = _replace_state(
        project_id,
        channel_id,
        lambda current: {
            **current,
            "status": status if status is not None else current.get("status", "draft"),
            "notes": str(notes) if notes is not None else current.get("notes", ""),
            "payload_snapshot_json": payload_snapshot_json if payload_snapshot_json is not None else current.get("payload_snapshot_json", {}),
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "project_id": project_id,
        "channel": updated,
    }


@router.post("/projects/{project_id}/channels/{channel_id}/attempts")
def record_distribution_attempt(project_id: str, channel_id: str, payload: Dict[str, Any], user_name: str = "", user_role: str = "") -> dict:
    if not _can_edit_or_publish(user_role, user_name):
        raise HTTPException(status_code=403, detail="Sem permissão para registar tentativa.")

    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    attempted_at = str(payload.get("attempted_at") or now_iso())
    notes = payload.get("notes")

    updated = _replace_state(
        project_id,
        channel_id,
        lambda current: {
            **current,
            "attempt_count": int(current.get("attempt_count", 0)) + 1,
            "last_attempt_at": attempted_at,
            "notes": str(notes) if notes is not None else current.get("notes", ""),
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "project_id": project_id,
        "channel": updated,
    }


@router.post("/projects/{project_id}/channels/{channel_id}/publish-success")
def mark_distribution_publish_success(project_id: str, channel_id: str, payload: Dict[str, Any], user_name: str = "", user_role: str = "") -> dict:
    if not _can_edit_or_publish(user_role, user_name):
        raise HTTPException(status_code=403, detail="Sem permissão para marcar sucesso.")

    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    published_at = str(payload.get("published_at") or now_iso())
    notes = payload.get("notes")

    updated = _replace_state(
        project_id,
        channel_id,
        lambda current: {
            **current,
            "status": "published",
            "published_at": published_at,
            "last_error": "",
            "notes": str(notes) if notes is not None else current.get("notes", ""),
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "project_id": project_id,
        "channel": updated,
    }


@router.post("/projects/{project_id}/channels/{channel_id}/publish-failed")
def mark_distribution_publish_failed(project_id: str, channel_id: str, payload: Dict[str, Any], user_name: str = "", user_role: str = "") -> dict:
    if not _can_edit_or_publish(user_role, user_name):
        raise HTTPException(status_code=403, detail="Sem permissão para marcar falha.")

    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    error = str(payload.get("error") or "Erro desconhecido")
    notes = payload.get("notes")

    updated = _replace_state(
        project_id,
        channel_id,
        lambda current: {
            **current,
            "status": "failed",
            "last_error": error,
            "notes": str(notes) if notes is not None else current.get("notes", ""),
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "project_id": project_id,
        "channel": updated,
    }
