from __future__ import annotations


def resolve_cdn_url(storage_path: str, version: int | None = None) -> str:
    path = str(storage_path or "").strip().replace("\\", "/").lstrip("/")
    if not path:
        return ""

    base = "/storage"
    url = f"{base}/{path}"

    if version is not None:
        url = f"{url}?v={int(version)}"

    return url
