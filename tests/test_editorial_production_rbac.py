from __future__ import annotations

import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from studio_core.api.routes import editorial_engine, editorial_production, production_pipeline
from studio_core.services.auth_principal import AuthenticatedPrincipal, get_current_principal


class EditorialProductionRBACTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(editorial_engine.router, prefix="/api")
        self.app.include_router(editorial_production.router, prefix="/api")
        self.app.include_router(production_pipeline.router, prefix="/api")
        self.client = TestClient(self.app)

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def set_role(self, role: str):
        self.app.dependency_overrides[get_current_principal] = lambda: AuthenticatedPrincipal(
            user_id="rbac-test", name="RBAC Test", role=role
        )

    def test_editorial_build_requires_bearer_authentication(self):
        response = self.client.post("/api/editorial-engine/build/project-1", json={"text": "story"})
        self.assertEqual(response.status_code, 401)

    def test_viewer_cannot_trigger_editorial_production(self):
        self.set_role("viewer")
        response = self.client.post("/api/editorial-production/story/project-1", json={})
        self.assertEqual(response.status_code, 403)

    def test_viewer_cannot_run_production_pipeline(self):
        self.set_role("viewer")
        response = self.client.post("/api/production-pipeline/run/project-1", json={})
        self.assertEqual(response.status_code, 403)

    def test_editor_is_authorized_for_production_pipeline(self):
        self.set_role("editor")
        response = self.client.get("/api/production-pipeline")
        self.assertNotEqual(response.status_code, 401)
        self.assertNotEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
