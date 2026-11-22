from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from studio_core.services import series_audio_ledger_service as ledger


class SeriesAudioLedgerPrimitiveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.event = {
            "event_id": "event-1",
            "event_type": "adaptation_script_created",
            "project_id": "project-1",
            "story_revision": "rev-1",
            "language": "pt-PT",
            "server_actor": "system-test",
            "script_revision": "script-1",
            "script_sha256": "a" * 64,
        }

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _patch_storage(self):
        return patch.object(ledger.APP_CONFIG, "storage_root", self.root), patch.object(
            ledger, "resolve_storage_path", side_effect=lambda *parts: self.root.joinpath(*parts).resolve()
        )

    def test_append_and_read_valid_event(self) -> None:
        p1, p2 = self._patch_storage()
        with p1, p2:
            ledger.append_ledger_event(self.event)
            self.assertEqual(ledger.read_ledger_events(), [self.event])

    def test_duplicate_event_id_rejected(self) -> None:
        p1, p2 = self._patch_storage()
        with p1, p2:
            ledger.append_ledger_event(self.event)
            with self.assertRaisesRegex(ledger.SeriesAudioLedgerError, "duplicate"):
                ledger.append_ledger_event({**self.event, "event_type": "script_approved"})

    def test_hash_tampering_detected(self) -> None:
        p1, p2 = self._patch_storage()
        with p1, p2:
            ledger.append_ledger_event(self.event)
            path = self.root / "data/editorial/series_audio_approval_ledger.jsonl"
            data = path.read_text(encoding="utf-8").replace("project-1", "project-2")
            path.write_text(data, encoding="utf-8")
            with self.assertRaisesRegex(ledger.SeriesAudioLedgerError, "integrity_mismatch"):
                ledger.read_ledger_events()

    def test_invalid_event_rejected(self) -> None:
        p1, p2 = self._patch_storage()
        with p1, p2:
            with self.assertRaisesRegex(ledger.SeriesAudioLedgerError, "project_id_required"):
                ledger.append_ledger_event({**self.event, "project_id": ""})

    def test_artifact_checksum_verification(self) -> None:
        p1, p2 = self._patch_storage()
        with p1, p2:
            file_path = self.root / "exports" / "audio" / "series.wav"
            file_path.parent.mkdir(parents=True)
            file_path.write_bytes(b"test audio bytes")
            checksum = hashlib.sha256(file_path.read_bytes()).hexdigest()
            verified = ledger.verify_approved_audio_artifact("exports/audio/series.wav", checksum)
            self.assertEqual(verified, file_path.resolve())
            with self.assertRaisesRegex(ledger.SeriesAudioLedgerError, "checksum_mismatch"):
                ledger.verify_approved_audio_artifact("exports/audio/series.wav", "0" * 64)

    def test_path_traversal_rejected(self) -> None:
        p1, p2 = self._patch_storage()
        with p1, p2:
            outside = self.root.parent / "outside.wav"
            outside.write_bytes(b"outside")
            try:
                with self.assertRaisesRegex(ledger.SeriesAudioLedgerError, "outside_storage_root"):
                    ledger.verify_approved_audio_artifact("../outside.wav", hashlib.sha256(b"outside").hexdigest())
            finally:
                outside.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
