from __future__ import annotations

import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

from studio_core.services import audiobook_service as audiobook


class AudiobookFallbackTests(unittest.TestCase):
    def test_system_tts_fails_instead_of_writing_silent_audio_when_engine_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "segment.wav"
            with patch.object(audiobook, "_espeak_command", return_value=""):
                with self.assertRaisesRegex(RuntimeError, "Nenhum motor TTS local"):
                    audiobook._synthesize_system_tts(
                        "Uma história para testar.",
                        output_path,
                        "pt-PT",
                    )

            self.assertFalse(output_path.exists())

    def test_audiobook_does_not_complete_when_system_tts_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(audiobook, "resolve_storage_path", side_effect=lambda *parts: Path(temp_dir).joinpath(*parts)):
                with patch.object(audiobook, "_resolve_default_provider", return_value="system_tts"):
                    with patch.object(audiobook, "_espeak_command", return_value=""):
                        with self.assertRaisesRegex(RuntimeError, "Falha no TTS do segmento"):
                            audiobook.build_audiobook(
                                {
                                    "pt-PT": {
                                        "pages": [{"pageNumber": 1, "text": "Texto de teste."}]
                                    }
                                },
                                {
                                    "project_id": "project-1",
                                    "project_title": "Teste",
                                },
                            )

            expected_output = Path(temp_dir) / "exports" / "project-1" / "audiobooks" / "teste_pt_pt.wav"
            self.assertFalse(expected_output.exists())

    def test_successful_fallback_reports_the_actual_provider(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fallback_path = Path(temp_dir) / "fallback.wav"
            with wave.open(str(fallback_path), "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(22050)
                wav_file.writeframes(b"\x01\x00" * 2205)

            with patch.object(audiobook, "resolve_storage_path", side_effect=lambda *parts: Path(temp_dir).joinpath(*parts)):
                with patch.object(audiobook, "_resolve_default_provider", return_value="xtts"):
                    with patch.object(audiobook, "ensure_audio_provider_running"):
                        with patch.object(audiobook, "_synthesize_http_provider", side_effect=RuntimeError("XTTS indisponível")):
                            with patch.object(
                                audiobook,
                                "_synthesize_system_tts",
                                return_value={
                                    "ok": True,
                                    "provider": "system_tts",
                                    "file_path": str(fallback_path),
                                },
                            ):
                                result = audiobook.build_audiobook(
                                    {
                                        "pt-PT": {
                                            "pages": [{"pageNumber": 1, "text": "Texto de teste."}]
                                        }
                                    },
                                    {
                                        "project_id": "project-2",
                                        "project_title": "Fallback",
                                        "provider": "xtts",
                                    },
                                )

            output = result["pt-PT"]
            self.assertEqual(output["provider"], "system_tts")
            self.assertEqual(output["requested_provider"], "xtts")
            self.assertTrue(output["fallback_used"])
            self.assertEqual(output["fallback_segments"], [1])
            self.assertTrue(Path(output["file_path"]).exists())

    @staticmethod
    def _write_wav(
        path: Path,
        *,
        frames: bytes,
        sample_width: int = 2,
        channels: int = 1,
        sample_rate: int = 22050,
    ) -> None:
        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(frames)

    def test_merge_rejects_silent_segment_before_creating_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            silent_path = Path(temp_dir) / "silent.wav"
            output_path = Path(temp_dir) / "combined.wav"
            self._write_wav(silent_path, frames=b"\x00\x00" * 2205)

            with self.assertRaisesRegex(RuntimeError, "silencioso"):
                audiobook._merge_wavs([silent_path], output_path)

            self.assertFalse(output_path.exists())

    def test_merge_rejects_incompatible_wav_formats(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            first_path = Path(temp_dir) / "first.wav"
            second_path = Path(temp_dir) / "second.wav"
            output_path = Path(temp_dir) / "combined.wav"
            signal = b"\x01\x00" * 2205
            self._write_wav(first_path, frames=signal, sample_rate=22050)
            self._write_wav(second_path, frames=signal, sample_rate=44100)

            with self.assertRaisesRegex(RuntimeError, "formatos WAV incompatíveis"):
                audiobook._merge_wavs([first_path, second_path], output_path)

            self.assertFalse(output_path.exists())

    def test_merge_rejects_empty_segment_list(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "combined.wav"

            with self.assertRaisesRegex(ValueError, "Não existem segmentos"):
                audiobook._merge_wavs([], output_path)

            self.assertFalse(output_path.exists())

    def test_build_audiobook_rejects_provider_reported_silent_audio(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            def synthesize_silence(_text: str, output_path: Path, _language: str) -> dict:
                self._write_wav(output_path, frames=b"\x00\x00" * 2205)
                return {
                    "ok": True,
                    "provider": "system_tts",
                    "file_path": str(output_path),
                }

            with patch.object(audiobook, "resolve_storage_path", side_effect=lambda *parts: Path(temp_dir).joinpath(*parts)):
                with patch.object(audiobook, "_resolve_default_provider", return_value="system_tts"):
                    with patch.object(audiobook, "_synthesize_system_tts", side_effect=synthesize_silence):
                        with self.assertRaisesRegex(RuntimeError, "silencioso"):
                            audiobook.build_audiobook(
                                {
                                    "pt-PT": {
                                        "pages": [{"pageNumber": 1, "text": "Texto de teste."}]
                                    }
                                },
                                {
                                    "project_id": "project-silent",
                                    "project_title": "Silêncio",
                                },
                            )

            expected_output = Path(temp_dir) / "exports" / "project-silent" / "audiobooks" / "silencio_pt_pt.wav"
            self.assertFalse(expected_output.exists())

    def test_empty_story_is_rejected_instead_of_creating_silence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(audiobook, "resolve_storage_path", side_effect=lambda *parts: Path(temp_dir).joinpath(*parts)):
                with patch.object(audiobook, "_resolve_default_provider", return_value="system_tts"):
                    with self.assertRaisesRegex(ValueError, "não contém texto"):
                        audiobook.build_audiobook(
                            {"pt-PT": {"pages": []}},
                            {"project_id": "project-3", "project_title": "Vazio"},
                        )


if __name__ == "__main__":
    unittest.main()
