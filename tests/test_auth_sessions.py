import json
from datetime import datetime, timedelta, timezone

import pytest

from studio_core.services.auth_sessions import SessionManager, SessionStoreError


class Clock:
    def __init__(self):
        self.value = datetime(2026, 11, 25, 12, tzinfo=timezone.utc)

    def __call__(self):
        return self.value


def test_created_token_is_opaque_and_only_hash_persisted(tmp_path):
    manager = SessionManager(tmp_path / "sessions.json")
    issued = manager.create("user-42")
    token = issued["token"]
    assert manager.resolve(token)["user_id"] == "user-42"
    saved = (tmp_path / "sessions.json").read_text()
    assert token not in saved
    assert len(json.loads(saved)) == 1


def test_expiration_invalidates_session(tmp_path):
    clock = Clock()
    manager = SessionManager(tmp_path / "sessions.json", ttl_seconds=60, clock=clock)
    issued = manager.create("u1")
    clock.value += timedelta(seconds=61)
    assert manager.resolve(issued["token"]) is None
    assert manager.purge_expired() == 0


def test_revoke_and_revoke_user(tmp_path):
    manager = SessionManager(tmp_path / "sessions.json")
    one = manager.create("alice")["token"]
    two = manager.create("alice")["token"]
    other = manager.create("bob")["token"]
    assert manager.revoke(one)
    assert manager.resolve(one) is None
    assert manager.revoke_user("alice") == 1
    assert manager.resolve(two) is None
    assert manager.resolve(other)["user_id"] == "bob"


def test_invalid_token_and_empty_user(tmp_path):
    manager = SessionManager(tmp_path / "sessions.json")
    assert manager.resolve("") is None
    assert manager.resolve("random-invalid-token") is None
    with pytest.raises(ValueError):
        manager.create(" ")


def test_corrupt_store_fails_closed(tmp_path):
    path = tmp_path / "sessions.json"
    path.write_text("{bad json", encoding="utf-8")
    manager = SessionManager(path)
    with pytest.raises(SessionStoreError):
        manager.resolve("any-token")
