from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from studio_core.core.config import APP_CONFIG
from studio_core.services import auth_principal


class AuthenticatedPrincipalTests(unittest.TestCase):
    def test_missing_bearer_is_401(self):
        with self.assertRaises(HTTPException) as raised:
            auth_principal.get_current_principal(None)
        self.assertEqual(raised.exception.status_code, 401)

    def test_unknown_session_is_401(self):
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="not-a-session")
        with patch.object(auth_principal, "_session_manager") as manager:
            manager.return_value.resolve.return_value = None
            with self.assertRaises(HTTPException) as raised:
                auth_principal.get_current_principal(credentials)
        self.assertEqual(raised.exception.status_code, 401)

    def test_inactive_account_is_rejected_and_session_revoked(self):
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-token")
        with patch.object(auth_principal, "_session_manager") as manager, patch.object(
            auth_principal, "get_json_item", return_value={"id": "u1", "is_active": False}
        ):
            manager.return_value.resolve.return_value = {"user_id": "u1"}
            with self.assertRaises(HTTPException) as raised:
                auth_principal.get_current_principal(credentials)
        self.assertEqual(raised.exception.status_code, 401)
        manager.return_value.revoke.assert_called_once_with("valid-token")

    def test_principal_role_is_loaded_from_persisted_user_not_request(self):
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-token")
        persisted = {"id": "u1", "name": "Editor", "role": "editor", "is_active": True}
        with patch.object(auth_principal, "_session_manager") as manager, patch.object(
            auth_principal, "get_json_item", return_value=persisted
        ):
            manager.return_value.resolve.return_value = {"user_id": "u1"}
            principal = auth_principal.get_current_principal(credentials)
        self.assertEqual(principal.user_id, "u1")
        self.assertEqual(principal.role, "editor")

    def test_persisted_user_identity_mismatch_is_rejected_and_revoked(self):
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-token")
        with patch.object(auth_principal, "_session_manager") as manager, patch.object(
            auth_principal,
            "get_json_item",
            return_value={"id": "different-user", "name": "Unexpected", "role": "owner"},
        ):
            manager.return_value.resolve.return_value = {"user_id": "u1"}
            with self.assertRaises(HTTPException) as raised:
                auth_principal.get_current_principal(credentials)
        self.assertEqual(raised.exception.status_code, 401)
        manager.return_value.revoke.assert_called_once_with("valid-token")

    def test_malformed_display_fields_fall_back_to_safe_principal_values(self):
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-token")
        persisted = {"id": "u1", "name": None, "role": None, "is_active": True}
        with patch.object(auth_principal, "_session_manager") as manager, patch.object(
            auth_principal, "get_json_item", return_value=persisted
        ):
            manager.return_value.resolve.return_value = {"user_id": "u1"}
            principal = auth_principal.get_current_principal(credentials)
        self.assertEqual(principal.user_id, "u1")
        self.assertEqual(principal.name, "")
        self.assertEqual(principal.role, "viewer")

    def test_production_requires_explicit_private_root(self):
        with patch.dict(os.environ, {"APP_ENV": "production"}, clear=False), patch.dict(
            os.environ, {"BARIBUDOS_PRIVATE_ROOT": ""}, clear=False
        ), patch.object(APP_CONFIG, "environment", "production"):
            with self.assertRaises(auth_principal.SessionStoreError):
                auth_principal._session_manager()

    def test_private_root_cannot_be_inside_public_storage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with patch.object(APP_CONFIG, "storage_root", root), patch.dict(
                os.environ, {"BARIBUDOS_PRIVATE_ROOT": str(root / "private")}, clear=False
            ):
                with self.assertRaises(auth_principal.SessionStoreError):
                    auth_principal._session_manager()


if __name__ == "__main__":
    unittest.main()
