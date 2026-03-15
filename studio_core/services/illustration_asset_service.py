from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.config import resolve_storage_path
from studio_core.core.models import now_iso
from studio_core.core.storage import update_json_item
from studio_core.services.illustration_pipeline_service import get_project_illustration_pipeline

PROJECTS_FILE = "data/projects.json"

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _normalized_ext(filename: str) -> str:
    ext = Path(str(filename or "")).suffix.lower()
    return ext if ext in ALLOWED_EXTENSIONS else ".png"


def _frame_output_dir(project_id: str, frame_type: str) -> Path:
    return resolve_storage_path("exports", project_id, "visuals", frame_type)


def _build_storage_name(frame_id: str, original_filename: str) -> str:
    return f"{frame_id}{_normalized_ext(original_filename)}"


def attach_uploaded_frame_image(
    *,
    project_id: str,
    frame_id: str,
    source_path: str,
    original_filename: str,
) -> Dict[str, Any]:
    pipeline = get_project_illustration_pipeline(project_id)
    frames = _safe_list(pipeline.get("frames", []))
    if not frames:
        raise ValueError("Projeto sem pipeline de ilustração.")

    selected_frame = None
    for item in frames:
        frame = _safe_dict(item)
        if str(frame.get("id", "")).strip() == str(frame_id).strip():
            selected_frame = frame
            break

    if not selected_frame:
        raise ValueError("Frame não encontrado.")

    src = Path(str(source_path or "")).expanduser().resolve()
    if not src.exists() or not src.is_file():
        raise ValueError("Ficheiro fonte não encontrado.")

    frame_type = str(selected_frame.get("frame_type", "book_page")).strip() or "book_page"
    output_dir = _frame_output_dir(project_id, frame_type)
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = _build_storage_name(frame_id, original_filename)
    target_path = output_dir / file_name
    shutil.copy2(src, target_path)

    image_record = {
        "id": str(uuid4()),
        "frame_id": frame_id,
        "frame_type": frame_type,
        "file_name": file_name,
        "file_path": str(target_path),
        "uploaded_at": now_iso(),
    }

    def updater(current: Dict[str, Any]) -> Dict[str, Any]:
        illustration_pipeline = _safe_dict(current.get("illustration_pipeline", {}))
        current_frames = _safe_list(illustration_pipeline.get("frames", []))
        updated_frames = []

        for item in current_frames:
            frame = _safe_dict(item)
            if str(frame.get("id", "")).strip() != str(frame_id).strip():
                updated_frames.append(frame)
                continue

            updated_frames.append({
                **frame,
                "status": "uploaded",
                "approved": True,
                "uploaded_manually": True,
                "image_path": str(target_path),
                "updated_at": now_iso(),
            })

        visuals = _safe_dict(current.get("visuals", {}))
        frame_assets = _safe_list(visuals.get("frame_assets", []))
        frame_assets.append(image_record)

        return {
            **current,
            "illustration_pipeline": {
                **illustration_pipeline,
                "frames": updated_frames,
                "updated_at": now_iso(),
            },
            "visuals": {
                **visuals,
                "frame_assets": frame_assets,
            },
            "updated_at": now_iso(),
        }

    updated_project = update_json_item(PROJECTS_FILE, project_id, updater)

    return {
        "ok": True,
        "asset": image_record,
        "project": updated_project,
    }


def list_approved_frames(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    pipeline = _safe_dict(project.get("illustration_pipeline", {}))
    frames = _safe_list(pipeline.get("frames", []))
    result = []

    for item in frames:
        frame = _safe_dict(item)
        if not bool(frame.get("approved", False)):
            continue
        image_path = str(frame.get("image_path", "")).strip()
        if not image_path:
            continue
        result.append(frame)

    return result


def build_storyboard_manifest(project: Dict[str, Any]) -> Dict[str, Any]:
    approved_frames = list_approved_frames(project)

    entries = []
    for frame in approved_frames:
        entries.append({
            "frame_id": frame.get("id", ""),
            "page_number": frame.get("page_number", 0),
            "page_title": frame.get("page_title", ""),
            "frame_type": frame.get("frame_type", ""),
            "image_path": frame.get("image_path", ""),
            "prompt": frame.get("prompt", ""),
        })

    return {
        "project_id": project.get("id", ""),
        "project_title": project.get("title", ""),
        "saga_slug": project.get("saga_slug", ""),
        "frames_count": len(entries),
        "frames": sorted(entries, key=lambda item: (item.get("page_number", 0), item.get("frame_type", ""))),
        "generated_at": now_iso(),
}
