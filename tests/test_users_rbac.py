from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from studio_core.api.routes import users
from studio_core.services.auth_principal import AuthenticatedPrincipal, get_current_principal


class UserManagementRBACTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(users.router, prefix="/api")
        self.client = TestClient(self.app)

    def set_principal(self, role: str):
        self.app.dependency_overrides[get_current_principal] = lambda: AuthenticatedPrincipal(
            user_id="test-id", name="Test", role=role
        )

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def test_viewer_cannot_list_users(self):
        self.set_principal("viewer")
        response = self.client.get("/api/users")
        self.assertEqual(response.status_code, 403)

    def test_editor_cannot_create_user(self):
        self.set_principal("editor")
        response = self.client.post("/api/users", json={
            "name": "New user", "role": "editor", "pin": "abc123", "is_active": True
        })
        self.assertEqual(response.status_code, 403)

    def test_owner_can_list_users(self):
        self.set_principal("owner")
        with patch.object(users, "list_json_items", return_value=[]):
            response = self.client.get("/api/users")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True, "users": []})

    def test_admin_can_list_users(self):
        self.set_principal("admin")
        with patch.object(users, "list_json_items", return_value=[]):
            response = self.client.get("/api/users")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
