from __future__ import annotations

import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from studio_core.api.routes import db_control, deploy_control, secret_control, updater, website_admin, website_control
from studio_core.services.auth_principal import AuthenticatedPrincipal, get_current_principal


class AdministrativeControlRBACTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        for module in (db_control, deploy_control, secret_control, updater, website_admin, website_control):
            self.app.include_router(module.router, prefix="/api")
        self.client = TestClient(self.app)

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def set_role(self, role: str):
        self.app.dependency_overrides[get_current_principal] = lambda: AuthenticatedPrincipal(
            user_id="admin-rbac-test", name="Admin RBAC Test", role=role
        )

    def test_secret_vault_listing_requires_authentication(self):
        response = self.client.get("/api/secret-control/vaults")
        self.assertEqual(response.status_code, 401)

    def test_database_status_requires_authentication(self):
        response = self.client.get("/api/db-control/status")
        self.assertEqual(response.status_code, 401)

    def test_deployment_summary_requires_authentication(self):
        response = self.client.get("/api/deploy-control/vercel/summary")
        self.assertEqual(response.status_code, 401)

    def test_viewer_cannot_change_website_product_visibility(self):
        self.set_role("viewer")
        response = self.client.patch("/api/website-admin/products/product-1/visibility", json={"active": False})
        self.assertEqual(response.status_code, 403)

    def test_editor_cannot_access_secret_vault(self):
        self.set_role("editor")
        response = self.client.get("/api/secret-control/vaults")
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
