import unittest

from studio_core.services.auth_credentials import hash_pin, verify_pin, is_hashed_pin


class AuthCredentialTests(unittest.TestCase):
    def test_hash_is_salted_and_never_contains_plain_pin(self):
        first = hash_pin("1234")
        second = hash_pin("1234")
        self.assertNotEqual(first, second)
        self.assertNotIn("1234", first)
        self.assertTrue(is_hashed_pin(first))
        self.assertTrue(verify_pin("1234", first))
        self.assertFalse(verify_pin("0000", first))

    def test_legacy_plaintext_verifies_for_migration(self):
        self.assertTrue(verify_pin("legacy-pin", "legacy-pin"))
        self.assertFalse(verify_pin("wrong-pin", "legacy-pin"))
        self.assertFalse(is_hashed_pin("legacy-pin"))

    def test_malformed_hash_fails_closed(self):
        self.assertFalse(verify_pin("1234", "pbkdf2_sha256$broken"))
        self.assertFalse(verify_pin("1234", "pbkdf2_sha256$1$00$00"))


if __name__ == "__main__":
    unittest.main()
