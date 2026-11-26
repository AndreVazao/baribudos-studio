from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from studio_core.api.routes import (
    commerce_groups, distribution_hub, editorial_engine, editorial_production,
    product_credits, project_integrity, publication_package, publish_readiness,
    sponsors, sponsorship_scopes, story_layout, story_source, story_translation,
    v1_readiness, website_bundle_reconcile, website_bundles, website_contract,
    website_visual_set_reconcile, website_visual_sets,
)
from studio_core.services.auth_principal import AuthenticatedPrincipal, get_current_principal


class ProjectProductionRoutesRBACTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        modules = (
            commerce_groups, distribution_hub, editorial_engine, editorial_production,
            product_credits, project_integrity, publication_package, publish_readiness,
            sponsors, sponsorship_scopes, story_layout, story_source, story_translation,
            v1_readiness, website_bundle_reconcile, website_bundles, website_contract,
            website_visual_set_reconcile, website_visual_sets,
        )
        for module in modules:
            self.app.include_router(module.router, prefix="/api")
        self.client = TestClient(self.app)

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def set_principal(self, role: str, user_id: str = "editor-1"):
        self.app.dependency_overrides[get_current_principal] = lambda: AuthenticatedPrincipal(
            user_id=user_id, name="Production Test", role=role
        )

    def test_private_project_and_commercial_routes_reject_anonymous_requests(self):
        requests = (
            ("GET", "/api/story-layout/project-1", None),
            ("POST", "/api/story-layout/page/project-1", {}),
            ("GET", "/api/story-source/project-1", None),
            ("POST", "/api/story-source/project-1", {}),
            ("GET", "/api/story-translation/project-1", None),
            ("POST", "/api/story-translation/project-1/generate", {}),
            ("POST", "/api/editorial-engine/build/project-1", {}),
            ("POST", "/api/editorial-production/story/project-1", {}),
            ("GET", "/api/product-credits/project-1", None),
            ("POST", "/api/product-credits/project-1/rebuild", {}),
            ("GET", "/api/project-integrity/project-1", None),
            ("POST", "/api/project-integrity/project-1/repair?user_role=owner&user_name=André", {}),
            ("GET", "/api/publication-package/project-1", None),
            ("POST", "/api/publication-package/project-1/freeze?user_role=owner", {}),
            ("GET", "/api/publish-readiness/project-1", None),
            ("POST", "/api/publish-readiness/project-1/mark-ready?user_role=owner", {}),
            ("GET", "/api/distribution/projects/project-1/channels", None),
            ("PATCH", "/api/distribution/projects/project-1/channels/website?user_role=owner", {}),
            ("POST", "/api/website-bundles/publish/group-1", {}),
            ("GET", "/api/website-bundles/status", None),
            ("POST", "/api/website-visual-sets/publish-all", {}),
            ("GET", "/api/website-bundles-reconcile", None),
            ("GET", "/api/website-visual-sets-reconcile", None),
            ("GET", "/api/website-visual-sets/export", None),
            ("GET", "/api/website-visual-sets/status", None),
            ("GET", "/api/website-visual-sets/summary", None),
            ("GET", "/api/sponsorship-scopes/resolve/project-1", None),
            ("GET", "/api/publication-package/project-1/freeze-preview", None),
            ("POST", "/api/publish-readiness/project-1/sync", {}),
            ("POST", "/api/publish-readiness/project-1/unmark-ready", {}),
            ("GET", "/api/v1-readiness/project-1", None),
            ("GET", "/api/website-contract/validate/project-1", None),
            ("GET", "/api/website-contract/validate-all", None),
            ("GET", "/api/sponsors", None),
            ("POST", "/api/sponsors", {}),
            ("GET", "/api/sponsorship-scopes", None),
            ("POST", "/api/sponsorship-scopes", {}),
            ("GET", "/api/commerce-groups", None),
            ("POST", "/api/commerce-groups", {"slug": "bundle", "name": "Bundle"}),
        )
        for method, path, payload in requests:
            response = self.client.request(method, path, json=payload)
            self.assertEqual(response.status_code, 401, f"{method} {path}: {response.status_code}")

    def test_viewer_cannot_access_project_even_if_client_claims_owner(self):
        self.set_principal("viewer", "viewer-1")
        with patch("studio_core.services.project_route_auth.read_json", return_value=[
            {"id": "project-1", "created_by": "owner-1"}
        ]):
            response = self.client.post(
                "/api/project-integrity/project-1/repair?user_role=owner&user_name=André",
                json={},
            )
        self.assertEqual(response.status_code, 403)

    def test_editor_can_read_own_story_source_but_not_another_users_project(self):
        self.set_principal("editor", "editor-1")
        with patch("studio_core.services.project_route_auth.read_json", return_value=[
            {"id": "project-1", "created_by": "editor-1"}
        ]), patch("studio_core.api.routes.story_source.get_story_source", return_value={"text": "own"}):
            own = self.client.get("/api/story-source/project-1")
        self.assertEqual(own.status_code, 200)
        self.assertEqual(own.json()["story_source"]["text"], "own")

        with patch("studio_core.services.project_route_auth.read_json", return_value=[
            {"id": "project-2", "created_by": "other-user"}
        ]):
            foreign = self.client.get("/api/story-source/project-2")
        self.assertEqual(foreign.status_code, 403)

    def test_distribution_role_is_taken_from_session_not_query(self):
        self.set_principal("editor", "editor-1")
        with patch("studio_core.services.project_route_auth.read_json", return_value=[
            {"id": "project-1", "created_by": "editor-1"}
        ]):
            response = self.client.patch(
                "/api/distribution/projects/project-1/channels/website?user_role=owner&user_name=André",
                json={"status": "published"},
            )
        self.assertEqual(response.status_code, 403)

    def test_global_commerce_and_sponsor_mutations_are_owner_admin_only(self):
        self.set_principal("editor", "editor-1")
        self.assertEqual(self.client.post("/api/sponsors", json={"name": "Sponsor"}).status_code, 403)
        self.assertEqual(self.client.post("/api/sponsorship-scopes", json={"name": "Scope"}).status_code, 403)
        self.assertEqual(self.client.post("/api/commerce-groups", json={"slug": "bundle", "name": "Bundle"}).status_code, 403)
        self.assertEqual(self.client.post("/api/website-visual-sets/publish-all").status_code, 403)
        self.assertEqual(self.client.post("/api/website-bundles/publish/group-1").status_code, 403)


if __name__ == "__main__":
    unittest.main()
