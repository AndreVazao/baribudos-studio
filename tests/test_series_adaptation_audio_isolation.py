from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from studio_core.services import video_service


def _approved_adaptation(audio_path: Path, script_text: str = "Guião de teste, apenas fixture.") -> dict:
    script_sha256 = hashlib.sha256(script_text.encode("utf-8")).hexdigest()
    audio_sha256 = hashlib.sha256(audio_path.read_bytes()).hexdigest()
    return {
        "status": "approved",
        "script": {
            "status": "approved",
            "revision": "rev-1",
            "text": script_text,
            "sha256": script_sha256,
            "decision": {
                "id": "decision-script-1",
                "decision": "approved",
                "decided_by": "editor-fixture",
                "decided_at": "2026-11-18T12:00:00Z",
                "revision": "rev-1",
                "sha256": script_sha256,
            },
        },
        "audio": {
            "status": "approved",
            "file_path": str(audio_path),
            "sha256": audio_sha256,
            "voice_id": "voice-fixture",
            "voice_consent": {
                "id": "consent-fixture",
                "status": "granted",
                "voice_id": "voice-fixture",
                "scope": "series_narration",
                "granted_by": "rights-holder-fixture",
                "granted_at": "2026-11-18T12:00:00Z",
            },
            "decision": {
                "id": "decision-audio-1",
                "decision": "approved",
                "decided_by": "editor-fixture",
                "decided_at": "2026-11-18T12:01:00Z",
                "sha256": audio_sha256,
            },
        },
    }


class SeriesAdaptationAudioIsolationTests(unittest.TestCase):
    def test_audiobook_alone_never_resolves_as_series_audio(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audiobook = Path(temporary) / "audiobook.wav"
            audiobook.write_bytes(b"book narration")
            project = {
                "outputs": {
                    "audiobook": {"pt-PT": {"file_path": str(audiobook)}}
                }
            }
            self.assertIsNone(video_service.resolve_approved_series_audio(project, "pt-PT"))

    def test_series_audio_requires_human_decisions_consent_and_matching_checksums(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audio = Path(temporary) / "series.wav"
            audio.write_bytes(b"separate series narration fixture")
            adaptation = _approved_adaptation(audio)
            project = {"outputs": {"series_adaptations": {"pt-PT": adaptation}}}

            self.assertEqual(
                video_service.resolve_approved_series_audio(project, "pt-PT"),
                str(audio),
            )

            without_consent = {
                **adaptation,
                "audio": {
                    **adaptation["audio"],
                    "voice_consent": {"status": "missing"},
                },
            }
            project["outputs"]["series_adaptations"]["pt-PT"] = without_consent
            self.assertIsNone(video_service.resolve_approved_series_audio(project, "pt-PT"))

    def test_changed_series_audio_fails_checksum_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audio = Path(temporary) / "series.wav"
            audio.write_bytes(b"original series audio")
            adaptation = _approved_adaptation(audio)
            audio.write_bytes(b"changed after approval")
            project = {"outputs": {"series_adaptations": {"pt-PT": adaptation}}}

            self.assertIsNone(video_service.resolve_approved_series_audio(project, "pt-PT"))

    def test_legacy_audio_path_is_ignored_and_output_is_animatic_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            frame = root / "frame.png"
            frame.write_bytes(b"frame fixture")
            storage = root / "storage"

            def fake_silent_renderer(_frames, output_path, _temp_dir, total_duration=6):
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(b"synthetic animatic")

            with (
                patch.object(video_service, "resolve_storage_path", side_effect=lambda *parts: storage.joinpath(*parts)),
                patch.object(video_service, "_has_ffmpeg", return_value=True),
                patch.object(video_service, "_build_silent_slideshow", side_effect=fake_silent_renderer) as silent_renderer,
                patch.object(video_service, "_build_video_with_audio_slideshow") as audio_renderer,
            ):
                result = video_service.build_series_episode(
                    {"title": "Teste", "language": "pt-PT"},
                    {
                        "project_id": "project-1",
                        "project_title": "Teste",
                        "language": "pt-PT",
                        "audio_path": str(root / "legacy-audiobook.wav"),
                        "sequence_frames": [{"index": 1, "image_path": str(frame)}],
                    },
                )

            self.assertTrue(silent_renderer.called)
            audio_renderer.assert_not_called()
            self.assertTrue(Path(result["file_path"]).is_file())
            self.assertEqual(result["status"], "animatic_only")
            self.assertEqual(result["artifact_kind"], "animatic")
            self.assertEqual(result["production_status"], "animatic_only")
            self.assertFalse(result["finalizable"])
            self.assertEqual(result["audio_source"], "none")


if __name__ == "__main__":
    unittest.main()
