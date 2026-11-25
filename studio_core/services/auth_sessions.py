"""Server-side opaque sessions stored in a local SQLite database.

Tokens are returned only at creation. Persisted state stores token hashes only.
SQLite transactions provide cross-process write serialization. API integration and
client migration are intentionally separate follow-up work.
"""
from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


class SessionStoreError(RuntimeError):
    """Raised when the session store cannot safely be accessed."""


class SessionManager:
    def __init__(self, store_path: str | Path, *, ttl_seconds: int = 8 * 60 * 60, clock=None):
        if ttl_seconds < 60:
            raise ValueError("ttl_seconds must be at least 60")
        self.store_path = Path(store_path)
        self.ttl_seconds = ttl_seconds
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._lock = threading.RLock()

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None:
            raise ValueError("clock must return timezone-aware datetime")
        return value.astimezone(timezone.utc)

    @staticmethod
    def _iso(value: datetime) -> str:
        return value.astimezone(timezone.utc).isoformat()

    def _secure_file_permissions(self) -> None:
        # SQLite sidecars can be created or removed by another process between
        # exists() and chmod(). Their disappearance is benign; failure to secure
        # the primary database is not.
        sidecars = (Path(f"{self.store_path}-wal"), Path(f"{self.store_path}-shm"))
        for candidate in (self.store_path, *sidecars):
            try:
                if candidate.exists():
                    os.chmod(candidate, 0o600)
            except FileNotFoundError:
                if candidate == self.store_path:
                    raise SessionStoreError("session database disappeared during permission hardening")
                continue
            except OSError as exc:
                raise SessionStoreError("session store permissions could not be secured") from exc

    @staticmethod
    def _enable_wal_with_retry(connection: sqlite3.Connection) -> None:
        # Multiple worker processes may open a brand-new database at once.
        # journal_mode changes can report SQLITE_BUSY even with SQLite's
        # connection timeout, so retry this idempotent initialization step.
        deadline = time.monotonic() + 8.0
        delay = 0.01
        while True:
            try:
                connection.execute("PRAGMA journal_mode=WAL")
                return
            except sqlite3.OperationalError as exc:
                message = str(exc).lower()
                if not any(marker in message for marker in ("locked", "busy")):
                    raise
                if time.monotonic() >= deadline:
                    raise
                time.sleep(delay)
                delay = min(delay * 2, 0.25)

    def _connect(self) -> sqlite3.Connection:
        connection = None
        try:
            self.store_path.parent.mkdir(parents=True, exist_ok=True)
            connection = sqlite3.connect(self.store_path, timeout=10, isolation_level=None)
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute(
                """CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                )"""
            )
            connection.execute("CREATE INDEX IF NOT EXISTS sessions_user_id_idx ON sessions(user_id)")
            self._secure_file_permissions()
            return connection
        except (OSError, sqlite3.Error, SessionStoreError) as exc:
            if connection is not None:
                connection.close()
            raise SessionStoreError("session store unavailable; refusing authentication") from exc

    def create(self, user_id: str) -> dict[str, str]:
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("user_id must be a non-empty string")
        token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(token)
        now = self._now()
        expires = now + timedelta(seconds=self.ttl_seconds)
        with self._lock:
            connection = self._connect()
            try:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute("DELETE FROM sessions WHERE expires_at <= ?", (self._iso(now),))
                connection.execute(
                    "INSERT INTO sessions(token_hash,user_id,created_at,expires_at) VALUES(?,?,?,?)",
                    (token_hash, user_id, self._iso(now), self._iso(expires)),
                )
                connection.commit()
                self._secure_file_permissions()
            except (sqlite3.Error, SessionStoreError) as exc:
                connection.rollback()
                raise SessionStoreError("session creation failed") from exc
            finally:
                connection.close()
        return {"token": token, "expires_at": self._iso(expires)}

    def resolve(self, token: str) -> dict[str, str] | None:
        if not isinstance(token, str) or not token:
            return None
        now = self._now()
        with self._lock:
            connection = self._connect()
            try:
                row = connection.execute(
                    "SELECT user_id,created_at,expires_at FROM sessions WHERE token_hash=?",
                    (self._hash_token(token),),
                ).fetchone()
                if row is None:
                    return None
                user_id, created_at, expires_at = row
                try:
                    expiry = datetime.fromisoformat(expires_at)
                except (TypeError, ValueError) as exc:
                    raise SessionStoreError("session record malformed") from exc
                if expiry.tzinfo is None or expiry <= now:
                    connection.execute("DELETE FROM sessions WHERE token_hash=?", (self._hash_token(token),))
                    self._secure_file_permissions()
                    return None
                if not isinstance(user_id, str) or not user_id.strip():
                    return None
                return {"user_id": user_id, "created_at": created_at, "expires_at": expires_at}
            except sqlite3.Error as exc:
                raise SessionStoreError("session lookup failed") from exc
            finally:
                connection.close()

    def revoke(self, token: str) -> bool:
        if not isinstance(token, str) or not token:
            return False
        with self._lock:
            connection = self._connect()
            try:
                cursor = connection.execute("DELETE FROM sessions WHERE token_hash=?", (self._hash_token(token),))
                self._secure_file_permissions()
                return cursor.rowcount > 0
            except sqlite3.Error as exc:
                raise SessionStoreError("session revocation failed") from exc
            finally:
                connection.close()

    def revoke_user(self, user_id: str) -> int:
        if not isinstance(user_id, str) or not user_id:
            return 0
        with self._lock:
            connection = self._connect()
            try:
                cursor = connection.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
                self._secure_file_permissions()
                return cursor.rowcount
            except sqlite3.Error as exc:
                raise SessionStoreError("user session revocation failed") from exc
            finally:
                connection.close()

    def purge_expired(self) -> int:
        now = self._iso(self._now())
        with self._lock:
            connection = self._connect()
            try:
                cursor = connection.execute("DELETE FROM sessions WHERE expires_at <= ?", (now,))
                self._secure_file_permissions()
                return cursor.rowcount
            except sqlite3.Error as exc:
                raise SessionStoreError("expired-session cleanup failed") from exc
            finally:
                connection.close()
