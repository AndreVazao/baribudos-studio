from __future__ import annotations

import unittest

from studio_core.services.secret_control_service import _build_vault_response


class SecretVaultResponseSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.vault = {
            "id": "vault-1",
            "name": "test",
            "rows": [
                {
                    "kind": "entry",
                    "key": "PAYMENT_TOKEN",
                    "value": "super-secret-token-value",
                    "masked_value": "su*******************ue",
                    "quote_style": "none",
                },
                {"kind": "comment", "raw": "# local configuration"},
                {"kind": "blank", "raw": ""},
            ],
        }

    def test_default_response_never_serializes_secret_value(self) -> None:
        response = _build_vault_response(self.vault)

        self.assertEqual(response["rows"][0]["value"], "")
        self.assertTrue(response["rows"][0]["masked_value"].startswith("su"))
        self.assertTrue(response["rows"][0]["masked_value"].endswith("ue"))
        self.assertNotIn("super-secret-token-value", response["rows"][0]["masked_value"])
        self.assertIn("PAYMENT_TOKEN=", response["rendered_env"])
        self.assertNotIn("super-secret-token-value", response["rendered_env"])
        self.assertNotIn("super-secret-token-value", repr(response))

    def test_explicit_reveal_response_keeps_value(self) -> None:
        response = _build_vault_response(self.vault, include_values=True)

        self.assertEqual(response["rows"][0]["value"], "super-secret-token-value")
        self.assertIn("PAYMENT_TOKEN=super-secret-token-value", response["rendered_env"])

    def test_source_vault_is_not_mutated(self) -> None:
        _build_vault_response(self.vault)
        self.assertEqual(self.vault["rows"][0]["value"], "super-secret-token-value")


if __name__ == "__main__":
    unittest.main()
