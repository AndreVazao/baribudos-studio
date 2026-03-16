from __future__ import annotations

import json
import shutil
import subprocess
import urllib.request
import wave
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.config import resolve_storage_path
from studio_core.core.storage import read_json
from studio_core.services.local_audio_engine_manager_service import ensure_audio_provider_running
from studio_core.services.voice_profile_service import get_default_voice_sample_path

LOCAL_AUDIO_STATUS_FILE = "data/local_audio_status.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_name(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value or "")).strip("_") or "audio"


def _load_local_audio_status() -> Dict[str, Any]:
    return _safe_dict(read_json(LOCAL_AUDIO_STATUS_FILE, {}))


def _resolve_default_provider(requested_provider: str = "") -> str:
    if _safe_text(requested_provider):
        return _safe_text(requested_provider)

    status = _load_local_audio_status()
    provider = _safe_text(status.get("default_provider", "system_tts"))
    return provider or "system_tts"


def _provider_api_url(provider: str) -> str:
    status = _load_local_audio_status()
    providers = _safe_dict(status.get("providers", {}))
    return _safe_text(_safe_dict(providers.get(provider, {})).get("api_url", ""))


def _espeak_voice_for_language(language: str) -> str:
    lang = _safe_text(language).lower()
    mapping = {
        "pt": "pt",
        "pt-pt": "pt",
        "pt-br": "pt-br",
        "en": "en",
        "en-us": "en-us",
        "en-gb": "en-gb",
        "es": "es",
        "fr": "fr",
        "de": "de",
        "it": "it",
        "nl": "nl",
    }
    return mapping.get(lang, "en")


def _write_silent_wav(output_path: Path, duration_seconds: float = 2.0, sample_rate: int = 22050) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    frames = int(sample_rate * max(0.2, duration_seconds))
    with wave.open(str(output_path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00\x00" * frames)


def _espeak_command() -> str:
    if shutil.which("espeak"):
        return "espeak"
    if shutil.which("espeak-ng"):
        return "espeak-ng"
    return ""


def _synthesize_system_tts(text: str, output_path: Path, language: str) -> Dict[str, Any]:
    text = _safe_text(text)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = _espeak_command()
    if command:
        try:
            subprocess.run(
                [
                    command,
                    "-v",
                    _espeak_voice_for_language(language),
                    "-w",
                    str(output_path),
                    text or "Texto vazio.",
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return {
                "ok": True,
                "provider": "system_tts",
                "file_path": str(output_path),
            }
        except Exception:
            pass

    approx_seconds = max(1.5, len(text.split()) * 0.45) if text else 2.0
    _write_silent_wav(output_path, duration_seconds=approx_seconds)
    return {
        "ok": False,
        "provider": "system_tts",
        "fallback_used": True,
        "file_path": str(output_path),
    }


def _http_post_json(url: str, payload: Dict[str, Any], timeout: int = 600) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as res:
        raw = res.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def _synthesize_http_provider(
    provider: str,
    text: str,
    output_path: Path,
    language: str,
    speaker_wav: str = "",
) -> Dict[str, Any]:
    api_url = _provider_api_url(provider)
    if not api_url:
        raise RuntimeError(f"API URL não configurada para {provider}.")

    payload = {
        "text": _safe_text(text),
        "language": _safe_text(language) or "en",
        "output_path": str(output_path),
    }

    if provider == "xtts" and _safe_text(speaker_wav):
        payload["speaker_wav"] = _safe_text(speaker_wav)

    result = _http_post_json(f"{api_url.rstrip('/')}/synthesize", payload)
    if not bool(result.get("ok", False)):
        raise RuntimeError(f"Falha no provider {provider}.")

    return {
        "ok": True,
        "provider": provider,
        "file_path": _safe_text(result.get("file_path")) or str(output_path),
    }


def _merge_wavs(inputs: List[Path], output_path: Path) -> None:
    if not inputs:
        _write_silent_wav(output_path, duration_seconds=2.0)
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    first = None
    data_chunks = []

    for wav_path in inputs:
        with wave.open(str(wav_path), "rb") as wav_file:
            params = wav_file.getparams()
            frames = wav_file.readframes(wav_file.getnframes())

        if first is None:
            first = params
        data_chunks.append(frames)

    with wave.open(str(output_path), "wb") as out:
        out.setparams(first)
        for chunk in data_chunks:
            out.writeframes(chunk)


def _page_text(page: Dict[str, Any]) -> str:
    return _safe_text(page.get("text", ""))


def _story_pages(story: Dict[str, Any]) -> List[Dict[str, Any]]:
    pages = _safe_list(story.get("pages", []))
    if pages:
        return [_safe_dict(page) for page in pages if isinstance(page, dict)]

    raw_text = _safe_text(story.get("raw_text", ""))
    if not raw_text:
        return []

    chunks = [part.strip() for part in raw_text.split("\n") if part.strip()]
    return [
        {
            "pageNumber": index,
            "title": f"Página {index}",
            "text": chunk,
        }
        for index, chunk in enumerate(chunks, start=1)
    ]


def build_audiobook(
    story_variants: Dict[str, Dict[str, Any]],
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    project_id = _safe_text(payload.get("project_id", ""))
    project_title = _safe_text(payload.get("project_title", "Projeto")) or "Projeto"
    requested_provider = _safe_text(payload.get("provider", ""))
    speaker_wav = _safe_text(payload.get("speaker_wav", ""))

    if not speaker_wav and project_id:
        try:
            speaker_wav = get_default_voice_sample_path(project_id)
        except Exception:
            speaker_wav = ""

    output_dir = resolve_storage_path("exports", project_id, "audiobooks")
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs: Dict[str, Any] = {}

    for language, raw_story in story_variants.items():
        story = _safe_dict(raw_story)
        provider = _resolve_default_provider(requested_provider)

        if provider in {"coqui_tts", "xtts"}:
            ensure_audio_provider_running(provider)

        language_safe = _safe_name(language)
        base_name = f"{_safe_name(project_title)}_{language_safe}"

        page_paths: List[Path] = []
        pages = _story_pages(story)

        for index, page in enumerate(pages, start=1):
            page_path = output_dir / f"{base_name}_page_{index:03d}.wav"
            text = _page_text(page)

            try:
                if provider == "coqui_tts":
                    synth = _synthesize_http_provider("coqui_tts", text, page_path, language)
                elif provider == "xtts":
                    synth = _synthesize_http_provider("xtts", text, page_path, language, speaker_wav=speaker_wav)
                else:
                    synth = _synthesize_system_tts(text, page_path, language)
            except Exception:
                synth = _synthesize_system_tts(text, page_path, language)

            page_paths.append(Path(synth["file_path"]))

        final_path = output_dir / f"{base_name}.wav"
        _merge_wavs(page_paths, final_path)

        outputs[language] = {
            "id": str(uuid4()),
            "type": "audiobook",
            "format": "wav",
            "language": language,
            "title": project_title,
            "provider": provider,
            "file_name": final_path.name,
            "file_path": str(final_path),
            "pages_count": len(pages),
            "engine": f"{provider}-runtime",
            "speaker_wav": speaker_wav if provider == "xtts" else "",
        }

    return outputs
