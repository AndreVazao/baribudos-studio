from __future__ import annotations

import os


# =========================================================
# CDN CONFIG
# =========================================================

CDN_BASE_URL = os.getenv("STUDIO_CDN_BASE_URL", "").rstrip("/")
STORAGE_PUBLIC_PREFIX = os.getenv("STUDIO_STORAGE_PUBLIC_PREFIX", "/storage").rstrip("/")


# =========================================================
# INTERNAL
# =========================================================

def _normalize_path(storage_path: str) -> str:
    path = str(storage_path or "").strip()
    path = path.replace("\\", "/")
    path = path.lstrip("/")
    return path


# =========================================================
# PUBLIC RESOLVER
# =========================================================

def resolve_cdn_url(storage_path: str, version: int | None = None) -> str:
    """
    Resolve public URL for any stored asset.

    Supports:
    - local storage (/storage mount)
    - external CDN
    - cache busting
    - versioning
    - future S3 / Cloudflare / R2
    """

    path = _normalize_path(storage_path)
    if not path:
        return ""

    if CDN_BASE_URL:
        url = f"{CDN_BASE_URL}/{path}"
    else:
        url = f"{STORAGE_PUBLIC_PREFIX}/{path}"

    if version is not None:
        url = f"{url}?v={int(version)}"

    return url
