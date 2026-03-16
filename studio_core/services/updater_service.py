from __future__ import annotations

import json
import os
import platform
import urllib.request
from pathlib import Path
from typing import Any, Dict, Tuple

from studio_core.core.config import resolve_project_path, resolve_storage_path
from studio_core.core.models import now_iso

DEFAULT_UPDATE_URL = os.getenv(
    "BARIBUDOS_UPDATE_URL",
    "https://raw.githubusercontent.com/AndreVazao/baribudos-studio/main/deploy/version.json",
).strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _version_file() -> Path:
    return resolve_project_path("deploy", "version.json")


def _default_local_version() -> Dict[str, Any]:
    return {
        "version": "0.1.0",
        "channel": "stable",
        "app_name": "Baribudos Studio",
        "build": "",
        "published_at": "",
    }


def _parse_version(version: str) -> Tuple[int, ...]:
    raw = _safe_text(version).replace("-", ".").replace("_", ".")
    parts = []
    for item in raw.split("."):
        try:
            parts.append(int(item))
        except Exception:
            parts.append(0)
    return tuple(parts or [0])


def _current_platform_key() -> str:
    name = platform.system().lower()
    if "windows" in name:
        return "windows"
    if "android" in name:
        return "android"
    if "darwin" in name:
        return "macos"
    return "linux"


def _downloads_dir() -> Path:
    path = resolve_storage_path("updates")
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_local_version_info() -> Dict[str, Any]:
    path = _version_file()
    if not path.exists():
        return _default_local_version()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {
            **_default_local_version(),
            **_safe_dict(data),
        }
    except Exception:
        return _default_local_version()


def fetch_remote_version_info(update_url: str = "") -> Dict[str, Any]:
    url = _safe_text(update_url) or DEFAULT_UPDATE_URL
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=20) as res:
        raw = res.read().decode("utf-8")
        data = json.loads(raw) if raw else {}
        return _safe_dict(data)


def compare_versions(local_version: str, remote_version: str) -> int:
    left = _parse_version(local_version)
    right = _parse_version(remote_version)

    if left < right:
        return -1
    if left > right:
        return 1
    return 0


def _resolve_download_url(remote: Dict[str, Any], channel: str = "") -> str:
    channel = _safe_text(channel) or _safe_text(remote.get("channel", "stable")) or "stable"
    platform_key = _current_platform_key()

    channels = _safe_dict(remote.get("channels", {}))
    channel_block = _safe_dict(channels.get(channel, {}))
    platform_urls = _safe_dict(channel_block.get("platforms", {}))

    if _safe_text(platform_urls.get(platform_key)):
        return _safe_text(platform_urls.get(platform_key))

    legacy_key = f"download_url_{platform_key}"
    if _safe_text(remote.get(legacy_key)):
        return _safe_text(remote.get(legacy_key))

    if _safe_text(remote.get("download_url")):
        return _safe_text(remote.get("download_url"))

    return ""


def _file_name_from_url(url: str) -> str:
    raw = _safe_text(url).split("?")[0].split("#")[0].strip()
    name = Path(raw).name
    return name or f"baribudos_update_{_current_platform_key()}"


def check_for_updates(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    local = get_local_version_info()

    requested_channel = _safe_text(payload.get("channel", "")) or _safe_text(local.get("channel", "stable")) or "stable"
    update_url = _safe_text(payload.get("update_url", "")) or DEFAULT_UPDATE_URL

    try:
        remote = fetch_remote_version_info(update_url)
        remote_channel = _safe_text(remote.get("channel", "")) or requested_channel
        remote_version = _safe_text(remote.get("version", "0.0.0")) or "0.0.0"
        local_version = _safe_text(local.get("version", "0.0.0")) or "0.0.0"

        cmp = compare_versions(local_version, remote_version)
        update_available = cmp < 0

        return {
            "ok": True,
            "checked_at": now_iso(),
            "update_url": update_url,
            "platform": _current_platform_key(),
            "channel": requested_channel,
            "local": local,
            "remote": remote,
            "update_available": update_available,
            "download_url": _resolve_download_url(remote, requested_channel),
            "comparison": cmp,
            "remote_channel": remote_channel,
        }
    except Exception as exc:
        return {
            "ok": False,
            "checked_at": now_iso(),
            "update_url": update_url,
            "platform": _current_platform_key(),
            "channel": requested_channel,
            "local": local,
            "remote": {},
            "update_available": False,
            "download_url": "",
            "error": str(exc),
        }


def download_update(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}

    checked = check_for_updates(payload)
    if not checked.get("ok", False):
        raise RuntimeError(_safe_text(checked.get("error", "Falha ao verificar updates.")))

    if not checked.get("update_available", False):
        return {
            "ok": True,
            "update_available": False,
            "downloaded": False,
            "message": "Sem atualização disponível.",
            "check": checked,
        }

    download_url = _safe_text(payload.get("download_url", "")) or _safe_text(checked.get("download_url", ""))
    if not download_url:
        raise RuntimeError("Sem URL de download para esta plataforma.")

    file_name = _safe_text(payload.get("file_name", "")) or _file_name_from_url(download_url)
    target_path = _downloads_dir() / file_name

    req = urllib.request.Request(download_url, method="GET")
    with urllib.request.urlopen(req, timeout=600) as res:
        target_path.write_bytes(res.read())

    return {
        "ok": True,
        "update_available": True,
        "downloaded": True,
        "download_url": download_url,
        "file_name": target_path.name,
        "file_path": str(target_path),
        "storage_url": f"/storage/updates/{target_path.name}",
        "check": checked,
    }
