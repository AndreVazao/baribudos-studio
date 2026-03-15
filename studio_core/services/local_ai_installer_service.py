from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, write_json
from studio_core.core.config import resolve_storage_path

LOCAL_AI_STATUS_FILE = "data/local_ai_status.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def _status_path() -> Path:
    return resolve_storage_path("local_ai")


def _default_install_root() -> Path:
    return _status_path()


def _detect_os() -> str:
    name = platform.system().lower()
    if "windows" in name:
        return "windows"
    if "darwin" in name:
        return "macos"
    return "linux"


def _build_paths(root: Path) -> Dict[str, str]:
    comfy_root = root / "comfyui"
    a1111_root = root / "automatic1111"
    models_root = root / "models"
    downloads_root = root / "downloads"
    outputs_root = root / "outputs"
    scripts_root = root / "scripts"

    return {
        "root": str(root),
        "comfyui_root": str(comfy_root),
        "automatic1111_root": str(a1111_root),
        "models_root": str(models_root),
        "downloads_root": str(downloads_root),
        "outputs_root": str(outputs_root),
        "scripts_root": str(scripts_root),
    }


def _ensure_dirs(paths: Dict[str, str]) -> None:
    for value in paths.values():
        Path(value).mkdir(parents=True, exist_ok=True)


def _build_windows_setup_bat(paths: Dict[str, str]) -> str:
    root = paths["root"]
    comfy = paths["comfyui_root"]
    a1111 = paths["automatic1111_root"]
    models = paths["models_root"]

    return f"""@echo off
setlocal

echo [Baribudos Studio] Local AI setup started...

where git >nul 2>nul
if errorlevel 1 (
  echo Git nao encontrado. Instala Git primeiro.
  exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
  echo Python nao encontrado. Instala Python 3.10+ primeiro.
  exit /b 1
)

if not exist "{comfy}" (
  echo Cloning ComfyUI...
  git clone https://github.com/comfyanonymous/ComfyUI.git "{comfy}"
)

if not exist "{a1111}" (
  echo Cloning Automatic1111...
  git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git "{a1111}"
)

if not exist "{comfy}\\venv" (
  echo Creating ComfyUI venv...
  python -m venv "{comfy}\\venv"
)

call "{comfy}\\venv\\Scripts\\activate.bat"
python -m pip install --upgrade pip
if exist "{comfy}\\requirements.txt" pip install -r "{comfy}\\requirements.txt"

if not exist "{a1111}\\venv" (
  echo Creating Automatic1111 venv...
  python -m venv "{a1111}\\venv"
)

call "{a1111}\\venv\\Scripts\\activate.bat"
python -m pip install --upgrade pip

echo.
echo Setup base concluido.
echo Modelos devem ser colocados em:
echo {models}
echo.
echo ComfyUI pronto em:
echo {comfy}
echo.
echo Automatic1111 pronto em:
echo {a1111}
echo.

exit /b 0
"""


def _build_windows_start_comfy_bat(paths: Dict[str, str]) -> str:
    comfy = paths["comfyui_root"]
    outputs = paths["outputs_root"]

    return f"""@echo off
setlocal
cd /d "{comfy}"

if exist "venv\\Scripts\\activate.bat" call "venv\\Scripts\\activate.bat"

set COMFYUI_OUTPUT_DIRECTORY={outputs}
python main.py --listen 127.0.0.1 --port 8188
"""


def _build_windows_start_a1111_bat(paths: Dict[str, str]) -> str:
    a1111 = paths["automatic1111_root"]

    return f"""@echo off
setlocal
cd /d "{a1111}"
set COMMANDLINE_ARGS=--api --listen --port 7860
call webui-user.bat
"""


def _build_linux_setup_sh(paths: Dict[str, str]) -> str:
    comfy = paths["comfyui_root"]
    a1111 = paths["automatic1111_root"]
    models = paths["models_root"]

    return f"""#!/usr/bin/env bash
set -e

echo "[Baribudos Studio] Local AI setup started..."

command -v git >/dev/null 2>&1 || {{ echo "Git nao encontrado"; exit 1; }}
command -v python3 >/dev/null 2>&1 || {{ echo "Python3 nao encontrado"; exit 1; }}

if [ ! -d "{comfy}" ]; then
  git clone https://github.com/comfyanonymous/ComfyUI.git "{comfy}"
fi

if [ ! -d "{a1111}" ]; then
  git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git "{a1111}"
fi

if [ ! -d "{comfy}/venv" ]; then
  python3 -m venv "{comfy}/venv"
fi

source "{comfy}/venv/bin/activate"
python -m pip install --upgrade pip
if [ -f "{comfy}/requirements.txt" ]; then
  pip install -r "{comfy}/requirements.txt"
fi
deactivate

if [ ! -d "{a1111}/venv" ]; then
  python3 -m venv "{a1111}/venv"
fi

echo
echo "Setup base concluido."
echo "Modelos devem ser colocados em:"
echo "{models}"
"""


