import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from studio_core.services.auth_sessions import SessionManager, SessionStoreError


class Clock:
    def __init__(self):
        self.value = datetime(2026, 11, 25, 12, tzinfo=timezone.utc)

    def __call__(self):
        return self.value


class SessionManagerTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.directory = Path(self.temporary_directory.name)

    def test_created_token_is_opaque_and_only_hash_persisted(self):
        manager = SessionManager(self.directory / "sessions.json")
        issued = manager.create("user-42")
        token = issued["token"]
        self.assertEqual(manager.resolve(token)["user_id"], "user-42")
        saved = (self.directory / "sessions.json").read_text(encoding="utf-8")
        self.assertNotIn(token, saved)
        self.assertEqual(len(json.loads(saved)), 1)

    def test_expiration_invalidates_session(self):
        clock = Clock()
        manager = SessionManager(self.directory / "sessions.json", ttl_seconds=60, clock=clock)
        issued = manager.create("u1")
        clock.value += timedelta(seconds=61)
        self.assertIsNone(manager.resolve(issued["token"]))
        self.assertEqual(manager.purge_expired(), 0)

    def test_revoke_and_revoke_user(self):
        manager = SessionManager(self.directory / "sessions.json")
        one = manager.create("alice")["token"]
        two = manager.create("alice")["token"]
        other = manager.create("bob")["token"]
        self.assertTrue(manager.revoke(one))
        self.assertIsNone(manager.resolve(one))
        self.assertEqual(manager.revoke_user("alice"), 1)
        self.assertIsNone(manager.resolve(two))
        self.assertEqual(manager.resolve(other)["user_id"], "bob")

    def test_invalid_token_and_empty_user(self):
        manager = SessionManager(self.directory / "sessions.json")
        self.assertIsNone(manager.resolve(""))
        self.assertIsNone(manager.resolve("random-invalid-token"))
        with self.assertRaises(ValueError):
            manager.create(" ")

    def test_corrupt_store_fails_closed(self):
        path = self.directory / "sessions.json"
        path.write_text("{bad json", encoding="utf-8")
        manager = SessionManager(path)
        with self.assertRaises(SessionStoreError):
            manager.resolve("any-token")


if __name__ == "__main__":
    unittest.main()
