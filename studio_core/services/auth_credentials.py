"""Credential hashing and verification for Studio PIN/password values."""
from __future__ import annotations

import hashlib
import hmac
import secrets

_ALGORITHM = "pbkdf2_sha256"
_ITERATIONS = 310_000
_SALT_BYTES = 16


def hash_pin(pin: str) -> str:
    if not isinstance(pin, str) or not pin:
        raise ValueError("PIN must be a non-empty string")
    salt = secrets.token_bytes(_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, _ITERATIONS)
    return f"${_ALGORITHM}${_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_pin(pin: str, stored_value: str) -> bool:
    if not isinstance(pin, str) or not isinstance(stored_value, str):
        return False
    if stored_value.startswith(f"${_ALGORITHM}$"):
        try:
            algorithm, iterations_raw, salt_hex, digest_hex = stored_value.split("$", 3)
            iterations = int(iterations_raw)
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(digest_hex)
            if algorithm != _ALGORITHM or iterations < 100_000 or iterations > 2_000_000:
                return False
            actual = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, iterations)
            return hmac.compare_digest(actual, expected)
        except (ValueError, TypeError):
            return False
    return hmac.compare_digest(pin.encode("utf-8"), stored_value.encode("utf-8"))


def is_hashed_pin(value: str) -> bool:
    return isinstance(value, str) and value.startswith(f"${_ALGORITHM}$")
