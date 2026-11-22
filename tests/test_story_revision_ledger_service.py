from __future__ import annotations

import json

import pytest

from studio_core.services.story_revision_ledger_service import (
    StoryRevisionLedgerError,
    StoryRevisionLedgerIntegrityError,
    append_story_revision,
    get_story_revision,
    verify_story_revision_ledger,
)


def _append(root, story=None):
    return append_story_revision(
        root,
        story=story if story is not None else {"title": "A semente", "pages": [{"text": "Com calma."}]},
        project_id="project-001",
        saga_id="baribudos",
        language="pt-PT",
        prompt_version="story-v1",
        provider="synthetic-test",
        model="fixture",
    )


def test_revision_is_persisted_and_retrievable_as_exact_snapshot(tmp_path):
    story = {"title": "A semente", "pages": [{"text": "Com calma."}]}
    created = _append(tmp_path, story)
    loaded = get_story_revision(tmp_path, created["revision_id"])

    assert loaded["story"] == story
    assert loaded["content_sha256"] == created["content_sha256"]
    assert loaded["event_type"] == "story_revision_created"
    assert created["status"] == "draft_needs_review"


def test_new_revision_does_not_overwrite_previous_revision(tmp_path):
    first = _append(tmp_path, {"title": "Primeira versão"})
    second = _append(tmp_path, {"title": "Segunda versão"})

    assert first["revision_id"] != second["revision_id"]
    assert get_story_revision(tmp_path, first["revision_id"])["story"]["title"] == "Primeira versão"
    assert get_story_revision(tmp_path, second["revision_id"])["story"]["title"] == "Segunda versão"
    assert verify_story_revision_ledger(tmp_path)["record_count"] == 2


def test_missing_metadata_fails_closed(tmp_path):
    with pytest.raises(StoryRevisionLedgerError, match="metadata_incomplete"):
        append_story_revision(
            tmp_path,
            story={"title": "Draft"},
            project_id="project-001",
            saga_id="baribudos",
            language="pt-PT",
            prompt_version="",
            provider="fixture",
            model="fixture",
        )


def test_empty_story_fails_closed(tmp_path):
    with pytest.raises(StoryRevisionLedgerError, match="story_required"):
        _append(tmp_path, {})


def test_tampered_story_content_is_detected(tmp_path):
    created = _append(tmp_path)
    ledger = tmp_path / "story-revisions.jsonl"
    record = json.loads(ledger.read_text(encoding="utf-8"))
    record["story"]["title"] = "Conteúdo adulterado"
    ledger.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")

    with pytest.raises(StoryRevisionLedgerIntegrityError):
        get_story_revision(tmp_path, created["revision_id"])


def test_tampered_or_truncated_ledger_fails_verification(tmp_path):
    _append(tmp_path)
    ledger = tmp_path / "story-revisions.jsonl"
    ledger.write_text("{incompleto\n", encoding="utf-8")

    with pytest.raises(StoryRevisionLedgerIntegrityError):
        verify_story_revision_ledger(tmp_path)


def test_revision_ids_are_not_resolved_from_other_storage_roots(tmp_path):
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_root.mkdir()
    second_root.mkdir()
    created = _append(first_root)

    with pytest.raises(StoryRevisionLedgerError, match="not_found"):
        get_story_revision(second_root, created["revision_id"])


def test_ledger_symlink_is_rejected(tmp_path):
    outside = tmp_path / "outside.jsonl"
    outside.write_text("", encoding="utf-8")
    (tmp_path / "story-revisions.jsonl").symlink_to(outside)

    with pytest.raises(StoryRevisionLedgerIntegrityError, match="symlink_rejected"):
        verify_story_revision_ledger(tmp_path)
