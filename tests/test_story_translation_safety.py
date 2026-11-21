from __future__ import annotations

import unittest
from unittest.mock import patch

from studio_core.services import story_translation_service as translations


class StoryTranslationSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = {
            "id": "project-translation-test",
            "title": "História",
            "language": "pt-PT",
            "output_languages": ["pt-PT", "en"],
            "language_variants": {},
        }
        self.source = {
            "story_source_text": "Uma história original em português.",
            "story_source_language": "pt-PT",
        }

    def test_unsupported_target_language_fails_without_writing_fake_translation(self) -> None:
        with patch.object(translations, "_get_project", return_value=self.project), patch.object(
            translations, "get_story_source", return_value=self.source
        ), patch.object(translations, "update_json_item") as update:
            with self.assertRaisesRegex(ValueError, "translation_provider_not_configured_for_languages:en"):
                translations.generate_story_translations("project-translation-test", {"languages": ["en"]})
        update.assert_not_called()

    def test_source_language_copy_is_not_labelled_as_translation(self) -> None:
        with patch.object(translations, "_get_project", return_value=self.project), patch.object(
            translations, "get_story_source", return_value=self.source
        ), patch.object(
            translations, "update_json_item", side_effect=lambda _path, _id, updater: updater(self.project)
        ):
            result = translations.generate_story_translations(
                "project-translation-test", {"languages": ["pt-PT"]}
            )
        variant = result["language_variants"]["pt-PT"]
        self.assertEqual(variant["raw_text"], self.source["story_source_text"])
        self.assertEqual(variant["translation_status"], "source_language_copy")
        self.assertEqual(variant["translation_engine"], "identity-copy-no-translation")


if __name__ == "__main__":
    unittest.main()
