from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from studio_core.api.routes import audiobooks, ebooks, project_commercial, videos
from studio_core.services.auth_principal import AuthenticatedPrincipal, get_current_principal


class ProjectCommercialMediaRBACTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(project_commercial.router, prefix="/api")
        self.app.include_router(ebooks.router, prefix="/api")
        self.app.include_router(audiobooks.router, prefix="/api")
        self.app.include_router(videos.router, prefix="/api")
        self.client = TestClient(self.app)
        self.project = {
            "id": "project-1",
            "created_by": "editor-1",
            "title": "Owned story",
            "story": {"title": "Owned story", "text": "Once upon a time"},
            "language": "pt-PT",
            "language_variants": {},
            "commercial": {"price": 10},
        }

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def set_principal(self, role: str, user_id: str = "editor-1"):
        self.app.dependency_overrides[get_current_principal] = lambda: AuthenticatedPrincipal(
            user_id=user_id, name="Test User", role=role
        )

    def test_all_private_routes_reject_anonymous_requests(self):
        self.assertEqual(self.client.get("/api/project-commercial/project-1").status_code, 401)
        self.assertEqual(self.client.patch("/api/project-commercial/project-1", json={"price": 12}).status_code, 401)
        self.assertEqual(self.client.post("/api/ebooks/export/project-1").status_code, 401)
        self.assertEqual(self.client.post("/api/audiobooks/export/project-1").status_code, 401)
        self.assertEqual(self.client.post("/api/videos/export/project-1").status_code, 401)

    def test_viewer_cannot_access_private_commercial_or_media_routes(self):
        self.set_principal("viewer")
        with patch.object(project_commercial, "_get_project", return_value=self.project):
            self.assertEqual(self.client.get("/api/project-commercial/project-1").status_code, 403)
        self.assertEqual(self.client.post("/api/ebooks/export/project-1").status_code, 403)
        self.assertEqual(self.client.post("/api/audiobooks/export/project-1").status_code, 403)
        self.assertEqual(self.client.post("/api/videos/export/project-1").status_code, 403)

    def test_editor_cannot_read_or_modify_another_users_commercial_data(self):
        self.set_principal("editor", user_id="different-editor")
        with patch.object(project_commercial, "_get_project", return_value=self.project):
            self.assertEqual(self.client.get("/api/project-commercial/project-1").status_code, 403)
            self.assertEqual(
                self.client.patch("/api/project-commercial/project-1", json={"price": 99}).status_code,
                403,
            )

    def test_editor_cannot_generate_media_for_another_users_project(self):
        self.set_principal("editor", user_id="different-editor")
        with patch.object(ebooks, "_get_project", return_value=self.project), patch.object(
            audiobooks, "_get_project", return_value=self.project
        ), patch.object(videos, "_get_project", return_value=self.project):
            self.assertEqual(self.client.post("/api/ebooks/export/project-1").status_code, 403)
            self.assertEqual(self.client.post("/api/audiobooks/export/project-1").status_code, 403)
            self.assertEqual(self.client.post("/api/videos/export/project-1").status_code, 403)

    def test_editor_can_read_and_update_own_commercial_data(self):
        self.set_principal("editor")
        updated = {**self.project, "commercial": {"price": 12}}
        with patch.object(project_commercial, "_get_project", return_value=self.project), patch.object(
            project_commercial, "update_json_item", return_value=updated
        ):
            self.assertEqual(self.client.get("/api/project-commercial/project-1").status_code, 200)
            response = self.client.patch("/api/project-commercial/project-1", json={"price": 12})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["commercial"]["price"], 12)

    def test_owner_can_access_another_users_commercial_data(self):
        self.set_principal("owner", user_id="owner-1")
        with patch.object(project_commercial, "_get_project", return_value=self.project):
            response = self.client.get("/api/project-commercial/project-1")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
