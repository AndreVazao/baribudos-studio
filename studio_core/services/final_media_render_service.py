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
from studio_core.services.ebook_service import build_epub
from studio_core.services.ip_runtime_service import load_ip_runtime

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

    raise ValueError(
        "final_character_animation_pipeline_not_implemented: "
        "o renderizador atual apenas montava slides/placeholder sem animação de personagens "
        "nem banda sonora de minissérie validada; usa a saída animatic_only enquanto o motor final não existe."
    )


def export_epub_from_story(project_id: str, language: str = "") -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    target_language = _safe_text(language or project.get("language", "pt-PT")) or "pt-PT"
    story_variants = _safe_dict(project.get("language_variants", {}))
    story = _safe_dict(story_variants.get(target_language, {})) or _safe_dict(project.get("story", {}))
    if not story or not _safe_list(story.get("pages", [])):
        raise ValueError("Sem story paginada para exportar.")

    has_version_approval = any(
        key in story for key in ("approved", "editorial_status", "approval_state")
    )
    version_approved = (
        story.get("approved") is True
        or _safe_text(story.get("editorial_status")).lower() == "approved"
        or _safe_text(story.get("approval_state")).lower() == "approved"
    )
    project_approved = (
        target_language == _safe_text(project.get("language"))
        and (
            project.get("approved") is True
            or _safe_text(project.get("editorial_status")).lower() == "approved"
        )
    )
    if not (version_approved if has_version_approval else project_approved):
        raise ValueError("Aprovação editorial explícita necessária antes de exportar EPUB.")

    saga_id = _safe_text(project.get("saga_slug")) or "baribudos"
    runtime = load_ip_runtime(saga_id)
    metadata = _safe_dict(runtime.get("metadata", {}))
    ebook_output = build_epub(
        story,
        project_id=project_id,
        project_title=_safe_text(project.get("title")) or "Projeto",
        language=target_language,
        author=_safe_text(metadata.get("author_default")) or "Autor",
        cover_path=_safe_text(project.get("cover_image")) or None,
        saga_id=saga_id,
    )

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "outputs": {
                **_safe_dict(current.get("outputs", {})),
                "epub_editorial": {
                    **_safe_dict(_safe_dict(current.get("outputs", {})).get("epub_editorial", {})),
                    target_language: ebook_output,
                },
            },
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "ebook": ebook_output,
        "project": updated,
    }
