from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi import HTTPException

from studio_core.api.routes import users
from studio_core.services.auth_credentials import hash_pin, is_hashed_pin, verify_pin


class UserLoginSessionTests(unittest.TestCase):
    def setUp(self):
        self.user = {
            "id": "u-test", "name": "Test Owner", "role": "owner",
            "pin": "legacy123", "is_active": True, "created_at": "t0", "updated_at": "t0",
        }

    def test_login_migrates_legacy_pin_and_returns_safe_dto_and_session(self):
        session = {"token": "opaque-session", "expires_at": "future"}
        with patch.object(users, "ensure_default_owner"), patch.object(
            users, "list_json_items", return_value=[dict(self.user)]
        ), patch.object(users, "update_json_item", side_effect=lambda file, uid, fn: fn(dict(self.user))) as update, patch.object(
            users, "_session_manager"
        ) as manager:
            manager.return_value.create.return_value = session
            result = users.login({"name": " test owner ", "pin": "legacy123"})
        self.assertEqual(result["session"], session)
        self.assertEqual(result["user"]["id"], "u-test")
        self.assertNotIn("pin", result["user"])
        self.assertNotIn("password", result["user"])
        update.assert_called_once()
        migrated = update.call_args.args[2](dict(self.user))
        self.assertTrue(is_hashed_pin(migrated["pin"]))
        self.assertTrue(verify_pin("legacy123", migrated["pin"]))
        manager.return_value.create.assert_called_once_with("u-test")

    def test_login_accepts_hashed_pin_without_rewriting(self):
        hashed = hash_pin("secret")
        user = {**self.user, "pin": hashed}
        with patch.object(users, "ensure_default_owner"), patch.object(
            users, "list_json_items", return_value=[user]
        ), patch.object(users, "update_json_item") as update, patch.object(users, "_session_manager") as manager:
            manager.return_value.create.return_value = {"token": "opaque", "expires_at": "future"}
            result = users.login({"name": "Test Owner", "pin": "secret"})
        self.assertNotIn("pin", result["user"])
        update.assert_not_called()

    def test_invalid_credentials_do_not_issue_session(self):
        with patch.object(users, "ensure_default_owner"), patch.object(
            users, "list_json_items", return_value=[dict(self.user)]
        ), patch.object(users, "_session_manager") as manager:
            with self.assertRaises(HTTPException) as raised:
                users.login({"name": "Test Owner", "pin": "wrong"})
        self.assertEqual(raised.exception.status_code, 401)
        manager.return_value.create.assert_not_called()

    def test_inactive_account_cannot_login(self):
        inactive = {**self.user, "is_active": False}
        with patch.object(users, "ensure_default_owner"), patch.object(
            users, "list_json_items", return_value=[inactive]
        ), patch.object(users, "_session_manager") as manager:
            with self.assertRaises(HTTPException) as raised:
                users.login({"name": "Test Owner", "pin": "legacy123"})
        self.assertEqual(raised.exception.status_code, 401)
        manager.return_value.create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
