from __future__ import annotations

from typing import Any, Dict, List

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item, write_json
from studio_core.services.illustration_provider_service import generate_illustration
from studio_core.services.illustration_generation_service import list_illustration_jobs
from studio_core.services.illustration_asset_service import attach_uploaded_frame_image
from studio_core.services.saga_runtime_service import load_saga_runtime

PROJECTS_FILE = "data/projects.json"
ILLUSTRATION_JOBS_FILE = "data/illustration_jobs.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _get_project(project_id: str) -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        if str(project.get("id", "")).strip() == str(project_id).strip():
            return project
    return None


def _build_saga_style(runtime: Dict[str, Any]) -> Dict[str, Any]:
    canons = _safe_dict(runtime.get("canons", {}))
    visual = _safe_dict(canons.get("visual", {}))
    characters = _safe_dict(canons.get("characters", {}))

    return {
        "palette": _safe_dict(runtime.get("palette", {})),
        "visual": {
            "style": str(visual.get("style", "")).strip(),
            "environment": str(_safe_dict(visual.get("environment_rules", {})).get("world", "")).strip(),
            "lighting": str(_safe_dict(visual.get("lighting_rules", {})).get("type", "")).strip(),
            "tone": ", ".join(str(item).strip() for item in _safe_list(visual.get("emotional_tone", [])) if str(item).strip()),
        },
        "character_rules": str(_safe_dict(characters.get("visual_dna", {}))).strip(),
    }


def run_local_illustration_generation(project_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    provider = str(payload.get("provider", "stable_diffusion")).strip() or "stable_diffusion"

    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    runtime = load_saga_runtime(str(project.get("saga_slug", "baribudos")).strip() or "baribudos")
    saga_style = _build_saga_style(runtime)

    jobs = list_illustration_jobs(project_id)
    if not jobs:
        raise ValueError("Projeto sem jobs de ilustração.")

    job_map = {str(_safe_dict(job).get("id", "")).strip(): _safe_dict(job) for job in jobs}
    updated_jobs = []
    generated = []

    for job in jobs:
        job_dict = _safe_dict(job)
        if str(job_dict.get("state", "")).strip() not in {"queued", "failed"}:
            updated_jobs.append(job_dict)
            continue

        prompt = str(job_dict.get("prompt", "")).strip()
        if not prompt:
            updated_jobs.append({**job_dict, "state": "failed", "updated_at": now_iso()})
            continue

        result = generate_illustration(
            prompt=prompt,
            provider=provider,
            saga_style=saga_style,
        )

        asset_result = attach_uploaded_frame_image(
            project_id=project_id,
            frame_id=str(job_dict.get("frame_id", "")).strip(),
            source_path=str(result.get("file_path", "")).strip(),
            original_filename=str(result.get("file_path", "")).split("/")[-1] or "generated.png",
        )

        generated.append({
            "job_id": str(job_dict.get("id", "")).strip(),
            "frame_id": str(job_dict.get("frame_id", "")).strip(),
            "provider": result.get("provider", provider),
            "file_path": result.get("file_path", ""),
            "fallback_used": bool(result.get("fallback_used", False)),
            "ok": bool(result.get("ok", False)),
        })

        updated_jobs.append({
            **job_dict,
            "state": "approved",
            "provider": result.get("provider", provider),
            "generated_file_path": result.get("file_path", ""),
            "updated_at": now_iso(),
        })

    write_json(ILLUSTRATION_JOBS_FILE, updated_jobs)

    updated_project = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "illustration_generation": {
                **_safe_dict(current.get("illustration_generation", {})),
                "provider": provider,
                "state": "generated",
                "generated_count": len(generated),
                "updated_at": now_iso(),
            },
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "provider": provider,
        "generated_count": len(generated),
        "generated": generated,
        "project": updated_project,
  }
