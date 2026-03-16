from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.core.storage import read_json, update_json_item
from studio_core.services.audiobook_service import build_audiobook
from studio_core.services.voice_library_service import get_voice_sample

router = APIRouter(prefix="/audiobooks", tags=["audiobooks"])

PROJECTS_FILE = "data/projects.json"


def _get_project(project_id: str) -> dict | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        if str(project.get("id", "")).strip() == str(project_id).strip():
            return project
    return None


@router.post("/export/{project_id}")
def export_audiobook(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    project = _get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    language = str(payload.get("language", project.get("language", "pt-PT"))).strip() or "pt-PT"
    provider = str(payload.get("provider", "")).strip()
    voice_sample_id = str(payload.get("voice_sample_id", "")).strip()

    language_variants = project.get("language_variants", {}) or {}
    story = language_variants.get(language) or project.get("story") or {}

    if not story:
        raise HTTPException(status_code=400, detail="Story não encontrada.")

    speaker_wav = ""
    voice_sample = None
    if voice_sample_id:
        voice_sample = get_voice_sample(voice_sample_id)
        if not voice_sample:
            raise HTTPException(status_code=404, detail="Voice sample não encontrada.")
        speaker_wav = str(voice_sample.get("file_path", "")).strip()

    outputs = build_audiobook(
        {language: story},
        {
            "project_id": project_id,
            "project_title": project.get("title", "Projeto"),
            "provider": provider,
            "speaker_wav": speaker_wav,
        },
    )

    audiobook_output = outputs.get(language, {})

    update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "outputs": {
                **(current.get("outputs", {}) or {}),
                "audiobook": {
                    **((current.get("outputs", {}) or {}).get("audiobook", {}) or {}),
                    language: audiobook_output,
                },
            },
            "audio_settings": {
                **(current.get("audio_settings", {}) or {}),
                "provider": provider or (current.get("audio_settings", {}) or {}).get("provider", "system_tts"),
                "voice_sample_id": voice_sample_id,
                "speaker_wav": speaker_wav,
            },
        },
    )

    return {
        "ok": True,
        "audiobook": audiobook_output,
        "voice_sample": voice_sample,
    }
