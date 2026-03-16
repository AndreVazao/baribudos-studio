from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.core.storage import read_json, update_json_item
from studio_core.services.editorial_page_engine import (
    build_book_preview_model,
    build_editorial_package,
    merge_two_pages,
    repaginate_existing_pages,
    split_one_page,
)
from studio_core.services.saga_runtime_service import load_saga_runtime

router = APIRouter(prefix="/editorial-engine", tags=["editorial-engine"])

PROJECTS_FILE = "data/projects.json"


def _get_project(project_id: str) -> dict | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        if str(project.get("id", "")).strip() == str(project_id).strip():
            return project
    return None


def _project_metadata(project: dict, payload: dict | None = None) -> dict:
    payload = payload or {}
    commercial = project.get("commercial", {}) or {}
    runtime = load_saga_runtime(str(project.get("saga_slug", "baribudos")).strip() or "baribudos")
    runtime_meta = runtime.get("metadata", {}) or {}

    return {
        "language": str(payload.get("language", project.get("language", "pt-PT"))).strip() or "pt-PT",
        "age_group": str(payload.get("age_group", commercial.get("target_age", runtime_meta.get("target_age", "4-10")))).strip(),
        "genre": str(payload.get("genre", runtime_meta.get("genre", "children"))).strip(),
        "theme": str(payload.get("theme", project.get("theme", ""))).strip(),
        "moral": str(payload.get("moral", project.get("moral", ""))).strip(),
        "pedagogical_goal": str(payload.get("pedagogical_goal", project.get("pedagogical_goal", ""))).strip(),
        "illustration_every": int(payload.get("illustration_every", 2) or 2),
    }


@router.post("/build/{project_id}")
def build_editorial(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    text = str(payload.get("text", "")).strip()
    if not text:
        story = project.get("story", {}) or {}
        text = str(payload.get("text", story.get("raw_text", ""))).strip()

    if not text:
        raise HTTPException(status_code=400, detail="Sem texto para processar.")

    runtime = load_saga_runtime(str(project.get("saga_slug", "baribudos")).strip() or "baribudos")
    metadata = _project_metadata(project, payload)

    result = build_editorial_package(
        text=text,
        metadata=metadata,
        ip_runtime=runtime,
    )

    updated_project = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "editorial_engine": result,
        },
    )

    return {
        "ok": True,
        "editorial": result,
        "project": updated_project,
    }


@router.post("/preview/{project_id}")
def preview_editorial(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    text = str(payload.get("text", "")).strip()
    if not text:
        story = project.get("story", {}) or {}
        text = str(story.get("raw_text", "")).strip()

    if not text:
        raise HTTPException(status_code=400, detail="Sem texto para preview.")

    runtime = load_saga_runtime(str(project.get("saga_slug", "baribudos")).strip() or "baribudos")
    metadata = _project_metadata(project, payload)

    result = build_book_preview_model(
        text=text,
        metadata=metadata,
        ip_runtime=runtime,
    )

    return {
        "ok": True,
        "preview": result,
    }


@router.post("/repaginate/{project_id}")
def repaginate_editorial(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    editorial = project.get("editorial_engine", {}) or {}
    pages = editorial.get("pages", []) or []
    if not pages:
        raise HTTPException(status_code=400, detail="Sem páginas editoriais.")

    metadata = _project_metadata(project, payload)
    next_pages = repaginate_existing_pages(pages, metadata)

    updated_project = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "editorial_engine": {
                **(current.get("editorial_engine", {}) or {}),
                "metadata": metadata,
                "pages": next_pages,
                "pages_count": len(next_pages),
            },
        },
    )

    return {
        "ok": True,
        "editorial": updated_project.get("editorial_engine", {}),
    }


@router.post("/merge-pages/{project_id}")
def merge_pages(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    editorial = project.get("editorial_engine", {}) or {}
    pages = editorial.get("pages", []) or []
    if not pages:
        raise HTTPException(status_code=400, detail="Sem páginas editoriais.")

    first_page_number = int(payload.get("first_page_number", 0) or 0)
    second_page_number = int(payload.get("second_page_number", 0) or 0)
    next_pages = merge_two_pages(pages, first_page_number, second_page_number)

    updated_project = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "editorial_engine": {
                **(current.get("editorial_engine", {}) or {}),
                "pages": next_pages,
                "pages_count": len(next_pages),
            },
        },
    )

    return {
        "ok": True,
        "editorial": updated_project.get("editorial_engine", {}),
    }


@router.post("/split-page/{project_id}")
def split_page(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    editorial = project.get("editorial_engine", {}) or {}
    pages = editorial.get("pages", []) or []
    if not pages:
        raise HTTPException(status_code=400, detail="Sem páginas editoriais.")

    metadata = _project_metadata(project, payload)
    page_number = int(payload.get("page_number", 0) or 0)

    next_pages = split_one_page(
        pages,
        page_number=page_number,
        age_group=metadata.get("age_group"),
        genre=metadata.get("genre"),
    )

    updated_project = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "editorial_engine": {
                **(current.get("editorial_engine", {}) or {}),
                "pages": next_pages,
                "pages_count": len(next_pages),
            },
        },
    )

    return {
        "ok": True,
        "editorial": updated_project.get("editorial_engine", {}),
      }
