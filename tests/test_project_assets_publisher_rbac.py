from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from studio_core.api.routes import assets, projects, website_publisher
from studio_core.services.auth_principal import AuthenticatedPrincipal, get_current_principal


class ProjectAssetsPublisherRBACTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(projects.router, prefix="/api")
        self.app.include_router(assets.router, prefix="/api")
        self.app.include_router(website_publisher.router, prefix="/api")
        self.client = TestClient(self.app)

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def set_role(self, role: str, user_id: str = "rbac-user", name: str = "RBAC User"):
        self.app.dependency_overrides[get_current_principal] = lambda: AuthenticatedPrincipal(
            user_id=user_id, name=name, role=role
        )

    def test_project_routes_require_authentication(self):
        self.assertEqual(self.client.get("/api/projects").status_code, 401)
        self.assertEqual(self.client.post("/api/projects", json={"title": "Story"}).status_code, 401)
        self.assertEqual(self.client.patch("/api/projects/project-1", json={}).status_code, 401)

    def test_viewer_cannot_access_project_crud(self):
        self.set_role("viewer")
        self.assertEqual(self.client.get("/api/projects").status_code, 403)
        self.assertEqual(self.client.post("/api/projects", json={"title": "Story"}).status_code, 403)
        self.assertEqual(self.client.patch("/api/projects/project-1", json={}).status_code, 403)

    def test_project_creator_is_taken_from_server_principal(self):
        self.set_role("editor", user_id="trusted-user-9", name="Trusted Editor")
        with patch.object(projects, "append_json_item") as append:
            response = self.client.post("/api/projects", json={
                "title": "A new story",
                "created_by": "attacker-controlled-id",
                "created_by_name": "Attacker",
            })
        self.assertEqual(response.status_code, 200)
        saved = append.call_args.args[1]
        self.assertEqual(saved["created_by"], "trusted-user-9")
        self.assertEqual(saved["created_by_name"], "Trusted Editor")
        self.assertEqual(response.json()["project"]["created_by"], "trusted-user-9")

    def test_editor_only_sees_private_projects_owned_by_authenticated_id(self):
        self.set_role("editor", user_id="editor-1", name="Same Display Name")
        rows = [
            {"id": "own", "created_by": "editor-1", "created_by_name": "Other", "visible_to_owner_only": True},
            {"id": "foreign", "created_by": "foreign-user", "created_by_name": "Same Display Name", "visible_to_owner_only": True},
            {"id": "shared", "created_by": "foreign-user", "visible_to_owner_only": False},
        ]
        with patch.object(projects, "list_json_items", return_value=rows):
            response = self.client.get("/api/projects")
        self.assertEqual(response.status_code, 200)
        self.assertEqual({p["id"] for p in response.json()["projects"]}, {"own", "shared"})

    def test_owner_can_list_all_projects(self):
        self.set_role("owner")
        rows = [{"id": "p1", "created_by": "other", "visible_to_owner_only": True}]
        with patch.object(projects, "list_json_items", return_value=rows):
            response = self.client.get("/api/projects")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["projects"]), 1)

    def test_assets_routes_require_authentication_and_reject_viewer(self):
        self.assertEqual(self.client.get("/api/assets").status_code, 401)
        self.set_role("viewer")
        self.assertEqual(self.client.get("/api/assets").status_code, 403)

    def test_website_publisher_requires_authentication_and_rejects_viewer(self):
        self.assertEqual(self.client.post("/api/website-publisher/publish/project-1").status_code, 401)
        self.set_role("viewer")
        self.assertEqual(self.client.post("/api/website-publisher/publish/project-1").status_code, 403)


if __name__ == "__main__":
    unittest.main()
