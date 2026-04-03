from __future__ import annotations

from studio_core.core.storage import list_json_items

PROJECTS_FILE = "data/projects.json"


def _normalize_name(value: str) -> str:
    return str(value or "").strip().lower()


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


def list_projects(user_id: str | None = "", user_name: str = "", user_role: str = "") -> dict:
    projects = list_json_items(PROJECTS_FILE)
    visible = [
        project
        for project in projects
        if _can_view_project(
            project,
            user_id=str(user_id or ""),
            user_name=user_name,
            user_role=user_role,
        )
    ]
    return {"ok": True, "projects": visible}
