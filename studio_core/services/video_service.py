from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from studio_core.core.config import resolve_storage_path


def _safe_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value or "")).strip("_") or "video"


def _require_command(command: str) -> None:
    if shutil.which(command) is None:
        raise RuntimeError(f"Dependência em falta: {command}")


def _run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Falha no comando externo.")


def _escape_drawtext(value: str) -> str:
    return (
        str(value or "")
        .replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace(",", "\\,")
        .replace("%", "\\%")
    )


def build_series_episode(story: Dict[str, Any], options: Dict[str, Any] | None = None) -> Dict[str, Any]:
    _require_command("ffmpeg")

    options = options or {}
    project_id = str(options.get("project_id", uuid4()))
    project_title = str(options.get("project_title", story.get("title", "episode"))).strip()
    language = str(options.get("language", story.get("language", "pt-PT"))).strip()

    output_dir = resolve_storage_path("videos", project_id, language)
    scenes_dir = output_dir / "scenes"
    temp_dir = output_dir / "temp"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    scene_files: list[Path] = []

    for page in story.get("pages", []) or []:
        number = int(page.get("pageNumber", 1))
        text = _escape_drawtext(str(page.get("text", "")).strip())
        scene_path = scenes_dir / f"scene_{number}.mp4"

        vf = (
            "drawtext="
            f"fontcolor=white:fontsize=34:"
            f"text='{text}':"
            "x=(w-text_w)/2:"
            "y=(h-text_h)/2"
        )

        _run([
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=#2F5E2E:s=1280x720:d=6",
            "-vf",
            vf,
            "-pix_fmt",
            "yuv420p",
            str(scene_path),
        ])

        scene_files.append(scene_path)

    concat_file = temp_dir / "concat.txt"
    concat_file.write_text(
        "\n".join(f"file '{scene.as_posix()}'" for scene in scene_files),
        encoding="utf-8",
    )

    final_name = f"{_safe_name(project_title)}_{language}.mp4"
    final_path = output_dir / final_name

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

    return {
        "id": str(uuid4()),
        "language": language,
        "final_file": final_name,
        "final_path": str(final_path),
        "engine": "python-video-real",
        "scene_count": len(scene_files)
    }
