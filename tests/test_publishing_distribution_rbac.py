from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from studio_core.api.routes import distribution_hub_v6, publishing
from studio_core.services.auth_principal import AuthenticatedPrincipal, get_current_principal


class PublishingDistributionRBACTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(distribution_hub_v6.router, prefix="/api")
        self.app.include_router(publishing.router, prefix="/api")
        self.client = TestClient(self.app)
        self.project = {
            "id": "project-1",
            "created_by": "owner-editor",
            "ready_for_publish": True,
        }

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def set_principal(self, role: str, user_id: str = "owner-editor"):
        self.app.dependency_overrides[get_current_principal] = lambda: AuthenticatedPrincipal(
            user_id=user_id, name="Trusted Actor", role=role
        )

    def test_private_publishing_and_distribution_routes_require_authentication(self):
        self.assertEqual(self.client.get("/api/distribution-hub/project-1").status_code, 401)
        self.assertEqual(self.client.post("/api/distribution-hub/project-1/refresh").status_code, 401)
        self.assertEqual(self.client.patch("/api/distribution-hub/project-1", json={}).status_code, 401)
        self.assertEqual(self.client.get("/api/publishing").status_code, 401)
        self.assertEqual(self.client.post("/api/publishing/publish", json={"project_id": "project-1"}).status_code, 401)

    def test_viewer_cannot_read_or_mutate_distribution_or_publish(self):
        self.set_principal("viewer")
        self.assertEqual(self.client.get("/api/distribution-hub/project-1").status_code, 403)
        self.assertEqual(self.client.post("/api/distribution-hub/project-1/refresh").status_code, 403)
        self.assertEqual(self.client.patch("/api/distribution-hub/project-1", json={}).status_code, 403)
        self.assertEqual(self.client.get("/api/publishing").status_code, 403)
        self.assertEqual(self.client.post("/api/publishing/publish", json={"project_id": "project-1"}).status_code, 403)

    def test_editor_cannot_access_another_users_distribution_or_publish(self):
        self.set_principal("editor", user_id="attacker")
        with patch.object(distribution_hub_v6, "_get_project", return_value=self.project), patch.object(
            publishing, "_get_project", return_value=self.project
        ):
            self.assertEqual(self.client.get("/api/distribution-hub/project-1").status_code, 403)
            self.assertEqual(self.client.post("/api/distribution-hub/project-1/refresh").status_code, 403)
            self.assertEqual(self.client.patch("/api/distribution-hub/project-1", json={"status": "ready"}).status_code, 403)
            self.assertEqual(
                self.client.post("/api/publishing/publish", json={"project_id": "project-1"}).status_code,
                403,
            )

    def test_editor_publication_listing_is_limited_to_owned_projects(self):
        self.set_principal("editor", user_id="editor-1")
        projects = [
            {"id": "own", "created_by": "editor-1"},
            {"id": "foreign", "created_by": "other"},
        ]
        publications = [
            {"id": "pub-own", "project_id": "own"},
            {"id": "pub-foreign", "project_id": "foreign"},
        ]
        with patch.object(publishing, "read_json", side_effect=[publications, projects]):
            response = self.client.get("/api/publishing")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.json()["publications"]], ["pub-own"])

    def test_owner_can_read_any_distribution_project(self):
        self.set_principal("owner", user_id="owner-id")
        with patch.object(distribution_hub_v6, "_get_project", return_value=self.project), patch.object(
            distribution_hub_v6, "get_distribution_hub_snapshot", return_value={"status": "draft"}
        ):
            response = self.client.get("/api/distribution-hub/project-1")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
