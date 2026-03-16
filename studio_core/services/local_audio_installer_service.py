from __future__ import annotations

import platform
import shutil
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from studio_core.core.config import resolve_storage_path
from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, write_json

LOCAL_AUDIO_STATUS_FILE = "data/local_audio_status.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def _detect_os() -> str:
    name = platform.system().lower()
    if "windows" in name:
        return "windows"
    if "darwin" in name:
        return "macos"
    return "linux"


def _default_install_root() -> Path:
    return resolve_storage_path("local_audio")


def _build_paths(root: Path) -> Dict[str, str]:
    return {
        "root": str(root),
        "coqui_root": str(root / "coqui_tts"),
        "xtts_root": str(root / "xtts"),
        "models_root": str(root / "models"),
        "voices_root": str(root / "voices"),
        "outputs_root": str(root / "outputs"),
        "scripts_root": str(root / "scripts"),
    }


def _ensure_dirs(paths: Dict[str, str]) -> None:
    for value in paths.values():
        Path(value).mkdir(parents=True, exist_ok=True)


def _write_script(path: Path, content: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        try:
            path.chmod(path.stat().st_mode | 0o111)
        except Exception:
            pass


def _windows_setup_bat(paths: Dict[str, str]) -> str:
    coqui = paths["coqui_root"]
    xtts = paths["xtts_root"]

    return f"""@echo off
setlocal

echo [Baribudos Studio] Local Audio setup started...

where python >nul 2>nul
if errorlevel 1 (
  echo Python nao encontrado. Instala Python 3.10+ primeiro.
  exit /b 1
)

if not exist "{coqui}\\venv" (
  python -m venv "{coqui}\\venv"
)

call "{coqui}\\venv\\Scripts\\activate.bat"
python -m pip install --upgrade pip
pip install TTS fastapi uvicorn soundfile

if not exist "{xtts}\\venv" (
  python -m venv "{xtts}\\venv"
)

call "{xtts}\\venv\\Scripts\\activate.bat"
python -m pip install --upgrade pip
pip install TTS fastapi uvicorn soundfile

echo Setup de audio local concluido.
exit /b 0
"""


def _windows_start_coqui_bat(paths: Dict[str, str]) -> str:
    coqui = paths["coqui_root"]
    models = paths["models_root"]
    outputs = paths["outputs_root"]

    return f"""@echo off
setlocal
cd /d "{coqui}"
call "venv\\Scripts\\activate.bat"
set BARIBUDOS_AUDIO_MODELS_ROOT={models}
set BARIBUDOS_AUDIO_OUTPUTS_ROOT={outputs}
python -m uvicorn server_coqui:app --host 127.0.0.1 --port 8020
"""


def _windows_start_xtts_bat(paths: Dict[str, str]) -> str:
    xtts = paths["xtts_root"]
    models = paths["models_root"]
    outputs = paths["outputs_root"]
    voices = paths["voices_root"]

    return f"""@echo off
setlocal
cd /d "{xtts}"
call "venv\\Scripts\\activate.bat"
set BARIBUDOS_AUDIO_MODELS_ROOT={models}
set BARIBUDOS_AUDIO_OUTPUTS_ROOT={outputs}
set BARIBUDOS_AUDIO_VOICES_ROOT={voices}
python -m uvicorn server_xtts:app --host 127.0.0.1 --port 8030
"""


def _linux_setup_sh(paths: Dict[str, str]) -> str:
    coqui = paths["coqui_root"]
    xtts = paths["xtts_root"]

    return f"""#!/usr/bin/env bash
set -e

command -v python3 >/dev/null 2>&1 || {{ echo "Python3 nao encontrado"; exit 1; }}

if [ ! -d "{coqui}/venv" ]; then
  python3 -m venv "{coqui}/venv"
fi
source "{coqui}/venv/bin/activate"
python -m pip install --upgrade pip
pip install TTS fastapi uvicorn soundfile
deactivate

if [ ! -d "{xtts}/venv" ]; then
  python3 -m venv "{xtts}/venv"
fi
source "{xtts}/venv/bin/activate"
python -m pip install --upgrade pip
pip install TTS fastapi uvicorn soundfile
deactivate
"""


def _linux_start_coqui_sh(paths: Dict[str, str]) -> str:
    coqui = paths["coqui_root"]
    models = paths["models_root"]
    outputs = paths["outputs_root"]

    return f"""#!/usr/bin/env bash
set -e
cd "{coqui}"
source venv/bin/activate
export BARIBUDOS_AUDIO_MODELS_ROOT="{models}"
export BARIBUDOS_AUDIO_OUTPUTS_ROOT="{outputs}"
python -m uvicorn server_coqui:app --host 127.0.0.1 --port 8020
"""


def _linux_start_xtts_sh(paths: Dict[str, str]) -> str:
    xtts = paths["xtts_root"]
    models = paths["models_root"]
    outputs = paths["outputs_root"]
    voices = paths["voices_root"]

    return f"""#!/usr/bin/env bash
set -e
cd "{xtts}"
source venv/bin/activate
export BARIBUDOS_AUDIO_MODELS_ROOT="{models}"
export BARIBUDOS_AUDIO_OUTPUTS_ROOT="{outputs}"
export BARIBUDOS_AUDIO_VOICES_ROOT="{voices}"
python -m uvicorn server_xtts:app --host 127.0.0.1 --port 8030
"""


def _coqui_server_py() -> str:
    return """from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

try:
    from TTS.api import TTS
except Exception:
    TTS = None

app = FastAPI(title="Baribudos Coqui TTS")

MODELS_ROOT = Path(os.getenv("BARIBUDOS_AUDIO_MODELS_ROOT", ".")).expanduser().resolve()
OUTPUTS_ROOT = Path(os.getenv("BARIBUDOS_AUDIO_OUTPUTS_ROOT", ".")).expanduser().resolve()
OUTPUTS_ROOT.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL = os.getenv("BARIBUDOS_COQUI_MODEL", "tts_models/en/ljspeech/tacotron2-DDC")
_ENGINE = None
_ENGINE_MODEL = None


class SynthesizePayload(BaseModel):
    text: str
    language: str = "en"
    output_path: str = ""


def get_engine():
    global _ENGINE, _ENGINE_MODEL
    if TTS is None:
        raise RuntimeError("Biblioteca TTS nao instalada.")

    if _ENGINE is None:
        _ENGINE_MODEL = DEFAULT_MODEL
        _ENGINE = TTS(model_name=_ENGINE_MODEL, progress_bar=False, gpu=False)
    return _ENGINE


@app.get("/docs")
def docs_ping():
    return {"ok": True, "engine": "coqui_tts", "model": DEFAULT_MODEL}


@app.post("/synthesize")
def synthesize(payload: SynthesizePayload):
    text = str(payload.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Texto vazio.")

    output_path = Path(payload.output_path).expanduser().resolve() if payload.output_path else OUTPUTS_ROOT / f"{uuid4()}.wav"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        engine = get_engine()
        engine.tts_to_file(text=text, file_path=str(output_path))
        return {
            "ok": True,
            "provider": "coqui_tts",
            "file_path": str(output_path),
            "model": _ENGINE_MODEL,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
"""


def _xtts_server_py() -> str:
    return """from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

try:
    from TTS.api import TTS
except Exception:
    TTS = None

app = FastAPI(title="Baribudos XTTS")

MODELS_ROOT = Path(os.getenv("BARIBUDOS_AUDIO_MODELS_ROOT", ".")).expanduser().resolve()
OUTPUTS_ROOT = Path(os.getenv("BARIBUDOS_AUDIO_OUTPUTS_ROOT", ".")).expanduser().resolve()
VOICES_ROOT = Path(os.getenv("BARIBUDOS_AUDIO_VOICES_ROOT", ".")).expanduser().resolve()
OUTPUTS_ROOT.mkdir(parents=True, exist_ok=True)
VOICES_ROOT.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL = os.getenv("BARIBUDOS_XTTS_MODEL", "tts_models/multilingual/multi-dataset/xtts_v2")
_ENGINE = None
_ENGINE_MODEL = None


class SynthesizePayload(BaseModel):
    text: str
    language: str = "en"
    speaker_wav: str = ""
    output_path: str = ""


def get_engine():
    global _ENGINE, _ENGINE_MODEL
    if TTS is None:
        raise RuntimeError("Biblioteca TTS nao instalada.")

    if _ENGINE is None:
        _ENGINE_MODEL = DEFAULT_MODEL
        _ENGINE = TTS(model_name=_ENGINE_MODEL, progress_bar=False, gpu=False)
    return _ENGINE


@app.get("/docs")
def docs_ping():
    return {"ok": True, "engine": "xtts", "model": DEFAULT_MODEL}


@app.post("/synthesize")
def synthesize(payload: SynthesizePayload):
    text = str(payload.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Texto vazio.")

    output_path = Path(payload.output_path).expanduser().resolve() if payload.output_path else OUTPUTS_ROOT / f"{uuid4()}.wav"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    speaker_wav = str(payload.speaker_wav or "").strip()
    if speaker_wav:
        speaker_path = Path(speaker_wav).expanduser().resolve()
        if not speaker_path.exists():
            raise HTTPException(status_code=400, detail="speaker_wav nao encontrado.")
    else:
        speaker_path = None

    try:
        engine = get_engine()
        kwargs = {
            "text": text,
            "file_path": str(output_path),
            "language": str(payload.language or "en"),
        }
        if speaker_path is not None:
            kwargs["speaker_wav"] = str(speaker_path)

        engine.tts_to_file(**kwargs)
        return {
            "ok": True,
            "provider": "xtts",
            "file_path": str(output_path),
            "model": _ENGINE_MODEL,
            "speaker_wav": str(speaker_path) if speaker_path else "",
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
"""


def setup_local_audio_installer(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    root = Path(str(payload.get("install_root", "")).strip() or _default_install_root()).expanduser().resolve()
    os_name = _detect_os()
    paths = _build_paths(root)
    _ensure_dirs(paths)

    scripts_root = Path(paths["scripts_root"])
    coqui_root = Path(paths["coqui_root"])
    xtts_root = Path(paths["xtts_root"])

    _write_script(coqui_root / "server_coqui.py", _coqui_server_py())
    _write_script(xtts_root / "server_xtts.py", _xtts_server_py())

    if os_name == "windows":
        _write_script(scripts_root / "setup-local-audio.bat", _windows_setup_bat(paths))
        _write_script(scripts_root / "start-coqui-tts.bat", _windows_start_coqui_bat(paths))
        _write_script(scripts_root / "start-xtts.bat", _windows_start_xtts_bat(paths))
    else:
        _write_script(scripts_root / "setup-local-audio.sh", _linux_setup_sh(paths), executable=True)
        _write_script(scripts_root / "start-coqui-tts.sh", _linux_start_coqui_sh(paths), executable=True)
        _write_script(scripts_root / "start-xtts.sh", _linux_start_xtts_sh(paths), executable=True)

    status = {
        "id": str(uuid4()),
        "configured_at": now_iso(),
        "os": os_name,
        "paths": paths,
        "requirements": {
            "python": _command_exists("python") or _command_exists("python3"),
        },
        "providers": {
            "system_tts": {
                "available": True,
                "enabled": True,
            },
            "coqui_tts": {
                "installed": True,
                "api_url": "http://127.0.0.1:8020",
                "enabled": True,
            },
            "xtts": {
                "installed": True,
                "api_url": "http://127.0.0.1:8030",
                "enabled": True,
            },
        },
        "default_provider": "system_tts",
        "fallback_provider": "system_tts",
    }

    write_json(LOCAL_AUDIO_STATUS_FILE, status)

    return {
        "ok": True,
        "status": status,
    }


def get_local_audio_status() -> Dict[str, Any]:
    return _safe_dict(read_json(LOCAL_AUDIO_STATUS_FILE, {}))


def set_local_audio_default_provider(provider: str) -> Dict[str, Any]:
    provider = str(provider or "").strip()
    allowed = {"system_tts", "coqui_tts", "xtts"}

    if provider not in allowed:
        raise ValueError("Provider de áudio inválido.")

    status = _safe_dict(read_json(LOCAL_AUDIO_STATUS_FILE, {}))
    if not status:
        raise ValueError("Local Audio ainda não foi configurado.")

    status["default_provider"] = provider
    status["updated_at"] = now_iso()
    write_json(LOCAL_AUDIO_STATUS_FILE, status)

    return {
        "ok": True,
        "status": status,
    }
