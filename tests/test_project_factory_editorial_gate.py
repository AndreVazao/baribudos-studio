from __future__ import annotations

import unittest
from unittest.mock import patch

from studio_core.services import project_factory_engine as factory


class ProjectFactoryEditorialGateTests(unittest.TestCase):
    def _runtime(self) -> dict:
        return {
            "slug": "baribudos",
            "name": "Baribudos",
            "default_language": "pt-PT",
            "metadata": {},
            "validation": {"ok": True},
        }

    def _story(self, **overrides) -> dict:
        story = {
            "id": "story-draft",
            "title": "Uma história",
            "language": "pt-PT",
            "saga_id": "baribudos",
            "raw_text": "Texto de uma história ainda em revisão.",
            "pages": [{"pageNumber": 1, "title": "Página 1", "text": "Texto de uma história."}],
            "editorial_status": "draft",
            "approved": False,
        }
        story.update(overrides)
        return story

    def test_newly_generated_draft_cannot_trigger_media_builders(self) -> None:
        story = self._story()
        with patch.object(factory, "_build_story_variants", return_value={"pt-PT": story}), patch.object(
            factory, "_build_cover_output", side_effect=AssertionError("cover must remain gated")
        ), patch.object(
            factory, "_build_ebook_outputs", side_effect=AssertionError("EPUB must remain gated")
        ), patch.object(
            factory, "_build_audiobook_outputs", side_effect=AssertionError("audio must remain gated")
        ), patch.object(
            factory, "_build_video_outputs", side_effect=AssertionError("video must remain gated")
        ), patch.object(
            factory, "generate_volume_guide", side_effect=AssertionError("guide must remain gated")
        ):
            result = factory.run_project_factory_engine(
                runtime=self._runtime(),
                project={"id": "project-1", "title": "Uma história", "language": "pt-PT"},
                payload={"createStory": True},
            )

        self.assertEqual(result["summary"]["editorial_status"], "needs_review")
        self.assertFalse(result["summary"]["media_gate_open"])
        self.assertTrue(result["summary"]["media_blocked"])
        self.assertEqual(result["language_variants"]["pt-PT"]["status"], "needs_review")
        self.assertEqual(result["ebook"], {})
        self.assertEqual(result["audiobook"], {})
        self.assertEqual(result["video"], {})
        self.assertIsNone(result["guide"])

    def test_project_approval_applies_only_to_base_language_without_version_state(self) -> None:
        story = self._story()
        story.pop("editorial_status")
        story.pop("approved")
        with patch.object(factory, "_build_cover_output", return_value=None), patch.object(
            factory, "_build_ebook_outputs", return_value={"pt-PT": {"format": "epub"}}
        ) as build_ebook, patch.object(
            factory, "_build_audiobook_outputs", return_value={"pt-PT": {"format": "wav"}}
        ), patch.object(
            factory, "_build_video_outputs", return_value={"pt-PT": {"format": "mp4"}}
        ), patch.object(factory, "generate_volume_guide", return_value={"title": "Guia"}):
            result = factory.run_project_factory_engine(
                runtime=self._runtime(),
                project={
                    "id": "project-3",
                    "title": "Uma história",
                    "language": "pt-PT",
                    "editorial_status": "approved",
                    "story": story,
                    "language_variants": {"pt-PT": story},
                },
                payload={"createStory": False},
            )
        self.assertTrue(result["summary"]["media_gate_open"])
        build_ebook.assert_called_once()

    def test_project_approval_does_not_approve_unreviewed_translation(self) -> None:
        source = self._story()
        source.pop("editorial_status")
        source.pop("approved")
        translation = {**source, "language": "en"}
        with patch.object(factory, "_build_cover_output", return_value=None), patch.object(
            factory, "_build_ebook_outputs", side_effect=AssertionError("unreviewed translation must block media")
        ), patch.object(factory, "_build_audiobook_outputs"), patch.object(
            factory, "_build_video_outputs"
        ), patch.object(factory, "generate_volume_guide"):
            result = factory.run_project_factory_engine(
                runtime=self._runtime(),
                project={
                    "id": "project-4",
                    "title": "Uma história",
                    "language": "pt-PT",
                    "editorial_status": "approved",
                    "story": source,
                    "language_variants": {"pt-PT": source, "en": translation},
                },
                payload={"createStory": False},
            )
        self.assertFalse(result["summary"]["media_gate_open"])
        self.assertEqual(result["summary"]["blocked_languages"], ["en"])

    def test_explicitly_approved_existing_story_opens_media_gate(self) -> None:
        story = self._story(editorial_status="approved", approved=True)
        with patch.object(factory, "_build_cover_output", return_value=None), patch.object(
            factory, "_build_ebook_outputs", return_value={"pt-PT": {"format": "epub"}}
        ) as build_ebook, patch.object(
            factory, "_build_audiobook_outputs", return_value={"pt-PT": {"format": "wav"}}
        ) as build_audio, patch.object(
            factory, "_build_video_outputs", return_value={"pt-PT": {"format": "mp4"}}
        ) as build_video, patch.object(
            factory, "generate_volume_guide", return_value={"title": "Guia"}
        ):
            result = factory.run_project_factory_engine(
                runtime=self._runtime(),
                project={
                    "id": "project-2",
                    "title": "Uma história",
                    "language": "pt-PT",
                    "story": story,
                    "language_variants": {"pt-PT": story},
                },
                payload={"createStory": False},
            )

        self.assertTrue(result["summary"]["media_gate_open"])
        self.assertFalse(result["summary"]["media_blocked"])
        build_ebook.assert_called_once()
        build_audio.assert_called_once()
        build_video.assert_called_once()
        self.assertEqual(result["language_variants"]["pt-PT"]["status"], "approved")


if __name__ == "__main__":
    unittest.main()
