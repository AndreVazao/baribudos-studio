import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from scripts.export_studio_fastapi_manifest import (
    application_security_surface,
    build_manifest,
    dependency_tree,
    render_markdown,
)


def dependency(call, children=None, scopes=None):
    return SimpleNamespace(
        call=call,
        dependencies=children or [],
        security_scopes=scopes or [],
    )


def endpoint():
    pass


def auth_dependency():
    pass


class CORSMiddleware:
    pass


class TraceMiddleware:
    pass


class RuntimeRouteManifestTests(unittest.TestCase):
    def test_exports_each_method_and_marks_policy_unclassified(self):
        route = SimpleNamespace(
            path="/api/example",
            name="example",
            endpoint=endpoint,
            methods={"GET", "POST"},
            operation_id="example_operation",
            tags=["example"],
            dependant=dependency(endpoint, [dependency(auth_dependency, scopes=["editor"])]),
        )
        manifest = build_manifest([route])
        self.assertEqual(manifest["route_count"], 2)
        self.assertEqual([item["method"] for item in manifest["routes"]], ["GET", "POST"])
        for item in manifest["routes"]:
            self.assertEqual(item["policy_status"], "UNCLASSIFIED")
            self.assertEqual(item["default_access"], "DENY_BY_DEFAULT")
            self.assertFalse(item["runtime_protection_verified"])
            self.assertEqual(
                item["dependencies"]["dependencies"][0]["security_scopes"],
                ["editor"],
            )

    def test_dependency_tree_is_recursive_and_stable(self):
        tree = dependency_tree(
            dependency(endpoint, [dependency(auth_dependency, [dependency(endpoint)])])
        )
        self.assertEqual(tree["call"], f"{endpoint.__module__}.{endpoint.__qualname__}")
        self.assertEqual(len(tree["dependencies"]), 1)
        self.assertEqual(len(tree["dependencies"][0]["dependencies"]), 1)

    def test_duplicate_method_path_is_reported(self):
        route = SimpleNamespace(
            path="/api/duplicate",
            name="duplicate",
            endpoint=endpoint,
            methods={"GET"},
            operation_id=None,
            tags=[],
            dependant=dependency(endpoint),
        )
        manifest = build_manifest([route, route])
        self.assertEqual(manifest["duplicate_route_ids"], ["GET /api/duplicate"])

    def test_application_surface_captures_cors_and_global_dependencies_without_secrets(self):
        app = SimpleNamespace(
            router=SimpleNamespace(
                dependencies=[SimpleNamespace(dependency=auth_dependency, scopes=["owner"])]
            ),
            user_middleware=[
                SimpleNamespace(
                    cls=CORSMiddleware,
                    kwargs={
                        "allow_origins": ["*"],
                        "allow_credentials": True,
                        "allow_methods": ["*"],
                        "allow_headers": ["*"],
                    },
                ),
                SimpleNamespace(
                    cls=TraceMiddleware,
                    options={"secret": "must-not-appear", "enabled": True},
                ),
            ],
        )
        surface = application_security_surface(app)
        self.assertEqual(surface["global_dependency_count"], 1)
        self.assertEqual(surface["global_dependencies"][0]["call"], f"{auth_dependency.__module__}.{auth_dependency.__qualname__}")
        self.assertEqual(surface["global_dependencies"][0]["security_scopes"], ["owner"])
        self.assertEqual(surface["middleware_count"], 2)
        self.assertEqual(
            surface["middleware"][0]["cors_options"],
            {
                "allow_origins": ["*"],
                "allow_credentials": True,
                "allow_methods": ["*"],
                "allow_headers": ["*"],
            },
        )
        self.assertNotIn("must-not-appear", json.dumps(surface))
        self.assertNotIn("must-not-appear", render_markdown(build_manifest([], app=app)))

    def test_missing_application_is_explicitly_not_inspected(self):
        manifest = build_manifest([])
        self.assertEqual(
            manifest["application_security_surface"]["source"],
            "not supplied to build_manifest",
        )
        self.assertIn("Application object was not supplied", render_markdown(manifest))

    def test_manifest_includes_static_mounts_without_exporting_filesystem_paths(self):
        route = SimpleNamespace(
            path="/api/example",
            name="example",
            endpoint=endpoint,
            methods={"GET"},
            operation_id=None,
            tags=[],
            dependant=dependency(endpoint),
        )
        with tempfile.TemporaryDirectory() as directory:
            mount = Mount("/storage", app=StaticFiles(directory=directory), name="storage")
            app = SimpleNamespace(
                router=SimpleNamespace(dependencies=[]),
                user_middleware=[],
                routes=[route, mount],
            )
            manifest = build_manifest([route], app=app, app_routes=app.routes)
        surface = manifest["non_api_http_surface"]
        self.assertEqual(surface["non_api_route_count"], 1)
        self.assertEqual(surface["static_mount_count"], 1)
        static_record = surface["routes"][0]
        self.assertEqual(static_record["route_type"], "Mount")
        self.assertEqual(static_record["path"], "/storage")
        self.assertTrue(static_record["static_files"]["directory_configured"])
        self.assertTrue(static_record["static_files"]["directory_exists"])
        self.assertFalse(static_record["static_files"]["authorization_verified"])
        self.assertNotIn(directory, json.dumps(manifest))
        markdown = render_markdown(manifest)
        self.assertIn("StaticFiles mounts: **1**", markdown)
        self.assertIn("/storage", markdown)
        self.assertNotIn(directory, markdown)

    def test_real_application_inventories_storage_mount_when_root_exists(self):
        repository_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as temporary_root:
            temporary_path = Path(temporary_root)
            storage_root = temporary_path / "isolated-storage"
            storage_root.mkdir()
            json_output = temporary_path / "manifest.json"
            markdown_output = temporary_path / "manifest.md"

            environment = os.environ.copy()
            environment["BARIBUDOS_STORAGE_ROOT"] = str(storage_root)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "scripts.export_studio_fastapi_manifest",
                    "--json-output",
                    str(json_output),
                    "--markdown-output",
                    str(markdown_output),
                ],
                cwd=repository_root,
                env=environment,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )

            self.assertEqual(
                completed.returncode,
                0,
                msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
            )
            manifest = json.loads(json_output.read_text(encoding="utf-8"))
            storage_mounts = [
                item
                for item in manifest["non_api_http_surface"]["routes"]
                if item["path"] == "/storage"
            ]

            self.assertEqual(len(storage_mounts), 1)
            self.assertEqual(storage_mounts[0]["route_type"], "Mount")
            self.assertTrue(storage_mounts[0]["static_files"]["directory_exists"])
            self.assertFalse(storage_mounts[0]["static_files"]["authorization_verified"])
            self.assertNotIn(str(storage_root), json.dumps(manifest))
            self.assertNotIn(str(storage_root), markdown_output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
