from __future__ import annotations

import platform
import shutil
import sys
from pathlib import Path

from fastapi import APIRouter, Depends

from studio_core.core.config import APP_CONFIG, resolve_project_path, resolve_storage_path
from studio_core.core.storage import read_json
from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


def _command_status(command: str) -> dict:
    path = shutil.which(command)
    return {"ok": bool(path), "path": path or ""}


@router.get("")
def diagnostics(
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin")),
) -> dict:
    storage_root = resolve_storage_path()
    project_root = resolve_project_path()
    public_root = resolve_project_path("public")
    settings = read_json("data/settings.json", {})
    projects = read_json("data/projects.json", [])
    ips = read_json("data/ip_registry.json", [])
    return {
        "ok": True,
        "diagnostics": {
            "app_name": APP_CONFIG.app_name,
            "app_version": APP_CONFIG.app_version,
            "project_root": str(project_root),
            "storage_root": str(storage_root),
            "public_root": str(public_root),
            "system": {"platform": platform.platform(), "python_version": sys.version, "python_executable": sys.executable},
            "paths": {"project_root_exists": Path(project_root).exists(), "storage_root_exists": Path(storage_root).exists(), "public_root_exists": Path(public_root).exists()},
            "commands": {name: _command_status(command) for name, command in {
                "ffmpeg": "ffmpeg", "ffprobe": "ffprobe", "espeak": "espeak", "espeak_ng": "espeak-ng", "node": "node", "npm": "npm"
            }.items()},
            "data": {"projects_count": len(projects) if isinstance(projects, list) else 0, "ips_count": len(ips) if isinstance(ips, list) else 0, "settings_loaded": isinstance(settings, dict)},
        },
    }
