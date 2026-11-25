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

    def test_default_response_redacts_raw_comment_and_unknown_persisted_fields(self) -> None:
        vault = {
            **self.vault,
            "legacy_raw_text": "TOP_LEVEL_SECRET_MUST_NOT_LEAK",
            "rows": [
                {"kind": "comment", "raw": "# API_TOKEN=COMMENT_SECRET_MUST_NOT_LEAK"},
                {
                    "kind": "raw",
                    "raw": "UNPARSED_SECRET_MUST_NOT_LEAK",
                    "unexpected_secret_field": "ROW_FIELD_SECRET_MUST_NOT_LEAK",
                },
                {
                    "kind": "entry",
                    "key": "PAYMENT_TOKEN",
                    "value": "super-secret-token-value",
                    "raw": "PAYMENT_TOKEN=super-secret-token-value",
                },
            ],
        }

        response = _build_vault_response(vault)
        serialized = repr(response)

        self.assertEqual(response["rows"][0]["raw"], "")
        self.assertEqual(response["rows"][1]["raw"], "")
        self.assertNotIn("legacy_raw_text", response)
        self.assertNotIn("TOP_LEVEL_SECRET_MUST_NOT_LEAK", serialized)
        self.assertNotIn("COMMENT_SECRET_MUST_NOT_LEAK", serialized)
        self.assertNotIn("UNPARSED_SECRET_MUST_NOT_LEAK", serialized)
        self.assertNotIn("unexpected_secret_field", serialized)
        self.assertNotIn("ROW_FIELD_SECRET_MUST_NOT_LEAK", serialized)
        self.assertNotIn("super-secret-token-value", serialized)

    def test_source_vault_is_not_mutated(self) -> None:
        _build_vault_response(self.vault)
        self.assertEqual(self.vault["rows"][0]["value"], "super-secret-token-value")


if __name__ == "__main__":
    unittest.main()
