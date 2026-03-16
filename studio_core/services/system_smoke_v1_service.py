from __future__ import annotations

from typing import Any, Dict, List

from studio_core.core.storage import read_json
from studio_core.services.updater_service import get_local_version_info
from studio_core.services.v1_readiness_service import get_v1_readiness

PROJECTS_FILE = "data/projects.json"
USERS_FILE = "data/users.json"
SETTINGS_FILE = "data/settings.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _pick_first_project() -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    if not isinstance(projects, list) or not projects:
        return None
    return _safe_dict(projects[0])


def run_v1_smoke() -> Dict[str, Any]:
    users = read_json(USERS_FILE, [])
    settings = _safe_dict(read_json(SETTINGS_FILE, {}))
    local_version = get_local_version_info()

    project = _pick_first_project()
    project_id = _safe_text(project.get("id")) if project else ""

    checks = []

    checks.append({
        "key": "users_loaded",
        "label": "Users carregados",
        "ok": isinstance(users, list) and len(users) > 0,
        "count": len(users) if isinstance(users, list) else 0,
    })

    checks.append({
        "key": "settings_loaded",
        "label": "Settings carregadas",
        "ok": bool(settings),
    })

    checks.append({
        "key": "version_loaded",
        "label": "Versão local carregada",
        "ok": bool(_safe_text(local_version.get("version"))),
        "version": _safe_text(local_version.get("version")),
    })

    checks.append({
        "key": "project_exists",
        "label": "Existe pelo menos 1 projeto",
        "ok": bool(project_id),
        "project_id": project_id,
        "project_title": _safe_text(project.get("title")) if project else "",
    })

    readiness = None
    if project_id:
        try:
            readiness = get_v1_readiness(project_id)
            checks.append({
                "key": "v1_readiness",
                "label": "V1 readiness responde",
                "ok": True,
                "status": _safe_text(readiness.get("status")),
                "score": _safe_dict(readiness.get("score")),
            })
        except Exception as exc:
            checks.append({
                "key": "v1_readiness",
                "label": "V1 readiness responde",
                "ok": False,
                "error": str(exc),
            })
    else:
        checks.append({
            "key": "v1_readiness",
            "label": "V1 readiness responde",
            "ok": False,
            "error": "Sem projeto para validar.",
        })

    if project:
        story_layout = _safe_dict(project.get("story_layout", {}))
        story = _safe_dict(project.get("story", {}))
        outputs = _safe_dict(project.get("outputs", {}))
        illustration_pipeline = _safe_dict(project.get("illustration_pipeline", {}))
        audio_cast = _safe_dict(project.get("audio_cast", {}))

        checks.extend([
            {
                "key": "story_layout",
                "label": "Story layout existe",
                "ok": bool(_safe_list(story_layout.get("pages", []))),
                "count": len(_safe_list(story_layout.get("pages", []))),
            },
            {
                "key": "story_applied",
                "label": "Story aplicada existe",
                "ok": bool(_safe_list(story.get("pages", []))),
                "count": len(_safe_list(story.get("pages", []))),
            },
            {
                "key": "illustration_pipeline",
                "label": "Pipeline de ilustração existe",
                "ok": bool(_safe_list(illustration_pipeline.get("frames", []))),
                "count": len(_safe_list(illustration_pipeline.get("frames", []))),
            },
            {
                "key": "covers_output",
                "label": "Output de capa existe",
                "ok": bool(_safe_text(_safe_dict(outputs.get("covers", {})).get("file_path"))),
            },
            {
                "key": "audiobook_output",
                "label": "Output de audiobook existe",
                "ok": bool(_safe_dict(outputs.get("audiobook", {}))),
                "count": len(_safe_dict(outputs.get("audiobook", {}))),
            },
            {
                "key": "audio_cast",
                "label": "Audio cast existe",
                "ok": bool(audio_cast),
            },
        ])

    passed = sum(1 for item in checks if bool(item.get("ok", False)))
    total = len(checks)

    status = "pass" if passed == total else "warning" if passed >= max(1, total - 3) else "fail"

    return {
        "ok": True,
        "status": status,
        "score": {
            "passed": passed,
            "total": total,
        },
        "project_id": project_id,
        "checks": checks,
        "readiness": readiness,
  }
