from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item
from studio_core.services.ebook_service import build_epub
from studio_core.services.ip_runtime_service import load_ip_runtime

router = APIRouter(prefix="/ebooks", tags=["ebooks"])

PROJECTS_FILE = "data/projects.json"


def _get_project(project_id: str) -> dict | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        if str(project.get("id", "")) == str(project_id):
            return project
    return None


@router.post("/export/{project_id}")
def export_ebook(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    try:
        saga_id = str(project.get("saga_slug", "baribudos")).strip()
        runtime = load_ip_runtime(saga_id)
        metadata = runtime.get("metadata", {}) or {}

        language = str(payload.get("language", project.get("language", "pt-PT"))).strip()
        story = (project.get("language_variants", {}) or {}).get(language) or project.get("story", {}) or {}

        result = build_epub(
            story,
            project_id=project_id,
            project_title=project.get("title", "Projeto"),
            language=language,
            author=str(metadata.get("author_default") or "Autor").strip(),
            cover_path=project.get("cover_image") or None,
            saga_id=saga_id,
        )

        update_json_item(
            PROJECTS_FILE,
            project_id,
            lambda current: {
                **current,
                "outputs": {
                    **(current.get("outputs", {}) or {}),
                    "epub": {
                        **((current.get("outputs", {}) or {}).get("epub", {}) or {}),
                        language: result,
                    },
                },
                "updated_at": now_iso(),
            },
        )

        return {"ok": True, "result": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
