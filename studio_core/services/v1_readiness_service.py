from __future__ import annotations

from typing import Any, Dict, List

from studio_core.core.storage import read_json

PROJECTS_FILE = "data/projects.json"
VOICE_LIBRARY_FILE = "data/voice_library.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _find_project(project_id: str) -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        row = _safe_dict(project)
        if _safe_text(row.get("id")) == _safe_text(project_id):
            return row
    return None


def get_v1_readiness(project_id: str) -> Dict[str, Any]:
    project = _find_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    story_layout = _safe_dict(project.get("story_layout", {}))
    story_pages = _safe_list(story_layout.get("pages", []))

    story = _safe_dict(project.get("story", {}))
    story_applied_pages = _safe_list(story.get("pages", []))

    outputs = _safe_dict(project.get("outputs", {}))
    audiobook_outputs = _safe_dict(outputs.get("audiobook", {}))
    covers_output = _safe_dict(outputs.get("covers", {}))

    illustration_pipeline = _safe_dict(project.get("illustration_pipeline", {}))
    illustration_frames = _safe_list(illustration_pipeline.get("frames", []))
    approved_frames = [frame for frame in illustration_frames if bool(_safe_dict(frame).get("approved", False))]

    audio_cast = _safe_dict(project.get("audio_cast", {}))
    voice_library = read_json(VOICE_LIBRARY_FILE, [])
    voices_count = len(voice_library) if isinstance(voice_library, list) else 0

    checks = [
        {
            "key": "project_exists",
            "label": "Projeto existe",
            "ok": True,
        },
        {
            "key": "story_layout",
            "label": "Story layout criada",
            "ok": bool(story_layout and story_pages),
            "count": len(story_pages),
        },
        {
            "key": "story_applied",
            "label": "Story aplicada ao projeto",
            "ok": bool(story_applied_pages),
            "count": len(story_applied_pages),
        },
        {
            "key": "illustration_pipeline",
            "label": "Pipeline de ilustração criada",
            "ok": bool(illustration_pipeline and illustration_frames),
            "count": len(illustration_frames),
        },
        {
            "key": "illustration_approved",
            "label": "Frames aprovadas",
            "ok": len(approved_frames) > 0,
            "count": len(approved_frames),
        },
        {
            "key": "cover",
            "label": "Capa gerada",
            "ok": bool(_safe_text(covers_output.get("file_path"))),
            "file_path": _safe_text(covers_output.get("file_path")),
        },
        {
            "key": "audiobook",
            "label": "Audiobook gerado",
            "ok": bool(audiobook_outputs),
            "count": len(audiobook_outputs),
        },
        {
            "key": "voice_library",
            "label": "Biblioteca de vozes disponível",
            "ok": voices_count > 0,
            "count": voices_count,
        },
        {
            "key": "audio_cast",
            "label": "Casting de vozes configurado",
            "ok": bool(audio_cast),
        },
    ]

    passed = sum(1 for item in checks if bool(item.get("ok", False)))
    total = len(checks)

    if passed == total:
        status = "ready"
    elif passed >= max(1, total - 2):
        status = "almost_ready"
    else:
        status = "in_progress"

    return {
        "ok": True,
        "project_id": project_id,
        "project_title": _safe_text(project.get("title")),
        "status": status,
        "score": {
            "passed": passed,
            "total": total,
        },
        "checks": checks,
  }
