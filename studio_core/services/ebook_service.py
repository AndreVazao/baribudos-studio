from __future__ import annotations

from typing import Any, Dict
from uuid import uuid4

from studio_core.core.config import resolve_storage_path
from studio_core.services.ip_runtime_service import load_ip_runtime


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
    saga_id: str = "baribudos",
) -> Dict[str, Any]:
    runtime = load_ip_runtime(saga_id)
    metadata = runtime.get("metadata", {}) or {}

    final_author = str(author or metadata.get("author_default") or "Autor").strip()
    series_name = str(metadata.get("series_name") or runtime.get("name") or "").strip()
    producer = str(metadata.get("producer") or "").strip()
    tagline = str(metadata.get("tagline") or "").strip()
    genre = str(metadata.get("genre") or "").strip()
    description = str(metadata.get("description") or "").strip()

    output_dir = resolve_storage_path("exports", project_id, "ebooks")
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{_safe_name(project_title)}_{_safe_name(language)}.epub"
    file_path = output_dir / file_name

    content = [
        f"Título: {project_title}",
        f"Autor: {final_author}",
        f"Língua: {language}",
        f"Série: {series_name}",
        f"Producer: {producer}",
        f"Tagline: {tagline}",
        f"Género: {genre}",
        f"Descrição: {description}",
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
        "author": final_author,
        "series_name": series_name,
        "producer": producer,
        "file_name": file_name,
        "file_path": str(file_path),
        "cover_path": cover_path,
        "engine": "python-ebook-builder"
    }
