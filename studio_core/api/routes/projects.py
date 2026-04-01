from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.core.models import Project, ProjectCreate, ProjectPatch, now_iso
from studio_core.core.storage import append_json_item, list_json_items, update_json_item

router = APIRouter(prefix="/projects", tags=["projects"])

PROJECTS_FILE = "data/projects.json"


def _normalize_name(value: str) -> str:
    return str(value or "").strip().lower()


def _safe_text(value: str) -> str:
    return str(value or "").strip()


def _hidden_key_from_title(value: str) -> str:
    return _safe_text(value).lower().replace(" ", "-")


def _can_view_project(project: dict, user_id: str = "", user_name: str = "", user_role: str = "") -> bool:
    if not bool(project.get("visible_to_owner_only", True)):
        return True

    if not user_id and not user_name:
        return False

    if str(project.get("created_by", "")).strip() == str(user_id).strip():
        return True

    if _normalize_name(project.get("created_by_name", "")) == _normalize_name(user_name):
        return True

    return False


def _can_edit_or_publish(user_role: str, user_name: str) -> bool:
    role = str(user_role or "").strip().lower()
    name = _normalize_name(user_name)
    return role in {"owner", "creator", "admin"} or name in {"andré", "andre", "esposa", "wife", "mama"}


@router.get("")
def list_projects(user_id: str = "", user_name: str = "", user_role: str = "") -> dict:
    projects = list_json_items(PROJECTS_FILE)
    visible = [
        project for project in projects
        if _can_view_project(project, user_id=user_id, user_name=user_name, user_role=user_role)
    ]
    return {"ok": True, "projects": visible}


@router.post("")
def create_project(payload: ProjectCreate) -> dict:
    project_mode = _safe_text(payload.project_mode) or "official"
    is_hidden_mode = project_mode in {"standalone", "hidden_continuity", "hidden_ip", "hidden_saga"}

    hidden_universe_name = _safe_text(payload.hidden_universe_name)
    hidden_universe_key = _safe_text(payload.hidden_universe_key)
    hidden_saga_name = _safe_text(payload.hidden_saga_name)
    hidden_saga_key = _safe_text(payload.hidden_saga_key)

    if is_hidden_mode:
        if not hidden_universe_name:
            hidden_universe_name = payload.title.strip()
        if not hidden_universe_key:
            hidden_universe_key = _hidden_key_from_title(hidden_universe_name)
        if not hidden_saga_name:
            hidden_saga_name = hidden_universe_name
        if not hidden_saga_key:
            hidden_saga_key = _hidden_key_from_title(hidden_saga_name)

    project = Project(
        title=payload.title.strip(),
        saga_slug=payload.saga_slug.strip(),
        saga_name=payload.saga_name.strip(),
        language=payload.language.strip(),
        output_languages=payload.output_languages or [payload.language.strip()],
        created_by=payload.created_by.strip(),
        created_by_name=payload.created_by_name.strip(),
        visible_to_owner_only=payload.visible_to_owner_only,
        project_mode=project_mode,
        parent_project_id=_safe_text(payload.parent_project_id),
        continuity_source_project_id=_safe_text(payload.continuity_source_project_id),
        hidden_universe_key=hidden_universe_key,
        hidden_universe_name=hidden_universe_name,
        hidden_saga_key=hidden_saga_key,
        hidden_saga_name=hidden_saga_name,
        continuity={
            "can_promote_to_official_ip": True,
            "officialization_status": "hidden" if is_hidden_mode else "official",
            "suggested_title_origin": "manual_or_future_ai",
            "continuity_character_names": [],
            "continuity_notes": "",
        },
        story={
            "title": payload.title.strip(),
            "language": payload.language.strip(),
            "pages": [],
            "raw_text": ""
        }
    )

    append_json_item(PROJECTS_FILE, project.model_dump())
    return {"ok": True, "project": project.model_dump()}


@router.patch("/{project_id}")
def patch_project(project_id: str, payload: ProjectPatch, user_name: str = "", user_role: str = "") -> dict:
    if not _can_edit_or_publish(user_role, user_name):
        raise HTTPException(status_code=403, detail="Sem permissão editorial para editar projetos.")

    def updater(current: dict) -> dict:
        updated = {
            **current,
            "updated_at": now_iso(),
        }

        if payload.title is not None:
            updated["title"] = payload.title.strip()

        if payload.saga_slug is not None:
            updated["saga_slug"] = payload.saga_slug.strip()

        if payload.saga_name is not None:
            updated["saga_name"] = payload.saga_name.strip()

        if payload.language is not None:
            updated["language"] = payload.language.strip()

        if payload.output_languages is not None:
            updated["output_languages"] = payload.output_languages

        if payload.status is not None:
            updated["status"] = payload.status

        if payload.editorial_status is not None:
            updated["editorial_status"] = payload.editorial_status

        if payload.cover_image is not None:
            updated["cover_image"] = payload.cover_image

        if payload.illustration_path is not None:
            updated["illustration_path"] = payload.illustration_path

        if payload.project_mode is not None:
            updated["project_mode"] = payload.project_mode

        if payload.parent_project_id is not None:
            updated["parent_project_id"] = payload.parent_project_id

        if payload.continuity_source_project_id is not None:
            updated["continuity_source_project_id"] = payload.continuity_source_project_id

        if payload.hidden_universe_key is not None:
            updated["hidden_universe_key"] = payload.hidden_universe_key

        if payload.hidden_universe_name is not None:
            updated["hidden_universe_name"] = payload.hidden_universe_name

        if payload.hidden_saga_key is not None:
            updated["hidden_saga_key"] = payload.hidden_saga_key

        if payload.hidden_saga_name is not None:
            updated["hidden_saga_name"] = payload.hidden_saga_name

        if payload.commercial is not None:
            updated["commercial"] = {
                **(current.get("commercial", {}) or {}),
                **payload.commercial
            }

        if payload.front_matter is not None:
            updated["front_matter"] = {
                **current.get("front_matter", {}),
                **payload.front_matter
            }

        if payload.story is not None:
            updated["story"] = {
                **current.get("story", {}),
                **payload.story
            }

        if payload.continuity is not None:
            updated["continuity"] = {
                **(current.get("continuity", {}) or {}),
                **payload.continuity
            }

        return updated

    try:
        project = update_json_item(PROJECTS_FILE, project_id, updater)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {"ok": True, "project": project}
