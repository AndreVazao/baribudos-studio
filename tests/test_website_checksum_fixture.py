import hashlib
import json
import unittest
from pathlib import Path


class WebsiteChecksumFixtureTests(unittest.TestCase):
    def test_shared_fixture_matches_studio_checksum_algorithm(self):
        fixture_path = Path(__file__).parent / "fixtures" / "website-ingest-v1-checksum.json"
        envelope = json.loads(fixture_path.read_text(encoding="utf-8"))
        checksum = envelope.pop("checksum")

        canonical = json.dumps(envelope, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), checksum)


if __name__ == "__main__":
    unittest.main()
