from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.config import APP_CONFIG, resolve_storage_path

_LEDGER_RELATIVE = "data/editorial/series_audio_approval_ledger.jsonl"
_LOCK = threading.Lock()
_ALLOWED_EVENT_TYPES = {
    "adaptation_script_created",
    "script_approved",
    "series_audio_artifact_created",
    "series_audio_approved",
    "consent_granted",
    "consent_revoked",
    "approval_superseded",
}


class SeriesAudioLedgerError(ValueError):
    """Ledger integrity or validation failure; callers must fail closed."""


def _ledger_path() -> Path:
    root = APP_CONFIG.storage_root.resolve()
    target = resolve_storage_path(_LEDGER_RELATIVE)
    if not target.is_relative_to(root):
        raise SeriesAudioLedgerError("ledger_path_outside_storage_root")
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def _canonical_json(value: Dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _event_hash(event: Dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(event).encode("utf-8")).hexdigest()


def _validate_event(event: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(event, dict):
        raise SeriesAudioLedgerError("ledger_event_must_be_object")
    event_type = str(event.get("event_type", "")).strip()
    if event_type not in _ALLOWED_EVENT_TYPES:
        raise SeriesAudioLedgerError("ledger_event_type_invalid")
    event_id = str(event.get("event_id", "")).strip()
    if not event_id:
        raise SeriesAudioLedgerError("ledger_event_id_required")
    for key in ("project_id", "story_revision", "language"):
        if not str(event.get(key, "")).strip():
            raise SeriesAudioLedgerError(f"ledger_{key}_required")
    if not str(event.get("server_actor", "")).strip():
        raise SeriesAudioLedgerError("ledger_server_actor_required")
    return dict(event)


def read_ledger_events() -> List[Dict[str, Any]]:
    path = _ledger_path()
    if not path.exists():
        return []
    events: List[Dict[str, Any]] = []
    try:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                raise SeriesAudioLedgerError(f"ledger_blank_line_at_{line_number}")
            wrapper = json.loads(line)
            event = wrapper["event"]
            recorded_hash = str(wrapper["event_sha256"])
            if _event_hash(event) != recorded_hash:
                raise SeriesAudioLedgerError(f"ledger_integrity_mismatch_at_{line_number}")
            _validate_event(event)
            events.append(event)
    except SeriesAudioLedgerError:
        raise
    except Exception as exc:
        raise SeriesAudioLedgerError("ledger_corrupt_or_unreadable") from exc
    return events


def append_ledger_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Append an integrity-hashed server-created event; never edit prior entries.

    This primitive is not an approval API. Authentication, actor verification,
    consent validation and human decision UX must be implemented before routes
    can expose it. Client-supplied events must not be passed directly.
    """
    validated = _validate_event(event)
    path = _ledger_path()
    wrapper = {"event": validated, "event_sha256": _event_hash(validated)}
    encoded = (_canonical_json(wrapper) + "\\n").encode("utf-8")
    with _LOCK:
        existing = read_ledger_events()
        if any(str(item.get("event_id")) == str(validated["event_id"]) for item in existing):
            raise SeriesAudioLedgerError("ledger_event_id_duplicate")
        # Atomic replacement avoids partially written JSON lines on interruption.
        # Locking is process-local; multi-worker deployments require a DB-backed
        # transactional ledger or an OS-level lock before this API is exposed.
        prior = path.read_bytes() if path.exists() else b""
        fd, temp_name = tempfile.mkstemp(prefix="ledger-", suffix=".tmp", dir=str(path.parent))
        try:
            with os.fdopen(fd, "wb") as temp_file:
                temp_file.write(prior)
                temp_file.write(encoded)
                temp_file.flush()
                os.fsync(temp_file.fileno())
            os.replace(temp_name, path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
    return validated


def verify_approved_audio_artifact(relative_path: str, expected_sha256: str) -> Path:
    """Verify a server-owned audio file by safe relative path and exact checksum."""
    root = APP_CONFIG.storage_root.resolve()
    candidate = resolve_storage_path(relative_path)
    if not candidate.is_relative_to(root):
        raise SeriesAudioLedgerError("series_audio_path_outside_storage_root")
    if candidate.is_symlink():
        raise SeriesAudioLedgerError("series_audio_symlink_disallowed")
    if not candidate.is_file():
        raise SeriesAudioLedgerError("series_audio_artifact_missing")
    actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
    if not expected_sha256 or actual != expected_sha256:
        raise SeriesAudioLedgerError("series_audio_checksum_mismatch")
    return candidate


def resolve_approved_series_audio(project: Dict[str, Any], language: str) -> str | None:
    """Fail closed until a server-authenticated approval resolver is implemented."""
    # Deliberately not infer approval from project fields or this event log.
    # Resolver integration requires authenticated review decisions, voice consent,
    # script/audio lineage, revocation, and multi-process locking.
    return None
