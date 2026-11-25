from __future__ import annotations

import os
import tempfile
import unittest
from unittest.mock import patch

from fastapi import HTTPException

from studio_core.api.routes import users
from studio_core.services.auth_credentials import is_hashed_pin, verify_pin


class BootstrapOwnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.private = os.path.join(self.tmp.name, "private")
        self.storage = os.path.join(self.tmp.name, "storage")
        self.payload = users.OwnerBootstrapPayload(
            bootstrap_token="x" * 40, name="Initial Owner", pin="secure-pin-9876"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_bootstrap_creates_hashed_owner_and_session_once(self):
        session = {"token": "opaque", "expires_at": "future"}
        with patch.dict(os.environ, {
            "BARIBUDOS_BOOTSTRAP_TOKEN": "x" * 40,
            "BARIBUDOS_PRIVATE_ROOT": self.private,
            "BARIBUDOS_STORAGE_ROOT": self.storage,
        }), patch.object(users, "list_json_items", side_effect=[[], []]), patch.object(
            users, "append_json_item"
        ) as append, patch.object(users, "_session_manager") as session_mgr:
            session_mgr.return_value.create.return_value = session
            result = users.bootstrap_owner(self.payload)
        self.assertEqual(result["session"], session)
        self.assertEqual(result["user"]["role"], "owner")
        self.assertNotIn("pin", result["user"])
        owner_data = append.call_args.args[1]
        self.assertTrue(is_hashed_pin(owner_data["pin"]))
        self.assertTrue(verify_pin("secure-pin-9876", owner_data["pin"]))
        self.assertNotEqual(owner_data["pin"], "1234")

    def test_bootstrap_rejects_missing_configured_secret(self):
        with patch.dict(os.environ, {"BARIBUDOS_BOOTSTRAP_TOKEN": ""}):
            with self.assertRaises(HTTPException) as raised:
                users.bootstrap_owner(self.payload)
        self.assertEqual(raised.exception.status_code, 503)

    def test_bootstrap_rejects_bad_token(self):
        with patch.dict(os.environ, {"BARIBUDOS_BOOTSTRAP_TOKEN": "y" * 40}):
            with self.assertRaises(HTTPException) as raised:
                users.bootstrap_owner(self.payload)
        self.assertEqual(raised.exception.status_code, 401)

    def test_bootstrap_refuses_existing_users(self):
        with patch.dict(os.environ, {
            "BARIBUDOS_BOOTSTRAP_TOKEN": "x" * 40,
            "BARIBUDOS_PRIVATE_ROOT": self.private,
        }), patch.object(users, "list_json_items", return_value=[{"id": "already"}]):
            with self.assertRaises(HTTPException) as raised:
                users.bootstrap_owner(self.payload)
        self.assertEqual(raised.exception.status_code, 409)


if __name__ == "__main__":
    unittest.main()
