from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item
from studio_core.services.ip_creator_service import get_ip_by_slug
from studio_core.services.production_readiness_service import (
    get_production_readiness,
    sync_ready_for_publish_with_readiness,
)

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


def _safe_list(value):
    return value if isinstance(value, list) else []


def _safe_dict(value):
    return value if isinstance(value, dict) else {}


def _blank(value) -> bool:
    return str(value or "").strip() == ""


def _character_consistency_report(char: dict) -> dict:
    visual_identity = _safe_dict(char.get("visual_identity"))
    wardrobe_identity = _safe_dict(char.get("wardrobe_identity"))
    consistency_rules = _safe_dict(char.get("consistency_rules"))
    prompt_guardrails = _safe_dict(char.get("prompt_guardrails"))
    reference_assets = _safe_dict(char.get("reference_assets"))

    missing = []

    if _blank(char.get("name")):
        missing.append("name")
    if _blank(char.get("role")):
        missing.append("role")
    if _blank(char.get("archetype")):
        missing.append("archetype")
    if len(_safe_list(char.get("traits"))) == 0:
        missing.append("traits")
    if _blank(char.get("accent_color")):
        missing.append("accent_color")
    if _blank(char.get("signature_item")):
        missing.append("signature_item")

    for key in ["species", "body_shape", "fur_primary", "hair_style", "eye_shape", "eye_color", "beard_style"]:
        if _blank(visual_identity.get(key)):
            missing.append(f"visual_identity.{key}")

    if len(_safe_list(visual_identity.get("distinctive_marks"))) == 0:
        missing.append("visual_identity.distinctive_marks")
    if len(_safe_list(visual_identity.get("silhouette_keywords"))) == 0:
        missing.append("visual_identity.silhouette_keywords")

    if _blank(wardrobe_identity.get("core_outfit")):
        missing.append("wardrobe_identity.core_outfit")
    if len(_safe_list(wardrobe_identity.get("forbidden_changes"))) == 0:
        missing.append("wardrobe_identity.forbidden_changes")

    for key in ["must_keep", "never_change"]:
        if len(_safe_list(consistency_rules.get(key))) == 0:
            missing.append(f"consistency_rules.{key}")

    for key in ["positive", "negative"]:
        if len(_safe_list(prompt_guardrails.get(key))) == 0:
            missing.append(f"prompt_guardrails.{key}")

    for key in ["front", "expression_sheet"]:
        if _blank(reference_assets.get(key)):
            missing.append(f"reference_assets.{key}")

    return {
        "id": str(char.get("id", "")).strip(),
        "name": str(char.get("name", "")).strip(),
        "status": "complete" if len(missing) == 0 else "needs_attention",
        "missing": missing,
    }


def _character_lock_status_for_project(project: dict) -> dict:
    saga_slug = str(project.get("saga_slug", "")).strip()
    ip_item = get_ip_by_slug(saga_slug) if saga_slug else None

    if not ip_item:
        return {
            "applicable": False,
            "character_lock_ready": True,
            "blocking_items": [],
            "label": "Sem IP associada",
        }

    reports = [_character_consistency_report(char) for char in _safe_list(ip_item.get("main_characters")) if isinstance(char, dict)]
    blocking_items = [item for item in reports if item.get("status") != "complete"]
    ready = len(reports) > 0 and len(blocking_items) == 0

    return {
        "applicable": True,
        "saga_slug": saga_slug,
        "character_lock_ready": ready,
        "blocking_items": blocking_items,
        "label": "Character lock pronto" if ready else "Character lock bloqueado",
    }


def _compose_readiness(project: dict) -> dict:
    readiness = get_production_readiness(str(project.get("id", "")))
    character_lock = _character_lock_status_for_project(project)
    package_ready = bool(_safe_dict(readiness.get("package_readiness")).get("ready", False))
    operational_ready = float(readiness.get("ratio", 0)) >= 0.75
    ready = bool(package_ready and operational_ready and character_lock.get("character_lock_ready", True))

    return {
        **readiness,
        "ready": ready,
        "operational_ready": operational_ready,
        "package_ready": package_ready,
        "character_lock": character_lock,
    }


@router.get("/{project_id}")
def get_publish_readiness(project_id: str) -> dict:
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    readiness = _compose_readiness(project)

    return {
        "ok": True,
        "project_id": project_id,
        "readiness": readiness,
        "ready_for_publish": bool(project.get("ready_for_publish", False)),
    }


@router.post("/{project_id}/sync")
def sync_publish_readiness(project_id: str, user_name: str = "", user_role: str = "") -> dict:
    if not _can_edit_or_publish(user_role, user_name):
        raise HTTPException(status_code=403, detail="Sem permissão para sincronizar prontidão.")

    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    sync_payload = sync_ready_for_publish_with_readiness(project_id)
    refreshed_project = _get_project(project_id)
    readiness = _compose_readiness(refreshed_project or project)

    return {
        "ok": True,
        "project_id": project_id,
        "ready_for_publish": bool(sync_payload.get("ready_for_publish", False)),
        "readiness": readiness,
    }


@router.post("/{project_id}/mark-ready")
def mark_ready(project_id: str, user_name: str = "", user_role: str = "") -> dict:
    if not _can_edit_or_publish(user_role, user_name):
        raise HTTPException(status_code=403, detail="Sem permissão para marcar como pronto.")

    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    readiness = _compose_readiness(project)

    if not readiness.get("operational_ready", False):
        raise HTTPException(
            status_code=400,
            detail=f"Projeto ainda não está operacionalmente pronto. Estado: {readiness.get('label', 'Não pronto')}."
        )

    if not readiness.get("package_ready", False):
        raise HTTPException(
            status_code=400,
            detail="Projeto ainda não tem publication package pronto para publicação."
        )

    if not _safe_dict(readiness.get("character_lock")).get("character_lock_ready", True):
        raise HTTPException(
            status_code=400,
            detail="Projeto bloqueado por character lock da saga. Fecha a consistência visual dos personagens principais antes de marcar como pronto."
        )

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "ready_for_publish": True,
            "ready_for_publish_at": now_iso(),
            "production_readiness": readiness,
            "production_readiness_synced_at": now_iso(),
            "updated_at": now_iso(),
        }
    )

    return {
        "ok": True,
        "project_id": project_id,
        "ready_for_publish": updated.get("ready_for_publish", False),
        "ready_for_publish_at": updated.get("ready_for_publish_at", ""),
        "readiness": readiness,
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
            "updated_at": now_iso(),
        }
    )

    return {
        "ok": True,
        "project_id": project_id,
        "ready_for_publish": updated.get("ready_for_publish", False),
    }
