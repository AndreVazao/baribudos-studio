"""Append-only, checksum-bound story revision ledger.

This module is deliberately storage-agnostic: callers must supply the protected
Studio data directory. It never reads approval flags from project JSON and it
never creates an approval. A revision is immutable evidence of generated or
edited content, not permission to produce or publish it.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator
from uuid import uuid4


LEDGER_FILENAME = "story-revisions.jsonl"
LOCK_FILENAME = "story-revisions.lock"
LEDGER_VERSION = 1


class StoryRevisionLedgerError(RuntimeError):
    """Base error for revision-ledger failures."""


class StoryRevisionLedgerIntegrityError(StoryRevisionLedgerError):
    """Raised when persisted ledger data is malformed or tampered with."""


class StoryRevisionLockError(StoryRevisionLedgerError):
    """Raised when the append lock cannot be acquired safely."""


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_root(storage_root: str | os.PathLike[str]) -> Path:
    root = Path(storage_root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise StoryRevisionLedgerError("story_revision_storage_root_missing")
    return root


def _contained_path(root: Path, filename: str) -> Path:
    candidate = root / filename
    # Resolve the parent and reject a pre-existing symlink at the target.
    if candidate.is_symlink():
        raise StoryRevisionLedgerIntegrityError("story_revision_ledger_symlink_rejected")
    resolved_parent = candidate.parent.resolve()
    if resolved_parent != root:
        raise StoryRevisionLedgerIntegrityError("story_revision_storage_path_escape")
    return candidate


@contextmanager
def _append_lock(root: Path, timeout_seconds: float = 5.0) -> Iterator[None]:
    lock_path = _contained_path(root, LOCK_FILENAME)
    deadline = time.monotonic() + max(0.1, timeout_seconds)
    descriptor: int | None = None
    while descriptor is None:
        try:
            descriptor = os.open(
                lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600
            )
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise StoryRevisionLockError("story_revision_lock_timeout")
            time.sleep(0.05)
            continue
        try:
            os.write(descriptor, f"{os.getpid()}\\n".encode("ascii"))
            os.fsync(descriptor)
        except OSError as exc:
            os.close(descriptor)
            descriptor = None
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass
            raise StoryRevisionLockError(
                "story_revision_lock_initialization_failed"
            ) from exc
    try:
        yield
    finally:
        try:
            if descriptor is not None:
                os.close(descriptor)
        finally:
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass


def _read_records(root: Path) -> list[Dict[str, Any]]:
    ledger_path = _contained_path(root, LEDGER_FILENAME)
    if not ledger_path.exists():
        return []
    records: list[Dict[str, Any]] = []
    previous_hash = "0" * 64
    seen_revision_ids: set[str] = set()
    try:
        with ledger_path.open("r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                if not raw_line.strip():
                    raise StoryRevisionLedgerIntegrityError(
                        f"story_revision_blank_ledger_line:{line_number}"
                    )
                try:
                    record = json.loads(raw_line)
                except json.JSONDecodeError as exc:
                    raise StoryRevisionLedgerIntegrityError(
                        f"story_revision_invalid_json:{line_number}"
                    ) from exc
                if not isinstance(record, dict):
                    raise StoryRevisionLedgerIntegrityError(
                        f"story_revision_invalid_record:{line_number}"
                    )
                supplied_hash = record.pop("record_hash", None)
                revision_id = record.get("revision_id")
                story = record.get("story")
                if record.get("ledger_version") != LEDGER_VERSION or record.get("event_type") != "story_revision_created":
                    raise StoryRevisionLedgerIntegrityError(
                        f"story_revision_unsupported_record:{line_number}"
                    )
                if not isinstance(revision_id, str) or not revision_id or revision_id in seen_revision_ids:
                    raise StoryRevisionLedgerIntegrityError(
                        f"story_revision_duplicate_or_missing_id:{line_number}"
                    )
                if not isinstance(story, dict) or _sha256(_canonical_json(story)) != record.get("content_sha256"):
                    raise StoryRevisionLedgerIntegrityError(
                        f"story_revision_content_checksum_mismatch:{line_number}"
                    )
                if record.get("previous_record_hash") != previous_hash:
                    raise StoryRevisionLedgerIntegrityError(
                        f"story_revision_chain_mismatch:{line_number}"
                    )
                expected_hash = _sha256(_canonical_json(record))
                if supplied_hash != expected_hash:
                    raise StoryRevisionLedgerIntegrityError(
                        f"story_revision_checksum_mismatch:{line_number}"
                    )
                record["record_hash"] = supplied_hash
                records.append(record)
                seen_revision_ids.add(revision_id)
                previous_hash = supplied_hash
    except OSError as exc:
        raise StoryRevisionLedgerError("story_revision_ledger_read_failed") from exc
    return records


def verify_story_revision_ledger(
    storage_root: str | os.PathLike[str],
) -> Dict[str, Any]:
    """Verify record, content and chain hashes without changing persisted data."""
    root = _safe_root(storage_root)
    records = _read_records(root)
    return {
        "ok": True,
        "record_count": len(records),
        "latest_record_hash": records[-1]["record_hash"] if records else "0" * 64,
        "revision_ids": [item["revision_id"] for item in records],
    }


def append_story_revision(
    storage_root: str | os.PathLike[str],
    *,
    story: Dict[str, Any],
    project_id: str,
    saga_id: str,
    language: str,
    prompt_version: str,
    provider: str,
    model: str,
    parent_revision_id: str | None = None,
    source_revision_id: str | None = None,
    actor_id: str = "system:generation",
) -> Dict[str, Any]:
    """Persist a new immutable story snapshot and return its checksum metadata.

    Approval state is intentionally not accepted as an argument. Any caller
    must separately implement authenticated, checksum-bound human approval.
    """
    if not isinstance(story, dict) or not story:
        raise StoryRevisionLedgerError("story_revision_story_required")
    required = {
        "project_id": project_id,
        "saga_id": saga_id,
        "language": language,
        "prompt_version": prompt_version,
        "provider": provider,
        "model": model,
        "actor_id": actor_id,
    }
    if any(not isinstance(value, str) or not value.strip() for value in required.values()):
        raise StoryRevisionLedgerError("story_revision_metadata_incomplete")
    snapshot = json.loads(_canonical_json(story).decode("utf-8"))
    content_hash = _sha256(_canonical_json(snapshot))
    root = _safe_root(storage_root)
    ledger_path = _contained_path(root, LEDGER_FILENAME)

    with _append_lock(root):
        records = _read_records(root)
        previous_hash = records[-1]["record_hash"] if records else "0" * 64
        revision_id = str(uuid4())
        body: Dict[str, Any] = {
            "ledger_version": LEDGER_VERSION,
            "event_type": "story_revision_created",
            "revision_id": revision_id,
            "created_at": _utc_now(),
            "project_id": project_id.strip(),
            "saga_id": saga_id.strip(),
            "language": language.strip(),
            "prompt_version": prompt_version.strip(),
            "provider": provider.strip(),
            "model": model.strip(),
            "actor_id": actor_id.strip(),
            "parent_revision_id": parent_revision_id,
            "source_revision_id": source_revision_id,
            "content_sha256": content_hash,
            "story": snapshot,
            "previous_record_hash": previous_hash,
        }
        record_hash = _sha256(_canonical_json(body))
        record = {**body, "record_hash": record_hash}
        descriptor: int | None = None
        try:
            flags = os.O_CREAT | os.O_APPEND | os.O_WRONLY
            flags |= getattr(os, "O_NOFOLLOW", 0)
            descriptor = os.open(ledger_path, flags, 0o600)
            with os.fdopen(descriptor, "ab") as handle:
                descriptor = None
                handle.write(_canonical_json(record) + b"\\n")
                handle.flush()
                os.fsync(handle.fileno())
        except OSError as exc:
            raise StoryRevisionLedgerError("story_revision_ledger_write_failed") from exc
        finally:
            if descriptor is not None:
                os.close(descriptor)

    return {
        "revision_id": revision_id,
        "content_sha256": content_hash,
        "record_hash": record_hash,
        "created_at": body["created_at"],
        "status": "draft_needs_review",
    }


def get_story_revision(
    storage_root: str | os.PathLike[str], revision_id: str
) -> Dict[str, Any]:
    """Return a verified revision snapshot; never return unverified content."""
    if not isinstance(revision_id, str) or not revision_id.strip():
        raise StoryRevisionLedgerError("story_revision_id_required")
    root = _safe_root(storage_root)
    for record in _read_records(root):
        if record["revision_id"] == revision_id:
            story = record.get("story")
            if not isinstance(story, dict) or _sha256(_canonical_json(story)) != record.get("content_sha256"):
                raise StoryRevisionLedgerIntegrityError("story_revision_content_checksum_mismatch")
            return {**record, "story": json.loads(_canonical_json(story).decode("utf-8"))}
    raise StoryRevisionLedgerError("story_revision_not_found")
