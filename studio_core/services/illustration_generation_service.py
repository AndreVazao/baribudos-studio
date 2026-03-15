from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.models import now_iso
from studio_core.core.storage import append_json_item, read_json, update_json_item
from studio_core.services.illustration_asset_service import attach_uploaded_frame_image
from studio_core.services.illustration_pipeline_service import get_project_illustration_pipeline

PROJECTS_FILE = "data/projects.json"
ILLUSTRATION_JOBS_FILE = "data/illustration_jobs.json"

JOB_STATES = {
    "queued",
    "generating",
    "generated",
    "approved",
    "failed",
    "skipped",
}


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _normalize_state(value: str) -> str:
    text = str(value or "").strip().lower()
    return text if text in JOB_STATES else "queued"


def _get_project(project_id: str) -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        if str(project.get("id", "")).strip() == str(project_id).strip():
            return project
    return None


def _selected_frames_from_pipeline(pipeline: Dict[str, Any]) -> List[Dict[str, Any]]:
    frames = _safe_list(pipeline.get("frames", []))
    result = []
    for item in frames:
        frame = _safe_dict(item)
        if not bool(frame.get("selected", False)):
            continue
        result.append(frame)
    return result


def queue_illustration_generation(project_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    pipeline = get_project_illustration_pipeline(project_id)
    if not pipeline:
        raise ValueError("Projeto sem pipeline de ilustração.")

    selected_frames = _selected_frames_from_pipeline(pipeline)
    if not selected_frames:
        raise ValueError("Nenhum frame selecionado na pipeline de ilustração.")

    jobs = []
    for frame in selected_frames:
        job = {
            "id": str(uuid4()),
            "project_id": project_id,
            "frame_id": frame.get("id", ""),
            "page_number": frame.get("page_number", 0),
            "frame_type": frame.get("frame_type", ""),
            "prompt": frame.get("prompt", ""),
            "mode": pipeline.get("mode", "approval"),
            "language": pipeline.get("language", ""),
            "state": "queued",
            "provider": str(payload.get("provider", "external")).strip() or "external",
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }
        append_json_item(ILLUSTRATION_JOBS_FILE, job)
        jobs.append(job)

    update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "illustration_generation": {
                "queued_at": now_iso(),
                "jobs_count": len(jobs),
                "provider": str(payload.get("provider", "external")).strip() or "external",
                "state": "queued",
            },
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "project_id": project_id,
        "jobs_count": len(jobs),
        "jobs": jobs,
    }


def list_illustration_jobs(project_id: str = "") -> List[Dict[str, Any]]:
    jobs = read_json(ILLUSTRATION_JOBS_FILE, [])
    if not isinstance(jobs, list):
        return []

    if not project_id:
        return jobs

    return [
        item for item in jobs
        if str(_safe_dict(item).get("project_id", "")).strip() == str(project_id).strip()
    ]


def update_illustration_job(job_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    jobs = read_json(ILLUSTRATION_JOBS_FILE, [])
    if not isinstance(jobs, list):
        jobs = []

    updated_job = None
    updated_jobs = []

    for item in jobs:
        job = _safe_dict(item)
        if str(job.get("id", "")).strip() != str(job_id).strip():
            updated_jobs.append(job)
            continue

        updated_job = {
            **job,
            "state": _normalize_state(payload.get("state", job.get("state", "queued"))),
            "provider": str(payload.get("provider", job.get("provider", "external"))).strip() or "external",
            "updated_at": now_iso(),
        }
        updated_jobs.append(updated_job)

    if not updated_job:
        raise ValueError("Job não encontrado.")

    from studio_core.core.storage import write_json
    write_json(ILLUSTRATION_JOBS_FILE, updated_jobs)

    return {
        "ok": True,
        "job": updated_job,
    }


def export_illustration_prompt_package(project_id: str) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    pipeline = get_project_illustration_pipeline(project_id)
    if not pipeline:
        raise ValueError("Projeto sem pipeline de ilustração.")

    selected_frames = _selected_frames_from_pipeline(pipeline)

    package = {
        "project_id": project_id,
        "project_title": project.get("title", ""),
        "saga_slug": project.get("saga_slug", ""),
        "mode": pipeline.get("mode", ""),
        "language": pipeline.get("language", ""),
        "frames_count": len(selected_frames),
        "frames": [
            {
                "frame_id": frame.get("id", ""),
                "page_number": frame.get("page_number", 0),
                "page_title": frame.get("page_title", ""),
                "frame_type": frame.get("frame_type", ""),
                "prompt": frame.get("prompt", ""),
            }
            for frame in selected_frames
        ],
        "generated_at": now_iso(),
    }

    return {
        "ok": True,
        "package": package,
    }


def import_generated_frame_image(
    *,
    project_id: str,
    frame_id: str,
    source_path: str,
    original_filename: str,
    approve: bool = True,
) -> Dict[str, Any]:
    result = attach_uploaded_frame_image(
        project_id=project_id,
        frame_id=frame_id,
        source_path=source_path,
        original_filename=original_filename,
    )

    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado após import.")

    jobs = read_json(ILLUSTRATION_JOBS_FILE, [])
    if not isinstance(jobs, list):
        jobs = []

    updated_jobs = []
    for item in jobs:
        job = _safe_dict(item)
        if str(job.get("project_id", "")).strip() == str(project_id).strip() and str(job.get("frame_id", "")).strip() == str(frame_id).strip():
            updated_jobs.append({
                **job,
                "state": "approved" if approve else "generated",
                "updated_at": now_iso(),
            })
        else:
            updated_jobs.append(job)

    from studio_core.core.storage import write_json
    write_json(ILLUSTRATION_JOBS_FILE, updated_jobs)

    update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "illustration_generation": {
                **_safe_dict(current.get("illustration_generation", {})),
                "state": "generated",
                "updated_at": now_iso(),
            },
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "asset_result": result,
    }


def import_generated_frame_image_from_temp_upload(
    *,
    project_id: str,
    frame_id: str,
    temp_path: str,
    original_filename: str,
    approve: bool = True,
) -> Dict[str, Any]:
    src = Path(str(temp_path or "")).expanduser().resolve()
    if not src.exists() or not src.is_file():
        raise ValueError("Ficheiro temporário não encontrado.")

    return import_generated_frame_image(
        project_id=project_id,
        frame_id=frame_id,
        source_path=str(src),
        original_filename=original_filename,
        approve=approve,
)
