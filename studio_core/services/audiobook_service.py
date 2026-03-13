from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from studio_core.core.config import resolve_storage_path


def _safe_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value or "")).strip("_") or "audio"


def _write_placeholder_mp3(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_audiobook(language_versions: Dict[str, Dict[str, Any]], options: Dict[str, Any] | None = None) -> Dict[str, Any]:
    options = options or {}
    project_id = str(options.get("project_id", uuid4()))
    project_title = str(options.get("project_title", "project")).strip()

    base_dir = resolve_storage_path("audiobooks", project_id)
    base_dir.mkdir(parents=True, exist_ok=True)

    outputs: Dict[str, Any] = {}

    for language, story in language_versions.items():
        lang_dir = base_dir / language
        lang_dir.mkdir(parents=True, exist_ok=True)

        file_name = f"{_safe_name(project_title)}_{language}.mp3"
        final_path = lang_dir / file_name

        combined_text = "\n\n".join(
            str(page.get("text", "")).strip()
            for page in story.get("pages", []) or []
        )

        _write_placeholder_mp3(
            final_path,
            f"PLACEHOLDER AUDIOBOOK FILE\nLANG={language}\nTITLE={project_title}\n\n{combined_text}"
        )

        outputs[language] = {
            "id": str(uuid4()),
            "language": language,
            "final_file": file_name,
            "final_path": str(final_path),
            "engine": "placeholder-local-audio"
        }

    return outputs
