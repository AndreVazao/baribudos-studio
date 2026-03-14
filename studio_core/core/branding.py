from __future__ import annotations

from pathlib import Path

from studio_core.core.config import resolve_project_path


def get_brand_root() -> Path:
    return resolve_project_path("public", "brand")


def get_brand_assets() -> dict:
    root = get_brand_root()

    return {
        "root": str(root),
        "studio_logo": str(root / "baribudos-studio-logo.png"),
        "series_logo": str(root / "os-baribudos-logo.png"),
        "protect_badge": str(root / "historia-que-protege-selo.png"),
    }
