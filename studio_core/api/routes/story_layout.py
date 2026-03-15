from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.story_layout_service import (
    add_story_layout_page,
    apply_story_layout_to_story,
    auto_paginate_story,
    get_story_layout,
    remove_story_layout_page,
    update_story_layout_page,
)

router = APIRouter(prefix="/story-layout", tags=["story-layout"])


@router.get("/{project_id}")
def get_layout(project_id: str) -> dict:
    try:
        return {
            "ok": True,
            "layout": get_story_layout(project_id),
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/paginate/{project_id}")
def paginate(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return auto_paginate_story(project_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/page/{project_id}/{page_id}")
def patch_page(project_id: str, page_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return update_story_layout_page(project_id, page_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/page/{project_id}")
def create_page(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return add_story_layout_page(project_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/page/{project_id}/{page_id}")
def delete_page(project_id: str, page_id: str) -> dict:
    try:
        return remove_story_layout_page(project_id, page_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/apply/{project_id}")
def apply_layout(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return apply_story_layout_to_story(project_id, payload.get("language", ""))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
