from __future__ import annotations

import unittest

from studio_core.api.main import app


class ApiCorsPolicyTests(unittest.TestCase):
    def test_cors_is_explicit_and_does_not_enable_cookie_credentials(self):
        middleware = next(
            item for item in app.user_middleware
            if getattr(item.cls, "__name__", "") == "CORSMiddleware"
        )
        options = middleware.kwargs
        self.assertTrue(options.get("allow_origins"))
        self.assertNotIn("*", options.get("allow_origins", []))
        self.assertFalse(options.get("allow_credentials"))
        self.assertIn("Authorization", options.get("allow_headers", []))
        self.assertIn("Content-Type", options.get("allow_headers", []))
        self.assertNotIn("*", options.get("allow_methods", []))


if __name__ == "__main__":
    unittest.main()
