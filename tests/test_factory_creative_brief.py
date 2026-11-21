from __future__ import annotations

import unittest
from unittest.mock import patch

from studio_core.services import factory_service


class FactoryCreativeBriefTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = {
            "id": "project-creative-brief",
            "title": "A aventura da floresta",
            "language": "pt-PT",
            "saga_slug": "baribudos",
            "story": {},
        }

    def test_generation_without_source_requires_configured_provider_and_brief(self) -> None:
        with patch.object(factory_service, "_get_project", return_value=self.project), patch.object(
            factory_service, "get_story_source_gate", return_value={"story_source_gate": {"ready_for_text_first_pipeline": False}}
        ), patch.object(factory_service, "get_story_source", return_value={}), patch.object(
            factory_service, "is_story_provider_configured", return_value=False
        ):
            with self.assertRaisesRegex(ValueError, "story_generation_requires_locked_source"):
                factory_service.run_factory("project-creative-brief", {"createStory": True, "creative_brief": "Uma aventura."})

    def test_configured_provider_accepts_creative_brief_without_pasted_source(self) -> None:
        runtime = {"slug": "baribudos", "validation": {"ok": True}}
        engine_result = {
            "story": {"id": "story-1", "editorial_status": "draft"},
            "language_variants": {"pt-PT": {"status": "needs_review"}},
            "cover": None,
            "ebook": {},
            "audiobook": {},
            "video": {},
            "guide": None,
            "summary": {"media_blocked": True},
        }
        with patch.object(factory_service, "_get_project", return_value=self.project), patch.object(
            factory_service, "get_story_source_gate", return_value={"story_source_gate": {"ready_for_text_first_pipeline": False}}
        ), patch.object(factory_service, "get_story_source", return_value={}), patch.object(
            factory_service, "is_story_provider_configured", return_value=True
        ), patch.object(factory_service, "load_saga_runtime", return_value=runtime), patch.object(
            factory_service, "run_project_factory_engine", return_value=engine_result
        ) as run_engine, patch.object(factory_service, "update_json_item", side_effect=lambda _path, _id, updater: updater(self.project)):
            result = factory_service.run_factory(
                "project-creative-brief",
                {"createStory": True, "creative_brief": "Uma semente ensina paciência.", "value_theme": "Paciência"},
            )

        engine_payload = run_engine.call_args.kwargs["payload"]
        self.assertEqual(engine_payload["creative_brief"], "Uma semente ensina paciência.")
        self.assertEqual(result["story"]["editorial_status"], "draft")
        self.assertTrue(result["summary"]["media_blocked"])


if __name__ == "__main__":
    unittest.main()
