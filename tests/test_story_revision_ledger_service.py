from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

import studio_core.services.story_revision_ledger_service as ledger_service

from studio_core.services.story_revision_ledger_service import (
    StoryRevisionLedgerError,
    StoryRevisionLedgerIntegrityError,
    StoryRevisionLockError,
    append_story_revision,
    get_story_revision,
    verify_story_revision_ledger,
)


class StoryRevisionLedgerServiceTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="baribudos-story-ledger-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def append(self, story=None):
        return append_story_revision(
            self.root,
            story=story if story is not None else {
                "title": "A semente",
                "pages": [{"text": "Com calma."}],
            },
            project_id="project-001",
            saga_id="baribudos",
            language="pt-PT",
            prompt_version="story-v1",
            provider="synthetic-test",
            model="fixture",
        )

    def test_revision_is_persisted_and_retrievable_as_exact_snapshot(self):
        story = {"title": "A semente", "pages": [{"text": "Com calma."}]}
        created = self.append(story)
        loaded = get_story_revision(self.root, created["revision_id"])

        self.assertEqual(loaded["story"], story)
        self.assertEqual(loaded["content_sha256"], created["content_sha256"])
        self.assertEqual(loaded["event_type"], "story_revision_created")
        self.assertEqual(created["status"], "draft_needs_review")

    def test_new_revision_does_not_overwrite_previous_revision(self):
        first = self.append({"title": "Primeira versão"})
        second = self.append({"title": "Segunda versão"})

        self.assertNotEqual(first["revision_id"], second["revision_id"])
        self.assertEqual(
            get_story_revision(self.root, first["revision_id"])["story"]["title"],
            "Primeira versão",
        )
        self.assertEqual(
            get_story_revision(self.root, second["revision_id"])["story"]["title"],
            "Segunda versão",
        )
        self.assertEqual(verify_story_revision_ledger(self.root)["record_count"], 2)

    def test_missing_metadata_fails_closed(self):
        with self.assertRaisesRegex(StoryRevisionLedgerError, "metadata_incomplete"):
            append_story_revision(
                self.root,
                story={"title": "Draft"},
                project_id="project-001",
                saga_id="baribudos",
                language="pt-PT",
                prompt_version="",
                provider="fixture",
                model="fixture",
            )

    def test_empty_story_fails_closed(self):
        with self.assertRaisesRegex(StoryRevisionLedgerError, "story_required"):
            self.append({})

    def test_tampered_story_content_is_detected(self):
        created = self.append()
        ledger = self.root / "story-revisions.jsonl"
        record = json.loads(ledger.read_text(encoding="utf-8"))
        record["story"]["title"] = "Conteúdo adulterado"
        ledger.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")

        with self.assertRaises(StoryRevisionLedgerIntegrityError):
            get_story_revision(self.root, created["revision_id"])

    def test_tampered_or_truncated_ledger_fails_verification(self):
        self.append()
        ledger = self.root / "story-revisions.jsonl"
        ledger.write_text("{incompleto\n", encoding="utf-8")

        with self.assertRaises(StoryRevisionLedgerIntegrityError):
            verify_story_revision_ledger(self.root)

    def test_revision_ids_are_not_resolved_from_other_storage_roots(self):
        created = self.append()
        other_root = self.root / "other"
        other_root.mkdir()

        with self.assertRaisesRegex(StoryRevisionLedgerError, "not_found"):
            get_story_revision(other_root, created["revision_id"])

    def test_lock_initialization_failure_cleans_up_lock_file(self):
        with patch(
            "studio_core.services.story_revision_ledger_service.os.fsync",
            side_effect=OSError("simulated fsync failure"),
        ):
            with self.assertRaisesRegex(
                StoryRevisionLockError, "lock_initialization_failed"
            ):
                self.append()

        self.assertFalse((self.root / "story-revisions.lock").exists())
        self.assertEqual(verify_story_revision_ledger(self.root)["record_count"], 0)
        self.append()
        self.assertEqual(verify_story_revision_ledger(self.root)["record_count"], 1)

    @unittest.skipUnless(
        hasattr(__import__("os"), "O_NOFOLLOW"),
        "O_NOFOLLOW is not available on this platform",
    )
    def test_append_rejects_ledger_symlink_without_touching_target(self):
        import os

        outside = self.root.parent / (self.root.name + "-append-target.jsonl")
        outside.write_text("", encoding="utf-8")
        self.addCleanup(outside.unlink, missing_ok=True)
        (self.root / "story-revisions.jsonl").symlink_to(outside)

        with self.assertRaises(StoryRevisionLedgerIntegrityError):
            self.append()

        self.assertEqual(outside.read_text(encoding="utf-8"), "")

    @unittest.skipUnless(
        hasattr(__import__("os"), "O_NOFOLLOW"),
        "O_NOFOLLOW is not available on this platform",
    )
    def test_append_uses_no_follow_when_symlink_appears_after_path_check(self):
        outside = self.root.parent / (self.root.name + "-race-target.jsonl")
        outside.write_text("protected\\n", encoding="utf-8")
        self.addCleanup(outside.unlink, missing_ok=True)
        original_contained_path = ledger_service._contained_path

        def create_symlink_after_path_check(root, filename):
            candidate = original_contained_path(root, filename)
            if filename == ledger_service.LEDGER_FILENAME:
                candidate.symlink_to(outside)
            return candidate

        with patch.object(
            ledger_service,
            "_contained_path",
            side_effect=create_symlink_after_path_check,
        ):
            with self.assertRaisesRegex(
                StoryRevisionLedgerError, "ledger_write_failed"
            ):
                self.append()

        self.assertEqual(outside.read_text(encoding="utf-8"), "protected\\n")

    def test_ledger_symlink_is_rejected(self):
        outside = self.root.parent / (self.root.name + "-outside.jsonl")
        outside.write_text("", encoding="utf-8")
        self.addCleanup(outside.unlink, missing_ok=True)
        (self.root / "story-revisions.jsonl").symlink_to(outside)

        with self.assertRaisesRegex(
            StoryRevisionLedgerIntegrityError, "symlink_rejected"
        ):
            verify_story_revision_ledger(self.root)

    def test_full_verification_detects_content_hash_mismatch(self):
        self.append()
        ledger = self.root / "story-revisions.jsonl"
        record = json.loads(ledger.read_text(encoding="utf-8"))
        record["story"]["title"] = "Conteúdo adulterado"
        body = {key: value for key, value in record.items() if key != "record_hash"}
        canonical = json.dumps(
            body,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        record["record_hash"] = hashlib.sha256(canonical).hexdigest()
        ledger.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")

        with self.assertRaisesRegex(
            StoryRevisionLedgerIntegrityError, "content_checksum_mismatch"
        ):
            verify_story_revision_ledger(self.root)

    def test_verification_rejects_duplicate_revision_ids(self):
        self.append()
        ledger = self.root / "story-revisions.jsonl"
        record = json.loads(ledger.read_text(encoding="utf-8"))
        duplicate_lines = (
            json.dumps(record, ensure_ascii=False)
            + "\n"
            + json.dumps(record, ensure_ascii=False)
            + "\n"
        )
        ledger.write_text(duplicate_lines, encoding="utf-8")

        with self.assertRaisesRegex(
            StoryRevisionLedgerIntegrityError, "duplicate_or_missing_id"
        ):
            verify_story_revision_ledger(self.root)


if __name__ == "__main__":
    unittest.main()
