import unittest
from types import SimpleNamespace

from scripts.export_studio_fastapi_manifest import build_manifest, dependency_tree


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


if __name__ == "__main__":
    unittest.main()
