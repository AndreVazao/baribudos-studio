from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from studio_core.services import video_service


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

    def test_project_embedded_approval_claim_is_not_trusted_without_ledger(self) -> None:
        project = {
            "outputs": {
                "series_adaptations": {
                    "pt-PT": {
                        "status": "approved",
                        "script": {"status": "approved", "decision": {"decision": "approved"}},
                        "audio": {
                            "status": "approved",
                            "voice_consent": {"status": "granted"},
                        },
                    }
                }
            }
        }
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
