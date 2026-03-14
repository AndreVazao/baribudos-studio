from __future__ import annotations

from typing import Any, Dict
from uuid import uuid4

from studio_core.core.config import resolve_storage_path


def _safe_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value or "")).strip("_") or "video"


def build_series_episode(
    story: Dict[str, Any],
    payload: Dict[str, Any]
) -> Dict[str, Any]:
    project_id = str(payload.get("project_id", "")).strip()
    project_title = str(payload.get("project_title", "Projeto")).strip()
    language = str(payload.get("language", story.get("language", "pt-PT"))).strip()

    output_dir = resolve_storage_path("exports", project_id, "videos")
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{_safe_name(project_title)}_{_safe_name(language)}.mp4"
    file_path = output_dir / file_name

    # Placeholder técnico até entrares no render real
    file_path.write_text(
        f"Video placeholder\n\nTítulo: {project_title}\nLíngua: {language}\n\n{story.get('raw_text', '')}",
        encoding="utf-8"
    )

    return {
        "id": str(uuid4()),
        "type": "video",
        "format": "mp4",
        "language": language,
        "title": project_title,
        "file_name": file_name,
        "file_path": str(file_path),
        "engine": "python-video-builder"
    }
