from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.models import now_iso
from studio_core.core.storage import append_json_item, list_json_items, read_json, update_json_item

SPONSORSHIP_SCOPES_FILE = "data/sponsorship_scopes.json"
PROJECTS_FILE = "data/projects.json"
ALLOWED_SCOPE_TYPES = {"studio_global", "ip", "saga", "product", "campaign"}


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _get_project(project_id: str) -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    for item in projects:
        if _safe_text(item.get("id")) == _safe_text(project_id):
            return item
    return None


def list_sponsorship_scopes() -> List[Dict[str, Any]]:
    return list_json_items(SPONSORSHIP_SCOPES_FILE)


def _normalize_scope(payload: Dict[str, Any], current: Dict[str, Any] | None = None) -> Dict[str, Any]:
    current = current or {}
    scope_type = _safe_text(payload.get("scope_type", current.get("scope_type") or "studio_global")) or "studio_global"
    if scope_type not in ALLOWED_SCOPE_TYPES:
        raise ValueError("scope_type_invalid")

    return {
        "id": _safe_text(current.get("id")) or f"sponsorship-scope-{uuid4()}",
        "sponsor_id": _safe_text(payload.get("sponsor_id", current.get("sponsor_id"))),
        "name": _safe_text(payload.get("name", current.get("name"))),
        "scope_type": scope_type,
        "scope_target_id": _safe_text(payload.get("scope_target_id", current.get("scope_target_id"))),
        "scope_target_slug": _safe_text(payload.get("scope_target_slug", current.get("scope_target_slug"))),
        "active": bool(payload.get("active", current.get("active", True))),
        "exclusive": bool(payload.get("exclusive", current.get("exclusive", False))),
        "priority": int(payload.get("priority", current.get("priority", 100)) or 100),
        "credit_text": _safe_text(payload.get("credit_text", current.get("credit_text"))),
        "cta_text": _safe_text(payload.get("cta_text", current.get("cta_text"))),
        "cta_url": _safe_text(payload.get("cta_url", current.get("cta_url"))),
        "logo_asset": _safe_text(payload.get("logo_asset", current.get("logo_asset"))),
        "placement_rules": _safe_list(payload.get("placement_rules", current.get("placement_rules"))),
        "internal_notes": _safe_text(payload.get("internal_notes", current.get("internal_notes"))),
        "start_at": _safe_text(payload.get("start_at", current.get("start_at"))),
        "end_at": _safe_text(payload.get("end_at", current.get("end_at"))),
        "created_at": current.get("created_at") or now_iso(),
        "updated_at": now_iso(),
    }


def create_sponsorship_scope(payload: Dict[str, Any]) -> Dict[str, Any]:
    item = _normalize_scope(payload)
    return append_json_item(SPONSORSHIP_SCOPES_FILE, item)


def patch_sponsorship_scope(scope_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    current = None
    for item in list_sponsorship_scopes():
        if _safe_text(item.get("id")) == _safe_text(scope_id):
            current = item
            break
    if not current:
        raise ValueError("sponsorship_scope_not_found")
    return update_json_item(SPONSORSHIP_SCOPES_FILE, current["id"], lambda row: _normalize_scope(payload, row))


def resolve_sponsorship_for_project(project_id: str) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    saga_slug = _safe_text(project.get("saga_slug"))
    candidates = []
    for item in list_sponsorship_scopes():
        row = _safe_dict(item)
        if not row.get("active", False):
            continue
        scope_type = _safe_text(row.get("scope_type"))
        target_id = _safe_text(row.get("scope_target_id"))
        target_slug = _safe_text(row.get("scope_target_slug"))
        matches = False
        if scope_type == "studio_global":
            matches = True
        elif scope_type == "product" and target_id == _safe_text(project_id):
            matches = True
        elif scope_type in {"ip", "saga"} and target_slug == saga_slug:
            matches = True
        if matches:
            candidates.append(row)

    precedence = {"product": 1, "campaign": 2, "saga": 3, "ip": 4, "studio_global": 5}
    candidates.sort(key=lambda row: (precedence.get(_safe_text(row.get("scope_type")), 99), int(row.get("priority", 100))))

    selected = None
    if candidates:
        selected = candidates[0]
        if selected.get("exclusive"):
            candidates = [selected]

    return {
        "ok": True,
        "project_id": project_id,
        "resolved": selected,
        "candidates": candidates,
    }
