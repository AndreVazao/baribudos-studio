from __future__ import annotations

import unittest

from scripts.audit_studio_routes import scan_source


class RouteAuditTests(unittest.TestCase):
    def test_detects_client_supplied_identity_without_local_auth_signal(self) -> None:
        source = """
from fastapi import APIRouter
router = APIRouter()

@router.get("/projects")
def list_projects(user_role: str, user_name: str):
    return {"role": user_role, "name": user_name}
"""
        [route] = scan_source(source, "projects.py")
        self.assertEqual(route["method"], "GET")
        self.assertEqual(route["path"], "/projects")
        self.assertFalse(route["auth_signal"])
        self.assertEqual(route["client_identity_inputs"], ["user_name", "user_role"])

    def test_detects_router_level_auth_dependency(self) -> None:
        source = """
from fastapi import APIRouter, Depends
router = APIRouter(dependencies=[Depends(require_admin)])

@router.post("/settings")
def update_settings():
    return {"ok": True}
"""
        [route] = scan_source(source, "settings.py")
        self.assertTrue(route["auth_signal"])
        self.assertIn("require_admin", " ".join(route["auth_evidence"]))

    def test_flags_operational_routes_and_destructive_signals(self) -> None:
        source = """
from fastapi import APIRouter
import subprocess
router = APIRouter()

@router.post("/deploy")
def deploy():
    subprocess.run(["deploy-tool"])
"""
        [route] = scan_source(source, "deploy_control.py")
        self.assertTrue(route["sensitive_surface"])
        self.assertTrue(route["dangerous_operation_signals"])


if __name__ == "__main__":
    unittest.main()
