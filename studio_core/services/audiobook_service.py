from __future__ import annotations

from typing import Any, Dict
from uuid import uuid4

from studio_core.core.config import resolve_storage_path


def _safe_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value or "")).strip("_") or "audio"


def build_audiobook(
    language_versions: Dict[str, Dict[str, Any]],
    payload: Dict[str, Any]
) -> Dict[str, Any]:
    project_id = str(payload.get("project_id", "")).strip()
    project_title = str(payload.get("project_title", "Projeto")).strip()

    output_dir = resolve_storage_path("exports", project_id, "audiobooks")
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs: Dict[str, Any] = {}

    for language, story in language_versions.items():
        file_name = f"{_safe_name(project_title)}_{_safe_name(language)}.mp3"
        file_path = output_dir / file_name

        # Placeholder técnico até entrares em TTS final
        file_path.write_text(
            f"Audiobook placeholder\n\nTítulo: {project_title}\nLíngua: {language}\n\n{story.get('raw_text', '')}",
            encoding="utf-8"
        )

        outputs[language] = {
            "id": str(uuid4()),
            "type": "audiobook",
            "format": "mp3",
            "language": language,
            "title": project_title,
            "file_name": file_name,
            "file_path": str(file_path),
            "engine": "python-audiobook-builder"
        }

    return outputs
