"""Server-side opaque session primitives for Baribudos Studio.

Tokens are returned only at creation. Persisted state stores token hashes only.
This module is a foundation; API route enforcement and client migration are separate.
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import tempfile
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


class SessionStoreError(RuntimeError):
    """Raised when the session store cannot safely be read or written."""


class SessionManager:
    def __init__(
        self,
        store_path: str | Path,
        *,
        ttl_seconds: int = 8 * 60 * 60,
        clock=None,
    ) -> None:
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

    def _read(self) -> dict[str, Any]:
        if not self.store_path.exists():
            return {}
        try:
            raw = self.store_path.read_text(encoding="utf-8")
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("store root is not an object")
            return data
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            raise SessionStoreError("session store is unreadable; refusing authentication") from exc

    def _write(self, data: dict[str, Any]) -> None:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(
            prefix=f".{self.store_path.name}.", suffix=".tmp", dir=str(self.store_path.parent)
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(data, stream, separators=(",", ":"), sort_keys=True)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.chmod(temporary, 0o600)
            except OSError:
                pass
            os.replace(temporary, self.store_path)
            try:
                os.chmod(self.store_path, 0o600)
            except OSError:
                pass
        except OSError as exc:
            try:
                os.unlink(temporary)
            except OSError:
                pass
            raise SessionStoreError("session store write failed") from exc

    def create(self, user_id: str) -> dict[str, str]:
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("user_id must be a non-empty string")
        token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(token)
        now = self._now()
        expires = now + timedelta(seconds=self.ttl_seconds)
        record = {
            "user_id": user_id,
            "created_at": self._iso(now),
            "expires_at": self._iso(expires),
        }
        with self._lock:
            records = self._read()
            self._purge(records, now)
            records[token_hash] = record
            self._write(records)
        return {"token": token, "expires_at": self._iso(expires)}

    def resolve(self, token: str) -> dict[str, str] | None:
        if not isinstance(token, str) or not token:
            return None
        token_hash = self._hash_token(token)
        now = self._now()
        with self._lock:
            records = self._read()
            record = records.get(token_hash)
            if not isinstance(record, dict):
                return None
            try:
                expires = datetime.fromisoformat(record["expires_at"])
                if expires.tzinfo is None or expires <= now:
                    records.pop(token_hash, None)
                    self._write(records)
                    return None
                user_id = record["user_id"]
                created_at = record["created_at"]
                if not isinstance(user_id, str) or not user_id:
                    return None
                return {"user_id": user_id, "created_at": created_at, "expires_at": record["expires_at"]}
            except (KeyError, TypeError, ValueError):
                records.pop(token_hash, None)
                self._write(records)
                return None

    def revoke(self, token: str) -> bool:
        if not isinstance(token, str) or not token:
            return False
        token_hash = self._hash_token(token)
        with self._lock:
            records = self._read()
            existed = records.pop(token_hash, None) is not None
            if existed:
                self._write(records)
            return existed

    def revoke_user(self, user_id: str) -> int:
        if not isinstance(user_id, str) or not user_id:
            return 0
        with self._lock:
            records = self._read()
            targets = [key for key, value in records.items()
                       if isinstance(value, dict) and value.get("user_id") == user_id]
            for key in targets:
                records.pop(key, None)
            if targets:
                self._write(records)
            return len(targets)

    def purge_expired(self) -> int:
        with self._lock:
            records = self._read()
            before = len(records)
            self._purge(records, self._now())
            removed = before - len(records)
            if removed:
                self._write(records)
            return removed

    @staticmethod
    def _purge(records: dict[str, Any], now: datetime) -> None:
        for key, value in list(records.items()):
            try:
                expiry = datetime.fromisoformat(value["expires_at"])
                if expiry.tzinfo is None or expiry <= now:
                    records.pop(key, None)
            except (KeyError, TypeError, ValueError):
                records.pop(key, None)
