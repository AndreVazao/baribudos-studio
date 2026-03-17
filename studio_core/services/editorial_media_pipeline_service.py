from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.config import resolve_storage_path
from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item
from studio_core.services.illustration_provider_service import generate_illustration

PROJECTS_FILE = "data/projects.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _get_project(project_id: str) -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        row = _safe_dict(project)
        if _safe_text(row.get("id")) == _safe_text(project_id):
            return row
    return None


def generate_editorial_illustrations(
    project_id: str,
    provider: str = "",
) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    pipeline = _safe_dict(project.get("illustration_pipeline", {}))
    frames = [_safe_dict(item) for item in _safe_list(pipeline.get("frames", []))]
    if not frames:
        raise ValueError("Sem fila de ilustrações.")

    updated_frames: List[Dict[str, Any]] = []

    for frame in frames:
        image_path = _safe_text(frame.get("image_path"))
        if image_path:
            updated_frames.append(frame)
            continue

        prompt = _safe_text(frame.get("prompt"))
        excerpt = _safe_text(frame.get("excerpt"))
        final_prompt = prompt
        if excerpt:
            final_prompt = f"{prompt}. Scene excerpt: {excerpt}".strip(". ")

        result = generate_illustration(
            prompt=final_prompt,
            provider=provider or None,
            saga_style={},
        )

        updated_frames.append({
            **frame,
            "image_path": _safe_text(result.get("file_path")),
            "provider": _safe_text(result.get("provider")),
            "updated_at": now_iso(),
        })

    updated_pipeline = {
        **pipeline,
        "frames": updated_frames,
        "frames_count": len(updated_frames),
        "generated_count": len([x for x in updated_frames if _safe_text(x.get("image_path"))]),
        "updated_at": now_iso(),
    }

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "illustration_pipeline": updated_pipeline,
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "pipeline": updated_pipeline,
        "project": updated,
    }


def _copy_or_placeholder_image(
    image_path: str,
    target_path: Path,
) -> str:
    target_path.parent.mkdir(parents=True, exist_ok=True)

    src = Path(_safe_text(image_path))
    if src.exists() and src.is_file():
        target_path.write_bytes(src.read_bytes())
        return str(target_path)

    target_path.write_bytes(b"")
    return str(target_path)


def build_video_package_from_storyboard(project_id: str) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    storyboard = _safe_dict(project.get("series_storyboard", {}))
    shots = [_safe_dict(item) for item in _safe_list(storyboard.get("shots", []))]
    if not shots:
        raise ValueError("Sem storyboard.")

    pipeline = _safe_dict(project.get("illustration_pipeline", {}))
    frames = [_safe_dict(item) for item in _safe_list(pipeline.get("frames", []))]

    frame_map = {
        int(_safe_dict(frame).get("page_number", 0) or 0): _safe_dict(frame)
        for frame in frames
    }

    export_dir = resolve_storage_path("exports", project_id, "video_storyboard")
    export_dir.mkdir(parents=True, exist_ok=True)

    slides: List[Dict[str, Any]] = []

    for shot in shots:
        scene_number = int(shot.get("scene_number", 0) or 0)
        frame = frame_map.get(scene_number, {})
        source_image = _safe_text(frame.get("image_path"))

        image_name = f"scene_{scene_number:03d}.png"
        local_image_path = export_dir / image_name
        local_image = _copy_or_placeholder_image(source_image, local_image_path)

        slides.append({
            "id": str(uuid4()),
            "scene_number": scene_number,
            "title": _safe_text(shot.get("shot_title")),
            "narration": _safe_text(shot.get("narration")),
            "visual_prompt": _safe_text(shot.get("visual_prompt")),
            "duration_seconds": int(shot.get("duration_seconds", 6) or 6),
            "transition": _safe_text(shot.get("transition", "fade")) or "fade",
            "audio_mode": _safe_text(shot.get("audio_mode", "narration")) or "narration",
            "image_path": local_image,
            "image_file": image_name,
        })

    video_package = {
        "id": str(uuid4()),
        "title": f"{_safe_text(project.get('title'))} Video Package",
        "source": "series_storyboard",
        "slides": slides,
        "slides_count": len(slides),
        "export_dir": str(export_dir),
        "updated_at": now_iso(),
    }

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "video_storyboard_package": video_package,
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "video_package": video_package,
        "project": updated,
      }
