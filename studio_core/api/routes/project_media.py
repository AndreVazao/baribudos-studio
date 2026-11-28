from __future__ import annotations

import mimetypes
import re
from pathlib import Path, PurePosixPath, PureWindowsPath

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from studio_core.core.config import APP_CONFIG, resolve_storage_path
from studio_core.core.storage import read_json
from studio_core.services.project_route_auth import require_project_path_access

router = APIRouter(prefix="/projects", tags=["project-media"])

_ALLOWED_EXTENSIONS = {
    ".avif", ".epub", ".gif", ".jpeg", ".jpg", ".m4a", ".m4v",
    ".mkv", ".mov", ".mp3", ".mp4", ".ogg", ".pdf", ".png",
    ".wav", ".webm", ".webp",
}


def _relative_storage_path(value: object) -> str | None:
    raw = str(value or "").strip().replace("\\", "/")
    if not raw:
        return None

    lower = raw.lower()
    marker = "/storage/"
    if marker in lower:
        raw = raw[lower.rfind(marker) + len(marker):]
    elif lower.startswith("storage/"):
        raw = raw[len("storage/"):]

    if not raw or raw.startswith("/") or re.match(r"^[a-zA-Z]:", raw):
        return None

    parts = PurePosixPath(raw).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        return None
    if PureWindowsPath(raw).drive or PureWindowsPath(raw).root:
        return None
    return "/".join(parts)


_MEDIA_PATH_KEYS = {
    "file_path", "storage_path", "cover_image", "illustration_path",
    "badge_file_path", "thumbnail_path", "preview_path",
}


def _project_media_paths(project: dict) -> set[str]:
    paths: set[str] = set()

    def visit(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in _MEDIA_PATH_KEYS and isinstance(child, str):
                    normalized = _relative_storage_path(child)
                    if normalized:
                        paths.add(normalized)
                else:
                    visit(child)
        elif isinstance(value, (list, tuple)):
            for child in value:
                visit(child)

    visit(project)
    return paths

def _resolve_project_media(project_id: str, requested_path: str) -> Path:
    projects = read_json("data/projects.json", [])
    project = next(
        (item for item in projects if str(item.get("id", "")).strip() == project_id),
        None,
    )
    if not isinstance(project, dict):
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    normalized = _relative_storage_path(requested_path)
    if not normalized or normalized not in _project_media_paths(project):
        raise HTTPException(status_code=404, detail="Ficheiro não associado ao projeto.")

    if Path(normalized).suffix.lower() not in _ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=404, detail="Tipo de ficheiro não permitido.")

    try:
        resolved = resolve_storage_path(normalized)
        storage_root = APP_CONFIG.storage_root.expanduser().resolve()
        resolved.relative_to(storage_root)
    except (OSError, ValueError):
        raise HTTPException(status_code=404, detail="Ficheiro não encontrado.") from None

    if not resolved.is_file():
        raise HTTPException(status_code=404, detail="Ficheiro não encontrado.")
    return resolved


@router.get("/{project_id}/media")
def get_project_media(
    project_id: str,
    path: str = Query(..., min_length=1, max_length=2048),
    principal=Depends(require_project_path_access),
) -> FileResponse:
    file_path = _resolve_project_media(project_id, path)
    extension = file_path.suffix.lower()
    media_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    inline = media_type.startswith(("image/", "audio/", "video/"))
    safe_name = "".join(char for char in file_path.name if char.isalnum() or char in "._-") or "media"
    disposition = "inline" if inline else "attachment"
    return FileResponse(
        file_path,
        media_type=media_type,
        headers={
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
            "Content-Disposition": f'{disposition}; filename="{safe_name}"',
        },
    )
