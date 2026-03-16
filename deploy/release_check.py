from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DEPLOY_DIR = ROOT / "deploy"


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _pick_first_project() -> Dict[str, Any] | None:
    projects = _read_json(DATA_DIR / "projects.json", [])
    if not isinstance(projects, list) or not projects:
        return None
    return _safe_dict(projects[0])


def run_release_check() -> Dict[str, Any]:
    manifest = _safe_dict(_read_json(DEPLOY_DIR / "release_manifest.json", {}))
    version_info = _safe_dict(_read_json(DEPLOY_DIR / "version.json", {}))
    projects = _read_json(DATA_DIR / "projects.json", [])
    users = _read_json(DATA_DIR / "users.json", [])
    settings = _safe_dict(_read_json(DATA_DIR / "settings.json", {}))
    voice_library = _read_json(DATA_DIR / "voice_library.json", [])

    project = _pick_first_project()
    outputs = _safe_dict(project.get("outputs", {})) if project else {}
    story_layout = _safe_dict(project.get("story_layout", {})) if project else {}
    story = _safe_dict(project.get("story", {})) if project else {}
    illustration_pipeline = _safe_dict(project.get("illustration_pipeline", {})) if project else {}

    checks = [
        {
            "key": "manifest_exists",
            "label": "release_manifest.json existe",
            "ok": bool(manifest),
        },
        {
            "key": "version_exists",
            "label": "version.json existe",
            "ok": bool(version_info),
        },
        {
            "key": "version_matches_target",
            "label": "version.json bate com target_version",
            "ok": _safe_text(version_info.get("version")) == _safe_text(manifest.get("target_version")),
            "current_version": _safe_text(version_info.get("version")),
            "target_version": _safe_text(manifest.get("target_version")),
        },
        {
            "key": "users_exist",
            "label": "users.json tem utilizadores",
            "ok": isinstance(users, list) and len(users) > 0,
            "count": len(users) if isinstance(users, list) else 0,
        },
        {
            "key": "settings_exist",
            "label": "settings.json existe e tem conteúdo",
            "ok": bool(settings),
        },
        {
            "key": "project_exists",
            "label": "há pelo menos 1 projeto",
            "ok": bool(project),
            "project_title": _safe_text(project.get("title")) if project else "",
        },
        {
            "key": "story_layout",
            "label": "story_layout pronta",
            "ok": bool(_safe_list(story_layout.get("pages", []))),
            "count": len(_safe_list(story_layout.get("pages", []))),
        },
        {
            "key": "story_applied",
            "label": "story aplicada pronta",
            "ok": bool(_safe_list(story.get("pages", []))),
            "count": len(_safe_list(story.get("pages", []))),
        },
        {
            "key": "illustration_pipeline",
            "label": "pipeline de ilustração pronta",
            "ok": bool(_safe_list(illustration_pipeline.get("frames", []))),
            "count": len(_safe_list(illustration_pipeline.get("frames", []))),
        },
        {
            "key": "cover_output",
            "label": "cover output pronta",
            "ok": bool(_safe_text(_safe_dict(outputs.get("covers", {})).get("file_path"))),
        },
        {
            "key": "audiobook_output",
            "label": "audiobook output pronta",
            "ok": bool(_safe_dict(outputs.get("audiobook", {}))),
            "count": len(_safe_dict(outputs.get("audiobook", {}))),
        },
        {
            "key": "voice_library",
            "label": "biblioteca de vozes existe",
            "ok": isinstance(voice_library, list) and len(voice_library) >= 0,
            "count": len(voice_library) if isinstance(voice_library, list) else 0,
        },
    ]

    passed = sum(1 for item in checks if item.get("ok"))
    total = len(checks)
    minimum = int(manifest.get("minimum_checks_passed", 8) or 8)

    status = "ready" if passed >= minimum else "not_ready"

    result = {
        "status": status,
        "score": {
            "passed": passed,
            "total": total,
            "minimum_required": minimum,
        },
        "checks": checks,
    }

    return result


if __name__ == "__main__":
    result = run_release_check()
    print(json.dumps(result, indent=2, ensure_ascii=False))
