from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.config import resolve_storage_path
from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item

PROJECTS_FILE = "data/projects.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _get_project(project_id: str) -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        row = _safe_dict(project)
        if _safe_text(row.get("id")) == _safe_text(project_id):
            return row
    return None


def _ffmpeg_exists() -> bool:
    return shutil.which("ffmpeg") is not None


def _ensure_placeholder_png(path: Path) -> None:
    if path.exists():
        return

    try:
        from PIL import Image, ImageDraw

        path.parent.mkdir(parents=True, exist_ok=True)
        img = Image.new("RGB", (1280, 720), (245, 238, 214))
        draw = ImageDraw.Draw(img)
        draw.text((60, 80), "Baribudos Studio", fill=(47, 94, 46))
        draw.text((60, 140), "Placeholder Scene", fill=(47, 94, 46))
        img.save(path)
    except Exception:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"")


def _write_concat_manifest(slides: List[Dict[str, Any]], manifest_path: Path) -> None:
    lines: List[str] = []

    for slide in slides:
        image_path = Path(_safe_text(slide.get("image_path"))).expanduser().resolve()
        if not image_path.exists():
            _ensure_placeholder_png(image_path)

        duration = int(slide.get("duration_seconds", 6) or 6)
        safe_file = str(image_path).replace("\\", "/").replace("'", "'\\''")
        lines.append(f"file '{safe_file}'")
        lines.append(f"duration {duration}")

    if slides:
        last_path = Path(_safe_text(slides[-1].get("image_path"))).expanduser().resolve()
        safe_file = str(last_path).replace("\\", "/").replace("'", "'\\''")
        lines.append(f"file '{safe_file}'")

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text("\n".join(lines), encoding="utf-8")


def render_video_from_package(project_id: str) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    video_package = _safe_dict(project.get("video_storyboard_package", {}))
    slides = [_safe_dict(item) for item in _safe_list(video_package.get("slides", []))]
    if not slides:
        raise ValueError("Sem pacote de vídeo.")

    export_dir = resolve_storage_path("exports", project_id, "final_video")
    export_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = export_dir / "concat_manifest.txt"
    output_path = export_dir / "final_story_video.mp4"

    _write_concat_manifest(slides, manifest_path)

    used_ffmpeg = False
    if _ffmpeg_exists():
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    str(manifest_path),
                    "-vsync",
                    "vfr",
                    "-pix_fmt",
                    "yuv420p",
                    str(output_path),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            used_ffmpeg = True
        except Exception:
            used_ffmpeg = False

    if not used_ffmpeg:
        output_path.write_bytes(b"")

    video_output = {
        "id": str(uuid4()),
        "type": "video",
        "title": f"{_safe_text(project.get('title'))} Final Video",
        "file_name": output_path.name,
        "file_path": str(output_path),
        "slides_count": len(slides),
        "used_ffmpeg": used_ffmpeg,
        "status": "rendered" if used_ffmpeg else "placeholder_rendered",
        "updated_at": now_iso(),
    }

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "outputs": {
                **_safe_dict(current.get("outputs", {})),
                "final_video": video_output,
            },
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "video": video_output,
        "project": updated,
    }


def export_epub_from_story(project_id: str, language: str = "") -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    target_language = _safe_text(language or project.get("language", "pt-PT")) or "pt-PT"
    story_variants = _safe_dict(project.get("language_variants", {}))
    story = _safe_dict(story_variants.get(target_language, {})) or _safe_dict(project.get("story", {}))
    pages = [_safe_dict(item) for item in _safe_list(story.get("pages", []))]
    if not pages:
        raise ValueError("Sem story para exportar.")

    export_dir = resolve_storage_path("exports", project_id, "epub")
    export_dir.mkdir(parents=True, exist_ok=True)

    output_path = export_dir / f"{_safe_text(project.get('title')).replace(' ', '_') or 'book'}_{target_language}.epub"

    epub_payload = {
        "title": _safe_text(project.get("title")),
        "language": target_language,
        "pages": pages,
    }

    output_path.write_text(json.dumps(epub_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    epub_output = {
        "id": str(uuid4()),
        "type": "ebook",
        "format": "epub",
        "title": _safe_text(project.get("title")),
        "language": target_language,
        "file_name": output_path.name,
        "file_path": str(output_path),
        "pages_count": len(pages),
        "status": "exported",
        "updated_at": now_iso(),
    }

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "outputs": {
                **_safe_dict(current.get("outputs", {})),
                "epub_editorial": {
                    **_safe_dict(_safe_dict(current.get("outputs", {})).get("epub_editorial", {})),
                    target_language: epub_output,
                },
            },
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "ebook": epub_output,
        "project": updated,
}
