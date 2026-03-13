from __future__ import annotations

import shutil
import subprocess
from typing import Dict

from fastapi import APIRouter

from studio_core.core.config import APP_CONFIG
from studio_core.core.storage import ensure_storage_structure

router = APIRouter()


def _check_command(command: str, args: list[str] | None = None) -> Dict[str, str | bool]:
    args = args or ["--version"]

    if shutil.which(command) is None:
        return {
            "ok": False,
            "error": "not-found"
        }

    try:
        result = subprocess.run(
            [command, *args],
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
        output = (result.stdout or result.stderr or "").strip()
        return {
            "ok": result.returncode == 0,
            "output": output
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc)
        }


@router.get("/diagnostics")
def diagnostics() -> dict:
    folders = ensure_storage_structure()

    return {
        "ok": True,
        "app_name": APP_CONFIG.app_name,
        "version": APP_CONFIG.app_version,
        "system": APP_CONFIG.system_info(),
        "storage_root": str(APP_CONFIG.storage_root),
        "folders": folders,
        "commands": {
            "python": _check_command("python"),
            "ffmpeg": _check_command("ffmpeg", ["-version"]),
            "espeak": _check_command("espeak", ["--version"]),
        }
}
