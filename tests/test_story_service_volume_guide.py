from __future__ import annotations

import unittest

from studio_core.services.story_service import generate_volume_guide


class VolumeGuideApprovalGateTests(unittest.TestCase):
    def test_single_story_never_generates_a_parent_volume_guide(self) -> None:
        result = generate_volume_guide({
            "project_title": "O Eco que Pedia Silêncio",
            "story": {
                "id": "bb-001",
                "title": "O Eco que Pedia Silêncio",
                "approved": True,
                "editorial_status": "approved",
                "approval_state": "approved",
                "pages": [{"pageNumber": 1, "text": "Texto de fixture"}],
            },
        })

        self.assertEqual(result["status"], "waiting_for_five_approved_stories")
        self.assertFalse(result["generated"])
        self.assertEqual(result["required_story_count"], 5)
        self.assertEqual(result["eligible_story_count"], 0)
        self.assertEqual(result["content"], "")

    def test_five_client_flagged_rows_still_do_not_authorize_a_guide(self) -> None:
        result = generate_volume_guide({
            "project_title": "Volume de fixture",
            "stories": [
                {
                    "id": f"fixture-{index}",
                    "approved": True,
                    "editorial_status": "approved",
                    "approval_state": "approved",
                }
                for index in range(1, 6)
            ],
        })

        self.assertEqual(result["status"], "waiting_for_five_approved_stories")
        self.assertFalse(result["generated"])
        self.assertEqual(result["eligible_story_count"], 0)
        self.assertEqual(result["content"], "")


if __name__ == "__main__":
    unittest.main()
