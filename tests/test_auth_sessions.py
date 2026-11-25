import hashlib
import sqlite3
import tempfile
import threading
import unittest
from unittest import mock
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
        self.store = self.directory / "sessions.sqlite"

    def test_created_token_is_opaque_and_only_hash_persisted(self):
        manager = SessionManager(self.store)
        issued = manager.create("user-42")
        token = issued["token"]
        self.assertEqual(manager.resolve(token)["user_id"], "user-42")
        with sqlite3.connect(self.store) as connection:
            row = connection.execute("SELECT token_hash FROM sessions").fetchone()
        self.assertEqual(row[0], hashlib.sha256(token.encode()).hexdigest())
        self.assertNotEqual(row[0], token)
        self.assertEqual(len(row[0]), 64)

    def test_expiration_invalidates_session(self):
        clock = Clock()
        manager = SessionManager(self.store, ttl_seconds=60, clock=clock)
        issued = manager.create("u1")
        clock.value += timedelta(seconds=61)
        self.assertIsNone(manager.resolve(issued["token"]))
        self.assertEqual(manager.purge_expired(), 0)

    def test_revoke_and_revoke_user(self):
        manager = SessionManager(self.store)
        one = manager.create("alice")["token"]
        two = manager.create("alice")["token"]
        other = manager.create("bob")["token"]
        self.assertTrue(manager.revoke(one))
        self.assertIsNone(manager.resolve(one))
        self.assertEqual(manager.revoke_user("alice"), 1)
        self.assertIsNone(manager.resolve(two))
        self.assertEqual(manager.resolve(other)["user_id"], "bob")

    def test_invalid_token_and_empty_user(self):
        manager = SessionManager(self.store)
        self.assertIsNone(manager.resolve(""))
        self.assertIsNone(manager.resolve("random-invalid-token"))
        with self.assertRaises(ValueError):
            manager.create(" ")

    def test_corrupt_store_fails_closed(self):
        self.store.write_bytes(b"not a valid sqlite database")
        manager = SessionManager(self.store)
        with self.assertRaises(SessionStoreError):
            manager.resolve("any-token")

    def test_disappearing_sqlite_sidecar_does_not_fail_permission_hardening(self):
        manager = SessionManager(self.store)
        self.store.touch()
        wal_path = Path(f"{self.store}-wal")
        wal_path.touch()
        real_chmod = __import__("os").chmod

        def chmod_with_sidecar_race(path, mode):
            if Path(path) == wal_path:
                raise FileNotFoundError("sidecar removed by concurrent SQLite connection")
            return real_chmod(path, mode)

        with mock.patch("studio_core.services.auth_sessions.os.chmod", side_effect=chmod_with_sidecar_race):
            manager._secure_file_permissions()

    def test_primary_database_permission_failure_fails_closed(self):
        manager = SessionManager(self.store)
        self.store.touch()
        with mock.patch(
            "studio_core.services.auth_sessions.os.chmod",
            side_effect=PermissionError("permission denied"),
        ):
            with self.assertRaises(SessionStoreError):
                manager._secure_file_permissions()

    def test_concurrent_instances_do_not_lose_created_sessions(self):
        token_results = []
        result_lock = threading.Lock()
        errors = []

        def create_session(index):
            try:
                issued = SessionManager(self.store).create(f"user-{index}")
                with result_lock:
                    token_results.append((issued["token"], f"user-{index}"))
            except Exception as exc:  # collect thread failures for assertion
                with result_lock:
                    errors.append(exc)

        workers = [threading.Thread(target=create_session, args=(index,)) for index in range(16)]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(timeout=15)

        self.assertFalse(any(worker.is_alive() for worker in workers), "thread timeout")
        self.assertEqual(errors, [])
        self.assertEqual(len(token_results), 16)
        verifier = SessionManager(self.store)
        for token, expected_user in token_results:
            self.assertEqual(verifier.resolve(token)["user_id"], expected_user)
        with sqlite3.connect(self.store) as connection:
            count = connection.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        self.assertEqual(count, 16)


if __name__ == "__main__":
    unittest.main()
