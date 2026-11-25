from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi import HTTPException
from starlette.requests import Request

from studio_core.api.routes import users


def make_request(auth_header: str | None = None) -> Request:
    headers = []
    if auth_header is not None:
        headers.append((b"authorization", auth_header.encode("latin-1")))
    return Request({"type": "http", "method": "GET", "path": "/api/users/me",
                   "headers": headers, "query_string": b"", "server": ("test", 80),
                   "client": ("test", 1), "scheme": "http"})


class CurrentUserSessionTests(unittest.TestCase):
    def test_requires_bearer_token(self):
        with self.assertRaises(HTTPException) as raised:
            users.get_current_user(make_request())
        self.assertEqual(raised.exception.status_code, 401)

    def test_returns_safe_dto_for_active_session_user(self):
        principal = {"user_id": "user-7", "created_at": "created", "expires_at": "future"}
        stored_user = {"id": "user-7", "name": "Editor", "role": "editor", "pin": "secret",
                       "is_active": True, "created_at": "t0", "updated_at": "t1"}
        with patch.object(users, "_session_manager") as session_manager, patch.object(
            users, "list_json_items", return_value=[stored_user]
        ):
            session_manager.return_value.resolve.return_value = principal
            result = users.get_current_user(make_request("Bearer opaque"))
        self.assertEqual(result["user"]["id"], "user-7")
        self.assertNotIn("pin", result["user"])
        self.assertEqual(result["session_expires_at"], "future")

    def test_inactive_user_session_is_revoked_and_rejected(self):
        principal = {"user_id": "user-8", "expires_at": "future"}
        inactive = {"id": "user-8", "is_active": False, "pin": "secret"}
        with patch.object(users, "_session_manager") as session_manager, patch.object(
            users, "list_json_items", return_value=[inactive]
        ):
            session_manager.return_value.resolve.return_value = principal
            with self.assertRaises(HTTPException) as raised:
                users.get_current_user(make_request("Bearer stale"))
        self.assertEqual(raised.exception.status_code, 401)
        session_manager.return_value.revoke.assert_called_once_with("stale")

    def test_invalid_session_is_rejected(self):
        with patch.object(users, "_session_manager") as session_manager:
            session_manager.return_value.resolve.return_value = None
            with self.assertRaises(HTTPException) as raised:
                users.get_current_user(make_request("Bearer invalid"))
        self.assertEqual(raised.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
