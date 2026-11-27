from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from studio_core.api.routes import assets, project_media, public_assets, updater, voice_library, voice_preview
from studio_core.core.config import APP_CONFIG
from studio_core.services.auth_principal import AuthenticatedPrincipal, get_current_principal
from studio_core.services import project_route_auth


class PrivateMediaServingTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(project_media.router, prefix="/api")
        self.app.include_router(assets.router, prefix="/api")
        self.app.include_router(public_assets.router, prefix="/api")
        self.app.include_router(voice_preview.router, prefix="/api")
        self.app.include_router(voice_library.router, prefix="/api")
        self.app.include_router(updater.router, prefix="/api")
        self.client = TestClient(self.app)
        self.principal = AuthenticatedPrincipal(
            user_id="editor-1", name="Editor", role="editor"
        )
        self.app.dependency_overrides[get_current_principal] = lambda: self.principal

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def test_project_media_requires_authenticated_project_access(self):
        self.app.dependency_overrides.clear()
        response = self.client.get(
            "/api/projects/project-1/media",
            params={"path": "outputs/story.mp4"},
        )
        self.assertEqual(response.status_code, 401)

    def test_project_media_only_serves_paths_referenced_by_owned_project(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file_path = root / "story.mp4"
            file_path.write_bytes(b"private-video")
            project = {
                "id": "project-1",
                "created_by": "editor-1",
                "outputs": {"video": {"pt-PT": {"file_path": "outputs/story.mp4"}}},
            }
            with patch.object(project_route_auth, "read_json", return_value=[project]), patch.object(
                project_media, "read_json", return_value=[project]
            ), patch.object(project_media, "resolve_storage_path", return_value=file_path), patch.object(
                APP_CONFIG, "storage_root", root
            ):
                response = self.client.get(
                    "/api/projects/project-1/media",
                    params={"path": "outputs/story.mp4"},
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content, b"private-video")
                self.assertEqual(response.headers["cache-control"], "private, no-store")
                self.assertEqual(response.headers["x-content-type-options"], "nosniff")

                unreferenced = self.client.get(
                    "/api/projects/project-1/media",
                    params={"path": "data/users.json"},
                )
                self.assertEqual(unreferenced.status_code, 404)

    def test_project_media_rejects_traversal_and_unsupported_extensions(self):
        project = {
            "id": "project-1",
            "created_by": "editor-1",
            "outputs": {"video": {"file_path": "outputs/story.mp4"}},
        }
        with patch.object(project_route_auth, "read_json", return_value=[project]), patch.object(
            project_media, "read_json", return_value=[project]
        ):
            traversal = self.client.get(
                "/api/projects/project-1/media",
                params={"path": "../data/users.json"},
            )
            unsupported = self.client.get(
                "/api/projects/project-1/media",
                params={"path": "outputs/secret.json"},
            )
        self.assertEqual(traversal.status_code, 404)
        self.assertEqual(unsupported.status_code, 404)

    def test_voice_library_api_never_returns_physical_storage_paths(self):
        sample = {
            "id": "voice-1",
            "name": "Narrator",
            "file_name": "sample.wav",
            "file_path": "/srv/studio/storage/voice_library/voice-1/sample.wav",
            "owner_user_id": "editor-1",
        }
        with patch.object(voice_library, "list_voice_samples", return_value=[sample]):
            response = self.client.get("/api/voice-library")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["voices"][0]["file_name"], "sample.wav")
        self.assertNotIn("file_path", response.json()["voices"][0])

    def test_voice_library_is_scoped_to_uploader_and_preview_rejects_other_users_sample(self):
        own = {"id": "voice-own", "name": "Own", "owner_user_id": "editor-1", "file_path": "/private/own.wav"}
        foreign = {"id": "voice-foreign", "name": "Foreign", "owner_user_id": "other-user", "file_path": "/private/foreign.wav"}
        with patch.object(voice_library, "list_voice_samples", return_value=[own, foreign]):
            listed = self.client.get("/api/voice-library")
        self.assertEqual([item["id"] for item in listed.json()["voices"]], ["voice-own"])

        with patch.object(voice_library, "get_voice_sample", return_value=foreign):
            denied = self.client.get("/api/voice-library/voice-foreign")
        self.assertEqual(denied.status_code, 403)

        with patch.object(voice_preview, "get_voice_sample", return_value=foreign):
            denied_preview = self.client.post("/api/voice-preview", json={
                "voice_sample_id": "voice-foreign",
                "text": "Olá",
                "provider": "system_tts",
            })
        self.assertEqual(denied_preview.status_code, 403)

    def test_voice_preview_response_sanitizes_sample_paths(self):
        sample = {
            "id": "voice-own",
            "owner_user_id": "editor-1",
            "file_name": "sample.wav",
            "file_path": "/srv/studio/storage/voice_library/sample.wav",
        }
        generated = {
            "ok": True,
            "preview": {
                "id": "preview-1",
                "file_url": "/api/voice-preview/preview-1/file",
                "file_name": "voice_preview.wav",
                "speaker_wav": "/srv/studio/storage/voice_library/sample.wav",
            },
            "voice_sample": sample,
        }
        with patch.object(voice_preview, "get_voice_sample", return_value=sample), patch.object(
            voice_preview, "generate_voice_preview", return_value=generated
        ) as generate:
            response = self.client.post("/api/voice-preview", json={
                "voice_sample_id": "voice-own",
                "text": "Olá",
            })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("file_path", response.json()["voice_sample"])
        self.assertNotIn("speaker_wav", response.json()["preview"])
        generate.assert_called_once()

    def test_voice_preview_uses_authenticated_opaque_id_route(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "voice-preview.wav"
            file_path.write_bytes(b"voice-preview")
            preview_id = "e8c3c8f5-7e5e-4e7e-9d2c-85bb0acac145"
            with patch.object(voice_preview, "resolve_storage_path", return_value=file_path), patch.object(
                voice_preview,
                "_read_preview_metadata",
                return_value={"owner_user_id": "editor-1", "created_at": time.time()},
            ):
                response = self.client.get(f"/api/voice-preview/{preview_id}/file")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"voice-preview")
            self.assertEqual(response.headers["cache-control"], "private, no-store")

            self.principal = AuthenticatedPrincipal(
                user_id="other-user", name="Other", role="editor"
            )
            with patch.object(voice_preview, "resolve_storage_path", return_value=file_path), patch.object(
                voice_preview,
                "_read_preview_metadata",
                return_value={"owner_user_id": "editor-1", "created_at": time.time()},
            ):
                foreign = self.client.get(f"/api/voice-preview/{preview_id}/file")
            self.assertEqual(foreign.status_code, 404)

    def test_updater_download_is_admin_only_and_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "installer.exe"
            file_path.write_bytes(b"installer")
            self.principal = AuthenticatedPrincipal(
                user_id="admin-1", name="Admin", role="admin"
            )
            with patch.object(updater, "resolve_storage_path", return_value=file_path):
                traversal = self.client.get("/api/updater/files/..%5Cusers.json")
                self.assertEqual(traversal.status_code, 404)
                allowed = self.client.get("/api/updater/files/installer.exe")
            self.assertEqual(allowed.status_code, 200)
            self.assertEqual(allowed.content, b"installer")
            self.assertEqual(allowed.headers["cache-control"], "private, no-store")

    def test_private_asset_file_requires_project_or_ip_access(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "private-cover.png"
            file_path.write_bytes(b"private-cover")
            project_asset = {
                "asset_id": "asset-project",
                "project_id": "project-1",
                "ip_slug": "saga-one",
                "storage_path": "editorial/assets/saga-one/cover/private-cover.png",
                "status": "draft",
            }
            with patch.object(assets, "get_asset_by_id", return_value=project_asset), patch.object(
                assets, "assert_project_access"
            ) as authorize_project, patch.object(
                assets, "assert_ip_read_access"
            ) as authorize_ip, patch.object(
                assets, "resolve_storage_path", return_value=file_path
            ):
                allowed = self.client.get("/api/assets/asset-project/file")
            self.assertEqual(allowed.status_code, 200)
            self.assertEqual(allowed.content, b"private-cover")
            authorize_project.assert_called_once_with("project-1", self.principal)
            authorize_ip.assert_called_once_with("saga-one", self.principal)
            self.assertEqual(allowed.headers["cache-control"], "private, no-store")

            with patch.object(assets, "get_asset_by_id", return_value=project_asset), patch.object(
                assets, "assert_project_access", side_effect=HTTPException(
                    status_code=403, detail="foreign project"
                )
            ):
                denied = self.client.get("/api/assets/asset-project/file")
            self.assertEqual(denied.status_code, 403)

    def test_asset_upload_cannot_self_publish_and_editor_cannot_publish(self):
        with patch.object(assets, "assert_project_access"), patch.object(
            assets, "assert_ip_edit_access"
        ), patch.object(
            assets, "register_asset",
            return_value={"asset_id": "asset-1", "status": "draft", "url": ""},
        ) as register:
            response = self.client.post("/api/assets/register", json={
                "asset_id": "asset-1",
                "project_id": "project-1",
                "ip_slug": "saga-one",
                "status": "published",
                "url": "/storage/private.png",
            })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(register.call_args.args[0]["status"], "draft")
        self.assertEqual(register.call_args.args[0]["url"], "")
        self.assertEqual(response.json()["asset"]["url"], "")
        self.assertNotIn("storage_path", response.json()["asset"])

        denied = self.client.post("/api/assets/asset-1/publish")
        self.assertEqual(denied.status_code, 403)

        self.principal = AuthenticatedPrincipal(
            user_id="admin-1", name="Admin", role="admin"
        )
        with patch.object(
            assets, "publish_asset",
            return_value={"asset_id": "asset-1", "status": "published", "url": ""},
        ), patch.object(
            assets, "update_asset",
            return_value={"asset_id": "asset-1", "status": "published", "url": ""},
        ):
            allowed = self.client.post("/api/assets/asset-1/publish")
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(allowed.json()["asset"]["url"], "/api/public/assets/asset-1/file")

    def test_asset_upload_collision_does_not_delete_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            existing = Path(directory) / "existing.png"
            existing.write_bytes(b"preexisting-data")
            self.client.raise_server_exceptions = False
            with patch.object(assets, "_build_asset_storage_path", return_value=(existing, "existing.png")), patch.object(
                assets, "assert_project_access"
            ), patch.object(assets, "assert_ip_edit_access"):
                response = self.client.post(
                    "/api/assets/upload",
                    files={"file": ("cover.png", b"new-upload", "image/png")},
                    data={"ip_slug": "saga-one", "asset_type": "cover", "context": "test"},
                )
            self.assertEqual(response.status_code, 500)
            self.assertEqual(existing.read_bytes(), b"preexisting-data")

    def test_public_manifest_strips_physical_storage_paths(self):
        manifest = public_assets._sanitize_public_manifest({
            "project": {"file_path": "/srv/studio/storage/private.mp4"},
            "assets": [{
                "asset_id": "asset-live",
                "status": "published",
                "storage_path": "covers/cover.png",
                "url": "/storage/covers/cover.png",
            }],
        })
        self.assertNotIn("file_path", manifest["project"])
        self.assertNotIn("storage_path", manifest["assets"][0])
        self.assertEqual(manifest["assets"][0]["url"], "/api/public/assets/asset-live/file")

    def test_public_asset_endpoint_only_serves_published_registry_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file_path = root / "cover.png"
            file_path.write_bytes(b"published-cover")
            draft = {"asset_id": "asset-draft", "status": "draft", "storage_path": "covers/cover.png"}
            published = {"asset_id": "asset-live", "status": "published", "storage_path": "covers/cover.png"}
            with patch.object(public_assets, "get_asset_by_id", return_value=draft):
                denied = self.client.get("/api/public/assets/asset-draft/file")
            self.assertEqual(denied.status_code, 404)

            with patch.object(public_assets, "get_asset_by_id", return_value=published), patch.object(
                public_assets, "resolve_storage_path", return_value=file_path
            ), patch.object(APP_CONFIG, "storage_root", root):
                allowed = self.client.get("/api/public/assets/asset-live/file")
            self.assertEqual(allowed.status_code, 200)
            self.assertEqual(allowed.content, b"published-cover")
            self.assertIn("public", allowed.headers["cache-control"])


if __name__ == "__main__":
    unittest.main()
