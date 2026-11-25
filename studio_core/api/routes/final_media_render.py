from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from studio_core.services.final_media_render_service import export_epub_from_story, render_video_from_package
from studio_core.services.project_route_auth import require_project_path_access

router = APIRouter(prefix="/final-media", tags=["final-media"])


@router.post("/render-video/{project_id}")
def render_video(project_id: str, _principal=Depends(require_project_path_access)) -> dict:
    try:
        return render_video_from_package(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Não foi possível renderizar o vídeo final.") from exc


@router.post("/export-epub/{project_id}")
def export_epub(project_id: str, payload: dict | None = None, _principal=Depends(require_project_path_access)) -> dict:
    try:
        return export_epub_from_story(project_id, str((payload or {}).get("language", "")).strip())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Não foi possível exportar o EPUB.") from exc
