from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from studio_core.core.config import resolve_storage_path


def _safe_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value or "")).strip("_") or "audio"


def _require_command(command: str) -> None:
    if shutil.which(command) is None:
        raise RuntimeError(f"Dependência em falta: {command}")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Falha no comando externo.")


def _voice_for_language(language: str) -> str:
    mapping = {
        "pt": "pt",
        "pt-PT": "pt",
        "pt-BR": "pt",
        "en": "en",
        "es": "es",
        "fr": "fr",
        "de": "de",
        "it": "it",
        "nl": "nl",
        "zh": "zh",
        "ja": "ja",
    }
    return mapping.get(language, "en")


def build_audiobook(language_versions: Dict[str, Dict[str, Any]], options: Dict[str, Any] | None = None) -> Dict[str, Any]:
    _require_command("espeak")
    _require_command("ffmpeg")

    options = options or {}
    project_id = str(options.get("project_id", uuid4()))
    project_title = str(options.get("project_title", "project")).strip()

    base_dir = resolve_storage_path("audiobooks", project_id)
    base_dir.mkdir(parents=True, exist_ok=True)

    outputs: Dict[str, Any] = {}

    for language, story in language_versions.items():
        lang_dir = base_dir / language
        chapters_dir = lang_dir / "chapters"
        temp_dir = lang_dir / "temp"
        chapters_dir.mkdir(parents=True, exist_ok=True)
        temp_dir.mkdir(parents=True, exist_ok=True)

        chapter_files: list[Path] = []

        for page in story.get("pages", []) or []:
            page_number = int(page.get("pageNumber", 1))
            text = str(page.get("text", "")).strip()
            wav_path = temp_dir / f"page_{page_number}.wav"
            mp3_path = chapters_dir / f"page_{page_number}.mp3"

            _run([
                "espeak",
                "-v",
                _voice_for_language(language),
                "-w",
                str(wav_path),
                text,
            ])

            _run([
                "ffmpeg",
                "-y",
                "-i",
                str(wav_path),
                "-codec:a",
                "libmp3lame",
                "-q:a",
                "2",
                str(mp3_path),
            ])

            chapter_files.append(mp3_path)

        concat_file = temp_dir / "concat.txt"
        _write_text(
            concat_file,
            "\n".join(f"file '{chapter.as_posix()}'" for chapter in chapter_files)
        )

        final_name = f"{_safe_name(project_title)}_{language}.mp3"
        final_path = lang_dir / final_name

        _run([
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            str(final_path),
        ])

        outputs[language] = {
            "id": str(uuid4()),
            "language": language,
            "final_file": final_name,
            "final_path": str(final_path),
            "engine": "python-audio-real",
            "chapter_count": len(chapter_files)
        }

    return outputs
