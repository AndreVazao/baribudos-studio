from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from studio_core.api.routes import (
    audio_cast, audio_cast_preview, editorial_media_pipeline, final_media_render,
    illustration_pipeline, illustration_provider, voice_library, voice_preview, voice_profiles,
)
from studio_core.services.auth_principal import AuthenticatedPrincipal, get_current_principal


class AudioIllustrationProductionRBACTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        modules = (
            audio_cast, audio_cast_preview, editorial_media_pipeline, final_media_render,
            illustration_pipeline, illustration_provider, voice_library, voice_preview, voice_profiles,
        )
        for module in modules:
            self.app.include_router(module.router, prefix="/api")
        self.client = TestClient(self.app)

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def set_principal(self, role: str, user_id: str = "editor-1"):
        self.app.dependency_overrides[get_current_principal] = lambda: AuthenticatedPrincipal(
            user_id=user_id, name="RBAC Test", role=role
        )

    def test_voice_and_project_media_routes_require_authentication(self):
        checks = (
            self.client.get("/api/voice-library"),
            self.client.post("/api/voice-preview", json={}),
            self.client.get("/api/voice-profiles"),
            self.client.get("/api/audio-cast/project-1"),
            self.client.post("/api/audio-cast-preview/project-1", json={}),
            self.client.post("/api/editorial-media/build-video-package/project-1"),
            self.client.post("/api/final-media/render-video/project-1"),
            self.client.get("/api/illustration-pipeline/project-1"),
            self.client.post("/api/illustration-provider/run/project-1", json={}),
        )
        self.assertTrue(all(response.status_code == 401 for response in checks))

    def test_viewer_is_denied_from_voice_and_project_media_routes(self):
        self.set_principal("viewer")
        checks = (
            self.client.get("/api/voice-library"),
            self.client.post("/api/voice-preview", json={}),
            self.client.get("/api/voice-profiles"),
            self.client.get("/api/audio-cast/project-1"),
            self.client.post("/api/editorial-media/build-video-package/project-1"),
            self.client.post("/api/final-media/render-video/project-1"),
            self.client.get("/api/illustration-pipeline/project-1"),
        )
        self.assertTrue(all(response.status_code == 403 for response in checks))

    def test_editor_can_access_own_audio_cast_project(self):
        self.set_principal("editor", "editor-1")
        with patch("studio_core.services.project_route_auth.read_json", return_value=[
            {"id": "project-1", "created_by": "editor-1"}
        ]), patch.object(audio_cast, "get_audio_cast", return_value={"cast": []}), patch.object(
            audio_cast, "list_project_character_names", return_value=[]
        ):
            response = self.client.get("/api/audio-cast/project-1")
        self.assertEqual(response.status_code, 200)

    def test_editor_cannot_access_another_users_media_project(self):
        self.set_principal("creator", "creator-1")
        with patch("studio_core.services.project_route_auth.read_json", return_value=[
            {"id": "project-1", "created_by": "another-user"}
        ]):
            response = self.client.post("/api/illustration-provider/run/project-1", json={})
        self.assertEqual(response.status_code, 403)

    def test_project_route_returns_not_found_for_missing_project(self):
        self.set_principal("editor", "editor-1")
        with patch("studio_core.services.project_route_auth.read_json", return_value=[]):
            response = self.client.get("/api/audio-cast/project-missing")
        self.assertEqual(response.status_code, 404)

    def test_owner_can_list_all_illustration_runs(self):
        self.set_principal("owner")
        with patch.object(illustration_pipeline, "list_illustration_runs", return_value=[]):
            response = self.client.get("/api/illustration-pipeline")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
