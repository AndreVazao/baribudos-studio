from __future__ import annotations

import math
import unittest

from studio_core.services.story_bundle_service import (
    EPISODE_MAX_SECONDS,
    EPISODE_MIN_SECONDS,
    VOLUME_MAX_SECONDS,
    VOLUME_MIN_SECONDS,
    _validate_episode_duration,
    _validate_volume_duration,
)


class CanonicalRuntimePolicyTests(unittest.TestCase):
    def test_episode_accepts_canonical_minimum_target_and_maximum(self) -> None:
        for duration in (EPISODE_MIN_SECONDS, 210.0, EPISODE_MAX_SECONDS):
            with self.subTest(duration=duration):
                _validate_episode_duration("episode-001", duration)

    def test_episode_rejects_short_long_and_non_finite_durations(self) -> None:
        for duration in (179.999, 240.001, 0.0, math.nan, math.inf):
            with self.subTest(duration=duration):
                with self.assertRaisesRegex(ValueError, "mini_series_duration_out_of_range"):
                    _validate_episode_duration("episode-001", duration)

    def test_volume_accepts_canonical_minimum_target_and_maximum(self) -> None:
        for duration in (VOLUME_MIN_SECONDS, 1050.0, VOLUME_MAX_SECONDS):
            with self.subTest(duration=duration):
                _validate_volume_duration(duration)

    def test_volume_rejects_short_long_and_non_finite_durations(self) -> None:
        for duration in (899.999, 1200.001, 0.0, math.nan, math.inf):
            with self.subTest(duration=duration):
                with self.assertRaisesRegex(ValueError, "volume_series_duration_out_of_range"):
                    _validate_volume_duration(duration)


if __name__ == "__main__":
    unittest.main()
