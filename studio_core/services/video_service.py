from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont

from studio_core.core.config import resolve_storage_path


def _safe_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value or "")).strip("_") or "video"


def _has_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def _has_ffprobe() -> bool:
    return shutil.which("ffprobe") is not None


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/verdanab.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size)
            except Exception:
                pass
    return ImageFont.load_default()


def _fit_font(text: str, max_width: int, start_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    size = start_size
    while size >= 18:
        font = _get_font(size)
        bbox = font.getbbox(text)
        if (bbox[2] - bbox[0]) <= max_width:
            return font
        size -= 2
    return _get_font(18)


def _audio_duration_seconds(audio_path: Path) -> float:
    if not _has_ffprobe():
        return 6.0
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(audio_path),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return max(1.0, float((result.stdout or "6").strip()))
    except Exception:
        return 6.0


def _build_fallback_frame(output_path: Path, title: str, language: str) -> None:
    width, height = 1600, 900
    image = Image.new("RGB", (width, height), (245, 238, 214))
    draw = ImageDraw.Draw(image)

    title_font = _fit_font(title, width - 160, 72)
    lang_font = _fit_font(f"Língua: {language}", width - 160, 34)

    bbox = title_font.getbbox(title)
    title_w = bbox[2] - bbox[0]
    draw.text(((width - title_w) // 2, 320), title, font=title_font, fill=(47, 94, 46))

    lang_text = f"Língua: {language}"
    bbox2 = lang_font.getbbox(lang_text)
    lang_w = bbox2[2] - bbox2[0]
    draw.text(((width - lang_w) // 2, 430), lang_text, font=lang_font, fill=(80, 80, 80))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format="PNG")


def _normalize_sequence_frames(sequence_frames: Any) -> List[str]:
    if not isinstance(sequence_frames, list):
        return []
    result: List[str] = []
    for item in sequence_frames:
        if isinstance(item, dict):
            path = str(item.get("image_path", "")).strip()
        else:
            path = str(item or "").strip()
        if path and Path(path).exists():
            result.append(path)
    return result


def _write_concat_file(frame_paths: List[str], duration_per_frame: float, concat_path: Path) -> None:
    lines: List[str] = []
    for frame_path in frame_paths:
        safe_path = Path(frame_path).resolve().as_posix().replace("'", r"'\''")
        lines.append(f"file '{safe_path}'")
        lines.append(f"duration {duration_per_frame:.3f}")
    if frame_paths:
        safe_last = Path(frame_paths[-1]).resolve().as_posix().replace("'", r"'\''")
        lines.append(f"file '{safe_last}'")
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_video_with_audio_slideshow(
    frame_paths: List[str],
    audio_path: Path,
    output_path: Path,
    temp_dir: Path,
) -> None:
    duration = _audio_duration_seconds(audio_path)
    per_frame = max(1.2, duration / max(1, len(frame_paths)))

    concat_path = temp_dir / "frames.txt"
    slideshow_path = temp_dir / "slideshow.mp4"
    _write_concat_file(frame_paths, per_frame, concat_path)

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            "-vf",
            "scale=1600:900:force_original_aspect_ratio=decrease,pad=1600:900:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            "-vsync",
            "vfr",
            "-pix_fmt",
            "yuv420p",
            str(slideshow_path),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(slideshow_path),
            "-i",
            str(audio_path),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            str(output_path),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _build_silent_slideshow(
    frame_paths: List[str],
    output_path: Path,
    temp_dir: Path,
    total_duration: int = 6,
) -> None:
    per_frame = max(1.2, total_duration / max(1, len(frame_paths)))
    concat_path = temp_dir / "frames.txt"
    _write_concat_file(frame_paths, per_frame, concat_path)

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            "-f",
            "lavfi",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-vf",
            "scale=1600:900:force_original_aspect_ratio=decrease,pad=1600:900:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            "-vsync",
            "vfr",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            str(output_path),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _build_video_with_audio_single(image_path: Path, audio_path: Path, output_path: Path) -> None:
    duration = _audio_duration_seconds(audio_path)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(image_path),
            "-i",
            str(audio_path),
            "-c:v",
            "libx264",
            "-t",
            str(duration),
            "-pix_fmt",
            "yuv420p",
            "-vf",
            "scale=1600:900:force_original_aspect_ratio=decrease,pad=1600:900:(ow-iw)/2:(oh-ih)/2",
            "-c:a",
            "aac",
            "-shortest",
            str(output_path),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _build_silent_single(image_path: Path, output_path: Path, duration: int = 6) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(image_path),
            "-f",
            "lavfi",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-c:v",
            "libx264",
            "-t",
            str(duration),
            "-pix_fmt",
            "yuv420p",
            "-vf",
            "scale=1600:900:force_original_aspect_ratio=decrease,pad=1600:900:(ow-iw)/2:(oh-ih)/2",
            "-c:a",
            "aac",
            "-shortest",
            str(output_path),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def build_series_episode(
    story: Dict[str, Any],
    payload: Dict[str, Any]
) -> Dict[str, Any]:
    project_id = str(payload.get("project_id", "")).strip()
    project_title = str(payload.get("project_title", "Projeto")).strip()
    language = str(payload.get("language", story.get("language", "pt-PT"))).strip()
    cover_path = str(payload.get("cover_path", "")).strip()
    audio_path = str(payload.get("audio_path", "")).strip()
    sequence_frames = _normalize_sequence_frames(payload.get("sequence_frames", []))

    output_dir = resolve_storage_path("exports", project_id, "videos")
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{_safe_name(project_title)}_{_safe_name(language)}.mp4"
    file_path = output_dir / file_name

    frame_path = output_dir / f"{_safe_name(project_title)}_{_safe_name(language)}_frame.png"
    temp_dir = output_dir / f".tmp_video_{_safe_name(project_title)}_{_safe_name(language)}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    if cover_path and Path(cover_path).exists():
        fallback_image = Path(cover_path)
    else:
        _build_fallback_frame(frame_path, project_title, language)
        fallback_image = frame_path

    if not _has_ffmpeg():
        raise RuntimeError("FFmpeg não está instalado. Não é possível gerar vídeo real.")

    try:
        if sequence_frames:
            if audio_path and Path(audio_path).exists():
                _build_video_with_audio_slideshow(sequence_frames, Path(audio_path), file_path, temp_dir)
                engine = "ffmpeg-slideshow+audio"
            else:
                _build_silent_slideshow(sequence_frames, file_path, temp_dir, total_duration=6)
                engine = "ffmpeg-slideshow-silent"
        else:
            if audio_path and Path(audio_path).exists():
                _build_video_with_audio_single(fallback_image, Path(audio_path), file_path)
                engine = "ffmpeg-single+audio"
            else:
                _build_silent_single(fallback_image, file_path, duration=6)
                engine = "ffmpeg-single-silent"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        "id": str(uuid4()),
        "type": "video",
        "format": "mp4",
        "language": language,
        "title": project_title,
        "file_name": file_name,
        "file_path": str(file_path),
        "engine": engine,
        "frames_used": len(sequence_frames),
        }
