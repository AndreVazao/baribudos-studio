from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from studio_core.api.routes import assets, audiobooks
from studio_core.services.auth_principal import AuthenticatedPrincipal, get_current_principal


class MediaUploadAndAudiobookOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(assets.router, prefix="/api")
        self.app.include_router(audiobooks.router, prefix="/api")
        self.client = TestClient(self.app)
        self.app.dependency_overrides[get_current_principal] = lambda: AuthenticatedPrincipal(
            user_id="user-a", name="Test", role="editor"
        )

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def test_asset_upload_rejects_oversized_stream_and_removes_partial_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "asset.bin"
            with patch.object(assets, "MAX_ASSET_UPLOAD_BYTES", 10), patch.object(
                assets, "_assert_asset_access"
            ), patch.object(
                assets, "_build_asset_storage_path", return_value=(destination, "asset.bin")
            ):
                response = self.client.post(
                    "/api/assets/upload",
                    data={"ip_slug": "test", "asset_type": "cover", "context": "story"},
                    files={"file": ("asset.png", b"x" * 11, "image/png")},
                )
            self.assertEqual(response.status_code, 413)
            self.assertFalse(destination.exists())

    def test_audiobook_export_rejects_another_users_voice_sample(self):
        project = {"id": "project-1", "created_by": "user-a", "story": {"pages": [{"text": "Olá"}]}}
        sample = {"id": "voice-1", "owner_user_id": "user-b", "file_path": "/private/voice.wav"}
        with patch.object(audiobooks, "_get_project", return_value=project), patch.object(
            audiobooks, "require_project_access"
        ), patch.object(audiobooks, "get_voice_sample", return_value=sample), patch.object(
            audiobooks, "build_audiobook"
        ) as build:
            response = self.client.post(
                "/api/audiobooks/export/project-1",
                json={"voice_sample_id": "voice-1"},
            )
        self.assertEqual(response.status_code, 404)
        build.assert_not_called()

    def test_audiobook_response_never_exposes_voice_storage_path(self):
        project = {"id": "project-1", "created_by": "user-a", "story": {"pages": [{"text": "Olá"}]}}
        sample = {
            "id": "voice-1", "owner_user_id": "user-a", "name": "Minha voz",
            "file_path": "/private/voice.wav", "source_path": "/private/source.wav",
        }
        output = {"file_url": "/api/assets/audio-1/file", "file_path": "/private/book.wav"}
        with patch.object(audiobooks, "_get_project", return_value=project), patch.object(
            audiobooks, "require_project_access"
        ), patch.object(audiobooks, "get_voice_sample", return_value=sample), patch.object(
            audiobooks, "build_audiobook", return_value={"pt-PT": output}
        ), patch.object(audiobooks, "update_json_item"):
            response = self.client.post(
                "/api/audiobooks/export/project-1",
                json={"voice_sample_id": "voice-1"},
            )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertNotIn("file_path", body["voice_sample"])
        self.assertNotIn("source_path", body["voice_sample"])
        self.assertNotIn("file_path", body["audiobook"])


if __name__ == "__main__":
    unittest.main()
