from __future__ import annotations

import math
import unittest

from studio_core.services.story_bundle_service import (
    _duration_recommendation,
    _validate_episode_duration,
    _validate_volume_duration,
)


class AdaptiveRuntimePolicyTests(unittest.TestCase):
    def test_episode_duration_window_is_advisory(self) -> None:
        recommendation = {"min_seconds": 270.0, "max_seconds": 360.0}
        self.assertEqual(_validate_episode_duration("episode-short", 180.0, recommendation), [
            "below_advisory_duration_window:episode-short:180.000<270.000"
        ])
        self.assertEqual(_validate_episode_duration("episode-long", 420.0, recommendation), [
            "above_advisory_duration_window:episode-long:420.000>360.000"
        ])
        self.assertEqual(_validate_episode_duration("episode-target", 300.0, recommendation), [])

    def test_episode_without_ip_specific_recommendation_has_no_warning(self) -> None:
        self.assertEqual(_validate_episode_duration("episode-001", 120.0), [])

    def test_invalid_episode_media_is_still_rejected(self) -> None:
        for duration in (0.0, -1.0, math.nan, math.inf, -math.inf):
            with self.subTest(duration=duration):
                with self.assertRaisesRegex(ValueError, "mini_series_duration_invalid"):
                    _validate_episode_duration("episode-001", duration)

    def test_compilation_has_no_universal_minimum_or_maximum(self) -> None:
        for duration in (0.01, 60.0, 1500.0, 7200.0):
            with self.subTest(duration=duration):
                _validate_volume_duration(duration)

    def test_invalid_compilation_media_is_rejected(self) -> None:
        for duration in (0.0, -1.0, math.nan, math.inf):
            with self.subTest(duration=duration):
                with self.assertRaisesRegex(ValueError, "volume_series_duration_invalid"):
                    _validate_volume_duration(duration)

    def test_recommendations_are_read_from_format_specific_ip_policy(self) -> None:
        item = {
            "duration_recommendations": {
                "miniseries": {
                    "recommended_min_seconds": 270,
                    "recommended_max_seconds": 360,
                }
            }
        }
        self.assertEqual(
            _duration_recommendation(item, "miniseries"),
            {"min_seconds": 270.0, "max_seconds": 360.0},
        )
        self.assertEqual(_duration_recommendation(item, "audiobook"), {})


if __name__ == "__main__":
    unittest.main()
