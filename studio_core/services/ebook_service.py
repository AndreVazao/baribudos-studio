from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from studio_core.core.config import resolve_storage_path


def _safe_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value or "")).strip("_") or "ebook"


def build_epub(
    story: Dict[str, Any],
    *,
    project_id: str,
    project_title: str,
    language: str,
    author: str,
    cover_path: str | None = None,
) -> Dict[str, Any]:
    output_dir = resolve_storage_path("exports", project_id, "ebooks")
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{_safe_name(project_title)}_{_safe_name(language)}.epub"
    file_path = output_dir / file_name

    # Placeholder técnico até entrares no gerador EPUB final
    content = [
        f"Título: {project_title}",
        f"Autor: {author}",
        f"Língua: {language}",
        f"Capa: {cover_path or ''}",
        "",
        story.get("raw_text", ""),
    ]
    file_path.write_text("\n".join(content), encoding="utf-8")

    return {
        "id": str(uuid4()),
        "type": "ebook",
        "format": "epub",
        "language": language,
        "title": project_title,
        "file_name": file_name,
        "file_path": str(file_path),
        "cover_path": cover_path,
        "engine": "python-ebook-builder"
    }
