from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from studio_core.api.routes import (
    health, local_ai_installer, local_audio_engine_manager, local_audio_installer,
    local_engine_manager, pairing, persistent_memory, public_assets, saga_loader,
    saga_runtime, saga_visual_sets, sagas, settings, system_smoke, system_smoke_v1,
)
from studio_core.services.auth_principal import AuthenticatedPrincipal, get_current_principal


class PrivateAdminSurfacesRBACTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        modules = (
            health, local_ai_installer, local_audio_engine_manager, local_audio_installer,
            local_engine_manager, pairing, persistent_memory, public_assets, saga_loader,
            saga_runtime, saga_visual_sets, sagas, settings, system_smoke, system_smoke_v1,
        )
        for module in modules:
            self.app.include_router(module.router, prefix="/api")
        self.client = TestClient(self.app)

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def set_principal(self, role: str, user_id: str = "user-1"):
        self.app.dependency_overrides[get_current_principal] = lambda: AuthenticatedPrincipal(
            user_id=user_id, name="RBAC Test", role=role
        )

    def test_private_admin_routes_reject_anonymous_requests(self):
        paths = (
            ("GET", "/api/settings"),
            ("POST", "/api/settings"),
            ("GET", "/api/persistent-memory/projects"),
            ("POST", "/api/persistent-memory/initialize"),
            ("GET", "/api/sagas"),
            ("POST", "/api/sagas"),
            ("GET", "/api/saga-loader"),
            ("GET", "/api/saga-loader/baribudos"),
            ("GET", "/api/saga-runtime/baribudos"),
            ("GET", "/api/saga-visual-sets"),
            ("PUT", "/api/saga-visual-sets"),
            ("GET", "/api/pairing"),
            ("POST", "/api/pairing/create"),
            ("POST", "/api/pairing/revoke/ANY-CODE"),
            ("GET", "/api/local-ai/status"),
            ("POST", "/api/local-ai/setup"),
            ("GET", "/api/local-audio/status"),
            ("GET", "/api/local-engine-manager/status"),
            ("GET", "/api/local-audio-engine-manager/status"),
            ("GET", "/api/system-smoke"),
            ("GET", "/api/system-smoke-v1"),
        )
        for method, path in paths:
            payload = {"pc_name": "studio", "lan_host": "127.0.0.1"} if path == "/api/pairing/create" else {}
            response = self.client.request(method, path, json=payload if method in {"POST", "PUT"} else None)
            self.assertEqual(response.status_code, 401, f"{method} {path}: {response.status_code}")

    def test_viewer_cannot_change_private_settings_or_run_local_operations(self):
        self.set_principal("viewer")
        self.assertEqual(self.client.get("/api/settings").status_code, 403)
        self.assertEqual(self.client.post("/api/settings", json={"youtube_publish": True}).status_code, 403)
        self.assertEqual(self.client.post("/api/local-ai/setup", json={}).status_code, 403)
        self.assertEqual(self.client.post("/api/local-audio-engine-manager/stop", json={"provider": "x"}).status_code, 403)
        self.assertEqual(self.client.post("/api/system-smoke/project-1").status_code, 403)

    def test_saga_can_edit_legacy_role_segment_is_ignored(self):
        self.set_principal("editor", "editor-1")
        ip = {
            "id": "ip-1", "slug": "public-ip", "owner_id": "owner-1",
            "visible_to_owner_only": False, "exclusive": False,
            "editable_by_roles": ["owner", "admin"], "allowed_editor_user_ids": [],
        }
        with patch("studio_core.services.ip_route_auth.get_ip_by_slug", return_value=ip):
            response = self.client.get("/api/saga-loader/public-ip/can-edit/owner")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["can_edit"])
        self.assertEqual(response.json()["role"], "editor")

    def test_pairing_resolve_remains_a_capability_endpoint_but_management_is_private(self):
        response = self.client.get("/api/pairing/resolve/BARI-AAAA-BBBB-CCCC")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["ok"])
        self.assertEqual(self.client.get("/api/pairing").status_code, 401)

    def test_public_health_does_not_disclose_runtime_or_filesystem_details(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["ok"])
        for key in ("host", "port", "environment", "storage_root", "project_root"):
            self.assertNotIn(key, body)

    def test_public_asset_manifest_never_returns_private_storage_paths(self):
        manifest = {
            "ok": True,
            "assets": {
                "primary_logo": {
                    "asset_id": "asset-1", "url": "https://cdn.example/logo.png",
                    "storage_path": "/private/storage/brand/logo.png", "status": "published",
                },
                "gallery": [{
                    "asset_id": "asset-2", "url": "https://cdn.example/gallery.png",
                    "storage_path": "/private/storage/gallery.png", "status": "published",
                }],
            },
        }
        with patch("studio_core.api.routes.public_assets.build_ip_asset_manifest", return_value=manifest):
            response = self.client.get("/api/public/ip/baribudos/assets")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("storage_path", response.text)
        self.assertIn("/api/public/assets/asset-1/file", response.text)
        self.assertNotIn("https://cdn.example/logo.png", response.text)

    def test_owner_admin_can_access_settings_without_client_supplied_role(self):
        self.set_principal("owner", "owner-1")
        with patch("studio_core.api.routes.settings.get_settings", return_value={"default_language": "pt-PT"}):
            response = self.client.get("/api/settings")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
