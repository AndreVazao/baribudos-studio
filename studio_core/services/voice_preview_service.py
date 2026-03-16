from __future__ import annotations

import json
import shutil
import subprocess
import urllib.request
import wave
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from studio_core.core.config import resolve_storage_path
from studio_core.core.storage import read_json
from studio_core.services.local_audio_engine_manager_service import ensure_audio_provider_running
from studio_core.services.voice_library_service import get_voice_sample

LOCAL_AUDIO_STATUS_FILE = "data/local_audio_status.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _load_local_audio_status() -> Dict[str, Any]:
    return _safe_dict(read_json(LOCAL_AUDIO_STATUS_FILE, {}))


def _provider_api_url(provider: str) -> str:
    status = _load_local_audio_status()
    providers = _safe_dict(status.get("providers", {}))
    return _safe_text(_safe_dict(providers.get(provider, {})).get("api_url", ""))


def _preview_dir() -> Path:
    path = resolve_storage_path("voice_previews")
    path.mkdir(parents=True, exist_ok=True)
    return path


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


def _espeak_command() -> str:
    if shutil.which("espeak"):
        return "espeak"
    if shutil.which("espeak-ng"):
        return "espeak-ng"
    return ""


def _write_silent_wav(output_path: Path, duration_seconds: float = 2.0, sample_rate: int = 22050) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames = int(sample_rate * max(0.2, duration_seconds))
    with wave.open(str(output_path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00\x00" * frames)


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

    _write_silent_wav(output_path, duration_seconds=max(1.5, len(text.split()) * 0.45 if text else 2.0))
    return {
        "ok": False,
        "provider": "system_tts",
        "file_path": str(output_path),
        "fallback_used": True,
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


def generate_voice_preview(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}

    provider = _safe_text(payload.get("provider", "system_tts")) or "system_tts"
    text = _safe_text(payload.get("text", "")) or "Olá. Este é um teste de voz do Baribudos Studio."
    language = _safe_text(payload.get("language", "pt-PT")) or "pt-PT"
    voice_sample_id = _safe_text(payload.get("voice_sample_id", ""))

    speaker_wav = ""
    voice_sample = None
    if voice_sample_id:
        voice_sample = get_voice_sample(voice_sample_id)
        if not voice_sample:
            raise ValueError("Voice sample não encontrada.")
        speaker_wav = _safe_text(voice_sample.get("file_path", ""))

    output_path = _preview_dir() / f"voice_preview_{uuid4()}.wav"

    try:
        if provider in {"coqui_tts", "xtts"}:
            ensure_audio_provider_running(provider)

        if provider == "coqui_tts":
            result = _synthesize_http_provider("coqui_tts", text, output_path, language)
        elif provider == "xtts":
            result = _synthesize_http_provider("xtts", text, output_path, language, speaker_wav=speaker_wav)
        else:
            result = _synthesize_system_tts(text, output_path, language)

        return {
            "ok": True,
            "preview": {
                "id": str(uuid4()),
                "provider": provider,
                "text": text,
                "language": language,
                "voice_sample_id": voice_sample_id,
                "speaker_wav": speaker_wav,
                "file_path": result["file_path"],
                "file_name": Path(result["file_path"]).name,
            },
            "voice_sample": voice_sample,
        }

    except Exception:
        fallback = _synthesize_system_tts(text, output_path, language)
        return {
            "ok": True,
            "preview": {
                "id": str(uuid4()),
                "provider": provider,
                "fallback_provider": "system_tts",
                "text": text,
                "language": language,
                "voice_sample_id": voice_sample_id,
                "speaker_wav": speaker_wav,
                "file_path": fallback["file_path"],
                "file_name": Path(fallback["file_path"]).name,
                "fallback_used": True,
            },
            "voice_sample": voice_sample,
}
