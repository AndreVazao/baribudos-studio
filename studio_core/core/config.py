from __future__ import annotations

import os
import platform
from dataclasses import dataclass, field
from pathlib import Path
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
    clean_parts = [str(part).strip("/\\") for part in parts if str(part).strip("/\\")]
    return APP_CONFIG.storage_root.joinpath(*clean_parts).resolve()


def resolve_project_path(*parts: str) -> Path:
    return APP_CONFIG.project_root.joinpath(*parts).resolve()
