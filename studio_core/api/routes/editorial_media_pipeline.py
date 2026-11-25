from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from studio_core.services.editorial_media_pipeline_service import build_video_package_from_storyboard, generate_editorial_illustrations
from studio_core.services.project_route_auth import require_project_path_access

router = APIRouter(prefix="/editorial-media", tags=["editorial-media"])


@router.post("/generate-illustrations/{project_id}")
def generate_illustrations(project_id: str, payload: dict | None = None, _principal=Depends(require_project_path_access)) -> dict:
    try:
        return generate_editorial_illustrations(project_id=project_id, provider=str((payload or {}).get("provider", "")).strip())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Não foi possível gerar as ilustrações editoriais.") from exc


@router.post("/build-video-package/{project_id}")
def build_video_package(project_id: str, _principal=Depends(require_project_path_access)) -> dict:
    try:
        return build_video_package_from_storyboard(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Não foi possível construir o pacote de vídeo.") from exc
