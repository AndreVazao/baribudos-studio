from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from studio_core.services import story_generation_engine as engine


class StoryGenerationFallbackTests(unittest.TestCase):
    def _runtime(self) -> dict:
        return {
            "slug": "baribudos",
            "name": "Baribudos",
            "default_language": "pt-PT",
            "main_characters": [{"name": "Tilo"}],
            "canons": {
                "characters": {"family": [{"name": "Tilo"}, {"name": "Magnus"}]},
                "pedagogical": {"approved_values": ["Paciência"]},
                "narrative": {"narrative_structure_standard": ["simple_introduction"]},
            },
            "resolved": {"series_name": "Baribudos", "mission": "Histórias seguras", "target_age": "4-10"},
            "validation": {"ok": True},
        }

    def test_template_fallback_is_marked_as_prototype_draft(self) -> None:
        with patch.dict(os.environ, {}, clear=True), patch.object(
            engine, "load_saga_runtime", return_value=self._runtime()
        ):
            story = engine.generate_canon_story({"saga_id": "baribudos", "language": "pt-PT"})
        self.assertEqual(story["generation_engine"], "deterministic_template_fallback")
        self.assertEqual(story["generation_status"], "prototype_needs_editorial_review")
        self.assertEqual(story["editorial_status"], "draft")
        self.assertFalse(story["approved"])

    def test_template_fallback_never_claims_nondefault_locale(self) -> None:
        with patch.dict(os.environ, {}, clear=True), patch.object(
            engine, "load_saga_runtime", return_value=self._runtime()
        ):
            with self.assertRaisesRegex(ValueError, "story_provider_required_for_nondefault_language"):
                engine.generate_canon_story({"saga_id": "baribudos", "language": "en"})


if __name__ == "__main__":
    unittest.main()
