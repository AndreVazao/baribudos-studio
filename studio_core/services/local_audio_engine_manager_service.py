from __future__ import annotations

import os
import platform
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, write_json

LOCAL_AUDIO_STATUS_FILE = "data/local_audio_status.json"
LOCAL_AUDIO_ENGINE_STATE_FILE = "data/local_audio_engine_state.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _is_windows() -> bool:
    return platform.system().lower().startswith("win")


def _command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def _load_status() -> Dict[str, Any]:
    return _safe_dict(read_json(LOCAL_AUDIO_STATUS_FILE, {}))


def _load_state() -> Dict[str, Any]:
    return _safe_dict(read_json(LOCAL_AUDIO_ENGINE_STATE_FILE, {}))


def _save_state(state: Dict[str, Any]) -> None:
    write_json(LOCAL_AUDIO_ENGINE_STATE_FILE, state)


def _check_http(url: str) -> bool:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as res:
            return 200 <= getattr(res, "status", 200) < 500
    except Exception:
        return False


def _provider_health_url(provider: str, status: Dict[str, Any]) -> str:
    providers = _safe_dict(status.get("providers", {}))
    entry = _safe_dict(providers.get(provider, {}))
    return _safe_text(entry.get("api_url"))


def _provider_health_path(provider: str) -> str:
    if provider == "coqui_tts":
        return "/docs"
    if provider == "xtts":
        return "/docs"
    return ""


def get_local_audio_engine_status() -> Dict[str, Any]:
    status = _load_status()
    state = _load_state()

    result = {
        "configured": bool(status),
        "default_provider": _safe_text(status.get("default_provider", "system_tts")) or "system_tts",
        "fallback_provider": _safe_text(status.get("fallback_provider", "system_tts")) or "system_tts",
        "requirements": _safe_dict(status.get("requirements", {})),
        "providers": {},
        "updated_at": now_iso(),
    }

    for provider in ["system_tts", "coqui_tts", "xtts"]:
        health_url = _provider_health_url(provider, status)
        health_path = _provider_health_path(provider)

        if provider == "system_tts":
            running = bool(_safe_dict(status.get("providers", {})).get("system_tts", {}).get("available", False))
            result["providers"][provider] = {
                "running": running,
                "health": {
                    "ok": running,
                    "url": "",
                },
                "state": _safe_dict(state.get(provider, {})),
            }
            continue

        url = f"{health_url.rstrip('/')}{health_path}" if health_url and health_path else ""
        running = _check_http(url) if url else False

        result["providers"][provider] = {
            "running": running,
            "health": {
                "ok": running,
                "url": url,
            },
            "state": _safe_dict(state.get(provider, {})),
        }

    return result


def _script_path(provider: str, status: Dict[str, Any]) -> Path:
    paths = _safe_dict(status.get("paths", {}))
    scripts_root = Path(_safe_text(paths.get("scripts_root", "")))

    if _is_windows():
        if provider == "coqui_tts":
            return scripts_root / "start-coqui-tts.bat"
        if provider == "xtts":
            return scripts_root / "start-xtts.bat"
    else:
        if provider == "coqui_tts":
            return scripts_root / "start-coqui-tts.sh"
        if provider == "xtts":
            return scripts_root / "start-xtts.sh"

    return Path("")


def _spawn(script_path: Path) -> subprocess.Popen:
    if not script_path.exists():
        raise FileNotFoundError(f"Script não encontrado: {script_path}")

    if _is_windows():
        return subprocess.Popen(
            ["cmd", "/c", str(script_path)],
            creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            cwd=str(script_path.parent),
        )

    return subprocess.Popen(
        [str(script_path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        cwd=str(script_path.parent),
        start_new_session=True,
    )


def start_audio_provider(provider: str, timeout_seconds: int = 60) -> Dict[str, Any]:
    provider = _safe_text(provider)
    if provider not in {"coqui_tts", "xtts"}:
        raise ValueError("Provider de áudio inválido para arranque local.")

    status = _load_status()
    if not status:
        raise ValueError("Local Audio ainda não foi configurado.")

    current = get_local_audio_engine_status()
    provider_info = _safe_dict(_safe_dict(current.get("providers", {})).get(provider, {}))
    if bool(provider_info.get("running", False)):
        return {
            "ok": True,
            "provider": provider,
            "already_running": True,
            "running": True,
        }

    script_path = _script_path(provider, status)
    process = _spawn(script_path)

    started = time.time()
    while time.time() - started < timeout_seconds:
        time.sleep(2)
        check = get_local_audio_engine_status()
        provider_check = _safe_dict(_safe_dict(check.get("providers", {})).get(provider, {}))
        if bool(provider_check.get("running", False)):
            state = _load_state()
            state[provider] = {
                "started_at": now_iso(),
                "pid": process.pid,
                "script_path": str(script_path),
                "running": True,
            }
            _save_state(state)
            return {
                "ok": True,
                "provider": provider,
                "already_running": False,
                "running": True,
                "pid": process.pid,
            }

    state = _load_state()
    state[provider] = {
        "started_at": now_iso(),
        "pid": process.pid,
        "script_path": str(script_path),
        "running": False,
        "timeout": True,
    }
    _save_state(state)

    return {
        "ok": False,
        "provider": provider,
        "running": False,
        "pid": process.pid,
        "timeout": True,
    }


def ensure_audio_provider_running(provider: str) -> Dict[str, Any]:
    if provider == "system_tts":
        status = get_local_audio_engine_status()
        info = _safe_dict(_safe_dict(status.get("providers", {})).get("system_tts", {}))
        return {
            "ok": bool(info.get("running", False)),
            "provider": provider,
            "running": bool(info.get("running", False)),
            "action": "checked",
        }

    current = get_local_audio_engine_status()
    provider_info = _safe_dict(_safe_dict(current.get("providers", {})).get(provider, {}))
    if bool(provider_info.get("running", False)):
        return {
            "ok": True,
            "provider": provider,
            "running": True,
            "action": "already_running",
        }

    started = start_audio_provider(provider)
    return {
        "ok": bool(started.get("ok", False)),
        "provider": provider,
        "running": bool(started.get("running", False)),
        "action": "started",
        "details": started,
    }


def stop_audio_provider(provider: str) -> Dict[str, Any]:
    provider = _safe_text(provider)
    state = _load_state()
    provider_state = _safe_dict(state.get(provider, {}))
    pid = provider_state.get("pid")

    if not pid:
        return {
            "ok": False,
            "provider": provider,
            "stopped": False,
            "reason": "pid_not_found",
        }

    try:
        if _is_windows():
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            os.kill(int(pid), 15)
    except Exception as exc:
        return {
            "ok": False,
            "provider": provider,
            "stopped": False,
            "reason": str(exc),
        }

    state[provider] = {
        **provider_state,
        "running": False,
        "stopped_at": now_iso(),
    }
    _save_state(state)

    return {
        "ok": True,
        "provider": provider,
        "stopped": True,
}
