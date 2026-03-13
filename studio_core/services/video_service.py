from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from studio_core.core.config import resolve_storage_path


def _safe_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value or "")).strip("_") or "video"


def _write_placeholder_mp4(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_series_episode(story: Dict[str, Any], options: Dict[str, Any] | None = None) -> Dict[str, Any]:
    options = options or {}
    project_id = str(options.get("project_id", uuid4()))
    project_title = str(options.get("project_title", story.get("title", "episode"))).strip()
    language = str(options.get("language", story.get("language", "pt-PT"))).strip()

    output_dir = resolve_storage_path("videos", project_id, language)
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{_safe_name(project_title)}_{language}.mp4"
    final_path = output_dir / file_name

    page_summary = "\n".join(
        f"CENA {page.get('pageNumber')}: {page.get('text', '')}"
        for page in story.get("pages", []) or []
    )

    _write_placeholder_mp4(
        final_path,
        f"PLACEHOLDER VIDEO FILE\nLANG={language}\nTITLE={project_title}\n\n{page_summary}"
    )

    return {
        "id": str(uuid4()),
        "language": language,
        "final_file": file_name,
        "final_path": str(final_path),
        "engine": "placeholder-local-video"
  }
