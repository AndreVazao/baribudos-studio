from __future__ import annotations

import os
import platform
from dataclasses import dataclass, field
from pathlib import Path, PureWindowsPath
from typing import Dict


def _project_root() -> Path:
    return Path.cwd().resolve()


def _storage_root() -> Path:
    custom = os.getenv("BARIBUDOS_STORAGE_ROOT", "").strip()
    if custom:
      return Path(custom).expanduser().resolve()
    return _project_root() / "storage"


@dataclass(slots=True)
class AppConfig:
    app_name: str = "Baribudos Studio"
    app_version: str = "1.0.0"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8787"))
    environment: str = os.getenv("APP_ENV", "development")
    project_root: Path = field(default_factory=_project_root)
    storage_root: Path = field(default_factory=_storage_root)

    def folder_map(self) -> Dict[str, Path]:
        return {
            "data": self.storage_root / "data",
            "uploads": self.storage_root / "uploads",
            "exports": self.storage_root / "exports",
            "covers": self.storage_root / "covers",
            "assets": self.storage_root / "assets",
            "voices": self.storage_root / "voices",
            "audiobooks": self.storage_root / "audiobooks",
            "videos": self.storage_root / "videos",
            "temp": self.storage_root / "temp",
            "logs": self.storage_root / "logs",
        }

    def system_info(self) -> Dict[str, str | int]:
        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "python_version": platform.python_version(),
            "machine": platform.machine(),
        }


APP_CONFIG = AppConfig()


def resolve_storage_path(*parts: str) -> Path:
    root = APP_CONFIG.storage_root.expanduser().resolve()
    clean_parts = []
    for part in parts:
        raw_part = str(part).strip()
        if not raw_part:
            continue

        # Reject absolute paths using both host and Windows semantics. The
        # Studio runs on Windows as well as CI/Linux, so a Windows drive or
        # UNC path must not become an apparently relative POSIX filename.
        windows_part = PureWindowsPath(raw_part)
        if (
            Path(raw_part).is_absolute()
            or windows_part.is_absolute()
            or windows_part.root
            or windows_part.drive
        ):
            raise ValueError("storage_path_must_be_relative")

        # Normalize separators before resolving so Windows-style traversal
        # is also evaluated as path traversal on POSIX CI.
        clean = raw_part.replace("\\\\", "/").replace("\\", "/").strip("/")
        if clean:
            clean_parts.append(clean)

    candidate = root.joinpath(*clean_parts).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("storage_path_outside_root") from exc
    return candidate


def resolve_project_path(*parts: str) -> Path:
    return APP_CONFIG.project_root.joinpath(*parts).resolve()
