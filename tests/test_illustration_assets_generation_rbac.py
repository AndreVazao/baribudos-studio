from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from studio_core.api.routes import illustration_assets, illustration_generation
from studio_core.services.auth_principal import AuthenticatedPrincipal, get_current_principal


class IllustrationAssetsGenerationRBACTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(illustration_assets.router, prefix="/api")
        self.app.include_router(illustration_generation.router, prefix="/api")
        self.client = TestClient(self.app)

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def set_principal(self, role: str, user_id: str = "editor-1"):
        self.app.dependency_overrides[get_current_principal] = lambda: AuthenticatedPrincipal(
            user_id=user_id, name="RBAC Test", role=role
        )

    def test_all_illustration_asset_and_generation_routes_require_authentication(self):
        responses = (
            self.client.get("/api/illustration-assets/storyboard/project-1"),
            self.client.post("/api/illustration-assets/upload"),
            self.client.get("/api/illustration-generation?project_id=project-1"),
            self.client.post("/api/illustration-generation/queue/project-1", json={}),
            self.client.get("/api/illustration-generation/package/project-1"),
            self.client.post("/api/illustration-generation/job/job-1", json={}),
            self.client.post("/api/illustration-generation/import"),
        )
        self.assertTrue(all(response.status_code == 401 for response in responses))

    def test_viewer_is_denied_from_illustration_routes(self):
        self.set_principal("viewer")
        responses = (
            self.client.get("/api/illustration-assets/storyboard/project-1"),
            self.client.get("/api/illustration-generation?project_id=project-1"),
            self.client.post("/api/illustration-generation/queue/project-1", json={}),
            self.client.get("/api/illustration-generation/package/project-1"),
        )
        self.assertTrue(all(response.status_code == 403 for response in responses))

    def test_editor_can_list_jobs_for_owned_project(self):
        self.set_principal("editor", "editor-1")
        with patch("studio_core.services.project_route_auth.read_json", return_value=[
            {"id": "project-1", "created_by": "editor-1"}
        ]), patch.object(illustration_generation, "list_illustration_jobs", return_value=[
            {"id": "job-1", "project_id": "project-1"}
        ]):
            response = self.client.get("/api/illustration-generation?project_id=project-1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["jobs"][0]["id"], "job-1")

    def test_editor_cannot_list_jobs_for_another_users_project(self):
        self.set_principal("editor", "editor-1")
        with patch("studio_core.services.project_route_auth.read_json", return_value=[
            {"id": "project-1", "created_by": "another-user"}
        ]):
            response = self.client.get("/api/illustration-generation?project_id=project-1")
        self.assertEqual(response.status_code, 403)

    def test_editor_cannot_update_job_owned_by_another_users_project(self):
        self.set_principal("creator", "creator-1")
        with patch.object(illustration_generation, "list_illustration_jobs", return_value=[
            {"id": "job-1", "project_id": "project-1"}
        ]), patch("studio_core.services.project_route_auth.read_json", return_value=[
            {"id": "project-1", "created_by": "another-user"}
        ]), patch.object(illustration_generation, "update_illustration_job") as update:
            response = self.client.post("/api/illustration-generation/job/job-1", json={"state": "approved"})
        self.assertEqual(response.status_code, 403)
        update.assert_not_called()

    def test_owner_can_list_global_illustration_jobs(self):
        self.set_principal("owner")
        with patch.object(illustration_generation, "list_illustration_jobs", return_value=[]):
            response = self.client.get("/api/illustration-generation")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["jobs"], [])

    def test_editor_cannot_list_global_illustration_jobs(self):
        self.set_principal("editor", "editor-1")
        response = self.client.get("/api/illustration-generation")
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
