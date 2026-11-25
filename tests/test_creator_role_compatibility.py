from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from studio_core.api.routes import project_commercial, projects
from studio_core.services.auth_principal import AuthenticatedPrincipal, get_current_principal


class CreatorRoleCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(projects.router, prefix="/api")
        self.app.include_router(project_commercial.router, prefix="/api")
        self.client = TestClient(self.app)
        self.owned = {
            "id": "creator-project",
            "created_by": "creator-1",
            "created_by_name": "Creator",
            "visible_to_owner_only": True,
            "commercial": {"price": 10},
        }
        self.foreign = {
            "id": "foreign-project",
            "created_by": "another-user",
            "visible_to_owner_only": True,
            "commercial": {"price": 99},
        }

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def set_creator(self):
        self.app.dependency_overrides[get_current_principal] = lambda: AuthenticatedPrincipal(
            user_id="creator-1", name="Creator", role="creator"
        )

    def test_creator_can_list_own_private_project(self):
        self.set_creator()
        with patch.object(projects, "list_json_items", return_value=[self.owned, self.foreign]):
            response = self.client.get("/api/projects")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.json()["projects"]], ["creator-project"])

    def test_creator_can_read_own_commercial_data(self):
        self.set_creator()
        with patch.object(project_commercial, "_get_project", return_value=self.owned):
            response = self.client.get("/api/project-commercial/creator-project")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["commercial"]["price"], 10)

    def test_creator_cannot_access_another_users_project(self):
        self.set_creator()
        with patch.object(project_commercial, "_get_project", return_value=self.foreign):
            response = self.client.get("/api/project-commercial/foreign-project")
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