def _build_linux_start_comfy_sh(paths: Dict[str, str]) -> str:
    comfy = paths["comfyui_root"]
    outputs = paths["outputs_root"]

    return f"""#!/usr/bin/env bash
set -e
cd "{comfy}"
source venv/bin/activate || true
export COMFYUI_OUTPUT_DIRECTORY="{outputs}"
python main.py --listen 127.0.0.1 --port 8188
"""


def _build_linux_start_a1111_sh(paths: Dict[str, str]) -> str:
    a1111 = paths["automatic1111_root"]

    return f"""#!/usr/bin/env bash
set -e
cd "{a1111}"
export COMMANDLINE_ARGS="--api --listen --port 7860"
bash webui.sh
"""


def _write_script(path: Path, content: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        try:
            mode = path.stat().st_mode
            path.chmod(mode | 0o111)
        except Exception:
            pass


def _initial_status(paths: Dict[str, str], os_name: str) -> Dict[str, Any]:
    return {
        "id": str(uuid4()),
        "configured_at": now_iso(),
        "os": os_name,
        "paths": paths,
        "requirements": {
            "python": _command_exists("python") or _command_exists("python3"),
            "git": _command_exists("git"),
        },
        "providers": {
            "comfyui": {
                "installed": Path(paths["comfyui_root"]).exists(),
                "api_url": "http://127.0.0.1:8188",
                "enabled": True,
            },
            "automatic1111": {
                "installed": Path(paths["automatic1111_root"]).exists(),
                "api_url": "http://127.0.0.1:7860",
                "enabled": True,
            },
            "cloud_openai": {
                "installed": False,
                "enabled": False,
            },
        },
        "default_provider": "stable_diffusion",
        "fallback_provider": "local_basic",
    }


def setup_local_ai_installer(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    install_root = Path(str(payload.get("install_root", "")).strip() or _default_install_root()).expanduser().resolve()
    os_name = _detect_os()
    paths = _build_paths(install_root)

    _ensure_dirs(paths)

    scripts_root = Path(paths["scripts_root"])

    if os_name == "windows":
        _write_script(scripts_root / "setup-local-ai.bat", _build_windows_setup_bat(paths))
        _write_script(scripts_root / "start-comfyui.bat", _build_windows_start_comfy_bat(paths))
        _write_script(scripts_root / "start-automatic1111.bat", _build_windows_start_a1111_bat(paths))
    else:
        _write_script(scripts_root / "setup-local-ai.sh", _build_linux_setup_sh(paths), executable=True)
        _write_script(scripts_root / "start-comfyui.sh", _build_linux_start_comfy_sh(paths), executable=True)
        _write_script(scripts_root / "start-automatic1111.sh", _build_linux_start_a1111_sh(paths), executable=True)

    status = _initial_status(paths, os_name)
    write_json(LOCAL_AI_STATUS_FILE, status)

    return {
        "ok": True,
        "status": status,
    }


def get_local_ai_status() -> Dict[str, Any]:
    return _safe_dict(read_json(LOCAL_AI_STATUS_FILE, {}))


def set_local_ai_default_provider(provider: str) -> Dict[str, Any]:
    provider = str(provider or "").strip()
    status = _safe_dict(read_json(LOCAL_AI_STATUS_FILE, {}))
    if not status:
        raise ValueError("Local AI installer ainda não foi configurado.")

    allowed = {"stable_diffusion", "automatic1111", "local_basic", "openai"}
    if provider not in allowed:
        raise ValueError("Provider inválido.")

    status["default_provider"] = provider
    status["updated_at"] = now_iso()
    write_json(LOCAL_AI_STATUS_FILE, status)

    return {
        "ok": True,
        "status": status,
  }
