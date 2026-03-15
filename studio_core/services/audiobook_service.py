from __future__ import annotations

import shutil
import subprocess
import wave
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from studio_core.core.config import resolve_storage_path


def _safe_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value or "")).strip("_") or "audio"


def _pick_tts_command() -> str | None:
    if shutil.which("espeak-ng"):
        return "espeak-ng"
    if shutil.which("espeak"):
        return "espeak"
    return None


def _has_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def _voice_for_language(language: str) -> str:
    lang = str(language or "").strip().lower()

    mapping = {
        "pt": "pt",
        "pt-pt": "pt-pt",
        "pt-br": "pt-br",
        "en": "en",
        "en-us": "en-us",
        "en-gb": "en-gb",
        "es": "es",
        "fr": "fr",
        "de": "de",
        "it": "it",
        "nl": "nl",
        "zh": "zh",
        "ja": "ja",
    }

    return mapping.get(lang, lang.split("-")[0] if "-" in lang else "en")


def _normalize_story_text(story: Dict[str, Any], title: str, language: str) -> str:
    raw_text = str(story.get("raw_text", "")).strip()
    if raw_text:
        return raw_text

    pages = story.get("pages", [])
    if isinstance(pages, list) and pages:
        chunks = []
        for page in pages:
            if not isinstance(page, dict):
                continue
            page_title = str(page.get("title", "")).strip()
            page_text = str(page.get("text", "")).strip()
            if page_title:
                chunks.append(page_title)
            if page_text:
                chunks.append(page_text)
        if chunks:
            return "\n\n".join(chunks)

    return f"{title}. Conteúdo indisponível na língua {language}."


def _write_silence_wav(path: Path, seconds: float = 1.0, framerate: int = 22050) -> None:
    nframes = int(seconds * framerate)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(framerate)
        silence = b"\x00\x00" * nframes
        wav_file.writeframes(silence)


def _generate_wav_with_espeak(tts_cmd: str, voice: str, text: str, wav_path: Path) -> None:
    subprocess.run(
        [
            tts_cmd,
            "-v",
            voice,
            "-s",
            "145",
            "-w",
            str(wav_path),
            text,
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _convert_wav_to_mp3(wav_path: Path, mp3_path: Path) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(wav_path),
            "-codec:a",
            "libmp3lame",
            "-qscale:a",
            "2",
            str(mp3_path),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def build_audiobook(
    language_versions: Dict[str, Dict[str, Any]],
    payload: Dict[str, Any]
) -> Dict[str, Any]:
    project_id = str(payload.get("project_id", "")).strip()
    project_title = str(payload.get("project_title", "Projeto")).strip()

    output_dir = resolve_storage_path("exports", project_id, "audiobooks")
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs: Dict[str, Any] = {}

    tts_cmd = _pick_tts_command()
    ffmpeg_ok = _has_ffmpeg()

    for language, story in language_versions.items():
        safe_base = f"{_safe_name(project_title)}_{_safe_name(language)}"
        wav_name = f"{safe_base}.wav"
        wav_path = output_dir / wav_name

        text = _normalize_story_text(story, project_title, language)
        voice = _voice_for_language(language)

        engine = "wav-fallback"
        final_path = wav_path
        final_name = wav_name
        audio_format = "wav"

        try:
            if tts_cmd:
                _generate_wav_with_espeak(tts_cmd, voice, text, wav_path)
                engine = f"{tts_cmd}-tts"
            else:
                _write_silence_wav(wav_path, seconds=1.0)
                engine = "silent-wav-fallback"

            if ffmpeg_ok:
                mp3_name = f"{safe_base}.mp3"
                mp3_path = output_dir / mp3_name
                _convert_wav_to_mp3(wav_path, mp3_path)
                final_path = mp3_path
                final_name = mp3_name
                audio_format = "mp3"
                engine = f"{engine}+ffmpeg-mp3"
        except Exception:
            if not wav_path.exists():
                _write_silence_wav(wav_path, seconds=1.0)
            final_path = wav_path
            final_name = wav_name
            audio_format = "wav"
            engine = "error-fallback-wav"

        outputs[language] = {
            "id": str(uuid4()),
            "type": "audiobook",
            "format": audio_format,
            "language": language,
            "title": project_title,
            "file_name": final_name,
            "file_path": str(final_path),
            "engine": engine
        }

    return outputs
