from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.final_media_render_service import export_epub_from_story, render_video_from_package

router = APIRouter(prefix="/final-media", tags=["final-media"])


@router.post("/render-video/{project_id}")
def render_video(project_id: str) -> dict:
    try:
        return render_video_from_package(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/export-epub/{project_id}")
def export_epub(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return export_epub_from_story(project_id, str(payload.get("language", "")).strip())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
