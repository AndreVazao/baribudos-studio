from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from studio_core.api.routes import covers, diagnostics, illustrations, ip_canons, ip_characters, ip_metadata, ip_branding, ip_palette, jobs
from studio_core.services.auth_principal import AuthenticatedPrincipal, get_current_principal


class LegacyRoutesRBACTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        for module in (covers, diagnostics, illustrations, ip_canons, ip_characters, ip_metadata, ip_branding, ip_palette, jobs):
            self.app.include_router(module.router, prefix="/api")
        self.client = TestClient(self.app)

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def set_principal(self, role: str, user_id: str = "editor-1"):
        self.app.dependency_overrides[get_current_principal] = lambda: AuthenticatedPrincipal(
            user_id=user_id, name="Authenticated Test", role=role
        )

    def test_private_legacy_routes_reject_anonymous_even_when_client_supplies_identity_fields(self):
        response = self.client.get("/api/ip-canons/private-ip/visual?user_id=owner-1&user_role=owner")
        self.assertEqual(response.status_code, 401)
        response = self.client.get("/api/ip-characters/private-ip?user_id=owner-1&user_role=owner")
        self.assertEqual(response.status_code, 401)
        response = self.client.get("/api/ip-metadata/private-ip?user_id=owner-1&user_role=owner")
        self.assertEqual(response.status_code, 401)
        response = self.client.get("/api/ip-branding/private-ip?user_id=owner-1&user_role=owner")
        self.assertEqual(response.status_code, 401)
        response = self.client.get("/api/ip-palette/private-ip?user_id=owner-1&user_role=owner")
        self.assertEqual(response.status_code, 401)

    def test_query_identity_cannot_impersonate_private_ip_owner(self):
        self.set_principal("editor", "editor-1")
        private_ip = {
            "id": "ip-1", "slug": "private-ip", "owner_id": "owner-1",
            "owner_name": "Authenticated Test", "visible_to_owner_only": True,
            "exclusive": True, "editable_by_roles": ["owner", "admin"],
            "allowed_editor_user_ids": [],
        }
        with patch("studio_core.services.ip_route_auth.get_ip_by_slug", return_value=private_ip):
            response = self.client.get("/api/ip-canons/private-ip/visual?user_id=owner-1&user_role=owner")
        self.assertEqual(response.status_code, 403)

    def test_authenticated_owner_can_pass_private_ip_read_gate(self):
        self.set_principal("owner", "owner-1")
        private_ip = {
            "id": "ip-1", "slug": "private-ip", "owner_id": "owner-1",
            "visible_to_owner_only": True, "exclusive": True,
            "editable_by_roles": ["owner"], "allowed_editor_user_ids": [],
        }
        with patch("studio_core.services.ip_route_auth.get_ip_by_slug", return_value=private_ip), \
             patch("studio_core.api.routes.ip_canons.get_ip_by_slug", return_value=private_ip), \
             patch("studio_core.api.routes.ip_canons._canon_path") as canon_path:
            canon_path.return_value.exists.return_value = False
            response = self.client.get("/api/ip-canons/private-ip/visual")
        self.assertEqual(response.status_code, 404)

    def test_diagnostics_are_owner_admin_only(self):
        self.assertEqual(self.client.get("/api/diagnostics").status_code, 401)
        self.set_principal("editor")
        self.assertEqual(self.client.get("/api/diagnostics").status_code, 403)
        self.set_principal("owner", "owner-1")
        with patch("studio_core.api.routes.diagnostics.read_json", side_effect=[{}, [], []]):
            response = self.client.get("/api/diagnostics")
        self.assertEqual(response.status_code, 200)

    def test_global_jobs_are_owner_admin_only_and_project_jobs_are_scoped(self):
        self.assertEqual(self.client.get("/api/jobs?user_role=owner").status_code, 401)
        self.set_principal("editor", "editor-1")
        self.assertEqual(self.client.get("/api/jobs").status_code, 403)
        rows = [{"id": "job-own", "project_id": "project-own"}, {"id": "job-other", "project_id": "project-other"}]
        with patch("studio_core.services.project_route_auth.read_json", return_value=[
            {"id": "project-own", "created_by": "editor-1"}
        ]), patch("studio_core.api.routes.jobs.list_jobs", return_value=rows):
            response = self.client.get("/api/jobs?project_id=project-own")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([job["id"] for job in response.json()], ["job-own"])

    def test_job_creation_uses_server_identity_and_requires_project_ownership(self):
        self.set_principal("creator", "creator-1")
        with patch("studio_core.services.project_route_auth.read_json", return_value=[
            {"id": "project-own", "created_by": "creator-1"}
        ]), patch("studio_core.api.routes.jobs.create_job", return_value={"id": "job-1"}) as create:
            response = self.client.post("/api/jobs", json={
                "type": "render", "project_id": "project-own", "created_by": "attacker",
                "user_id": "attacker", "user_role": "owner",
            })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(create.call_args.args[1]["created_by"], "creator-1")

    def test_cover_generation_requires_authentication_and_project_ownership(self):
        self.assertEqual(self.client.post("/api/covers/build", json={"project_id": "project-1"}).status_code, 401)
        self.set_principal("editor", "editor-1")
        with patch("studio_core.services.project_route_auth.read_json", return_value=[
            {"id": "project-1", "created_by": "someone-else"}
        ]):
            response = self.client.post("/api/covers/build", json={"project_id": "project-1"})
        self.assertEqual(response.status_code, 403)

    def test_legacy_illustration_upload_requires_project_session(self):
        self.assertEqual(self.client.post(
            "/api/illustrations/upload",
            data={"saga_id": "baribudos", "project_id": "project-1"},
            files={"file": ("test.png", b"image", "image/png")},
        ).status_code, 401)


if __name__ == "__main__":
    unittest.main()
