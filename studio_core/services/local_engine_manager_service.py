from __future__ import annotations

import os
import platform
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, write_json

LOCAL_AI_STATUS_FILE = "data/local_ai_status.json"
LOCAL_ENGINE_STATE_FILE = "data/local_engine_state.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _is_windows() -> bool:
    return platform.system().lower().startswith("win")


def _load_local_ai_status() -> Dict[str, Any]:
    return _safe_dict(read_json(LOCAL_AI_STATUS_FILE, {}))


def _load_engine_state() -> Dict[str, Any]:
    return _safe_dict(read_json(LOCAL_ENGINE_STATE_FILE, {}))


def _save_engine_state(state: Dict[str, Any]) -> None:
    write_json(LOCAL_ENGINE_STATE_FILE, state)


def _check_http(url: str) -> bool:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as res:
            return 200 <= getattr(res, "status", 200) < 500
    except Exception:
        return False


def _provider_runtime_url(provider: str, status: Dict[str, Any]) -> str:
    providers = _safe_dict(status.get("providers", {}))

    if provider == "automatic1111":
        return _safe_text(_safe_dict(providers.get("automatic1111", {})).get("api_url", "http://127.0.0.1:7860"))
    if provider == "stable_diffusion":
        return _safe_text(_safe_dict(providers.get("comfyui", {})).get("api_url", "http://127.0.0.1:8188"))
    return ""


def _provider_health_path(provider: str) -> str:
    if provider == "automatic1111":
        return "/sdapi/v1/progress"
    if provider == "stable_diffusion":
        return "/system_stats"
    return ""


def is_provider_running(provider: str) -> Dict[str, Any]:
    status = _load_local_ai_status()
    base_url = _provider_runtime_url(provider, status)
    health_path = _provider_health_path(provider)

    if not base_url or not health_path:
        return {
            "ok": False,
            "provider": provider,
            "running": False,
            "reason": "provider_not_configured",
        }

    running = _check_http(f"{base_url.rstrip('/')}{health_path}")
    return {
        "ok": True,
        "provider": provider,
        "running": running,
        "url": f"{base_url.rstrip('/')}{health_path}",
    }


def _script_path_for_provider(provider: str, status: Dict[str, Any]) -> Path:
    paths = _safe_dict(status.get("paths", {}))
    scripts_root = Path(_safe_text(paths.get("scripts_root", "")))

    if _is_windows():
        if provider == "automatic1111":
            return scripts_root / "start-automatic1111.bat"
        return scripts_root / "start-comfyui.bat"

    if provider == "automatic1111":
        return scripts_root / "start-automatic1111.sh"
    return scripts_root / "start-comfyui.sh"


def _spawn_process(script_path: Path) -> subprocess.Popen:
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


def start_provider(provider: str, timeout_seconds: int = 60) -> Dict[str, Any]:
    provider = _safe_text(provider)
    if provider not in {"stable_diffusion", "automatic1111"}:
        raise ValueError("Provider inválido para arranque local.")

    running_info = is_provider_running(provider)
    if running_info.get("running", False):
        return {
            "ok": True,
            "provider": provider,
            "already_running": True,
            "running": True,
        }

    status = _load_local_ai_status()
    if not status:
        raise ValueError("Local AI ainda não foi configurada.")

    script_path = _script_path_for_provider(provider, status)
    process = _spawn_process(script_path)

    started = time.time()
    while time.time() - started < timeout_seconds:
        time.sleep(2)
        check = is_provider_running(provider)
        if check.get("running", False):
            state = _load_engine_state()
            state[provider] = {
                "started_at": now_iso(),
                "pid": process.pid,
                "script_path": str(script_path),
                "running": True,
            }
            _save_engine_state(state)

            return {
                "ok": True,
                "provider": provider,
                "already_running": False,
                "running": True,
                "pid": process.pid,
            }

    state = _load_engine_state()
    state[provider] = {
        "started_at": now_iso(),
        "pid": process.pid,
        "script_path": str(script_path),
        "running": False,
        "timeout": True,
    }
    _save_engine_state(state)

    return {
        "ok": False,
        "provider": provider,
        "running": False,
        "pid": process.pid,
        "timeout": True,
    }


def ensure_provider_running(provider: str) -> Dict[str, Any]:
    info = is_provider_running(provider)
    if info.get("running", False):
        return {
            "ok": True,
            "provider": provider,
            "running": True,
            "action": "already_running",
        }

    started = start_provider(provider)
    return {
        "ok": bool(started.get("ok", False)),
        "provider": provider,
        "running": bool(started.get("running", False)),
        "action": "started",
        "details": started,
    }


def stop_provider(provider: str) -> Dict[str, Any]:
    provider = _safe_text(provider)
    state = _load_engine_state()
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
    _save_engine_state(state)

    return {
        "ok": True,
        "provider": provider,
        "stopped": True,
    }


def get_engine_manager_status() -> Dict[str, Any]:
    local_ai = _load_local_ai_status()
    engine_state = _load_engine_state()

    comfy = is_provider_running("stable_diffusion")
    a1111 = is_provider_running("automatic1111")

    return {
        "configured": bool(local_ai),
        "default_provider": _safe_text(local_ai.get("default_provider", "stable_diffusion")) or "stable_diffusion",
        "providers": {
            "stable_diffusion": {
                "running": bool(comfy.get("running", False)),
                "health": comfy,
                "state": _safe_dict(engine_state.get("stable_diffusion", {})),
            },
            "automatic1111": {
                "running": bool(a1111.get("running", False)),
                "health": a1111,
                "state": _safe_dict(engine_state.get("automatic1111", {})),
            },
        },
        "updated_at": now_iso(),
}
