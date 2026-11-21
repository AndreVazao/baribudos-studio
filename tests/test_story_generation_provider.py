from __future__ import annotations

import json
import os
import unittest
from unittest.mock import patch

from studio_core.services import story_generation_provider as provider


class StoryGenerationProviderTests(unittest.TestCase):
    def _story(self) -> dict:
        return {
            "title": "A semente paciente",
            "synopsis": "Uma semente ensina os amigos a respeitar o tempo da natureza.",
            "target_age": "4-10",
            "value_theme": "Paciência",
            "supporting_value": "Cuidado da natureza",
            "characters": ["Roko", "Mila", "Tilo", "Luma", "Magnus"],
            "protagonist": "Roko",
            "support_character": "Luma",
            "scenes": [{"key": "opening", "text": "Roko encontra uma semente."}],
            "pages": [{"title": "A semente", "text": "Roko encontrou uma semente.\nMila aproximou-se."}],
            "raw_text": "Roko encontrou uma semente. Mila aproximou-se.",
            "final_phrase": "Cada coisa tem o seu tempo.",
        }

    def test_provider_configuration_requires_provider_key_and_model(self) -> None:
        with patch.dict(os.environ, {
            "BARIBUDOS_STORY_PROVIDER": "openai_compatible",
            "BARIBUDOS_STORY_API_KEY": "test-key",
            "BARIBUDOS_STORY_MODEL": "test-model",
        }, clear=True):
            self.assertTrue(provider.is_story_provider_configured())

        with patch.dict(os.environ, {"BARIBUDOS_STORY_PROVIDER": "openai"}, clear=True):
            self.assertFalse(provider.is_story_provider_configured())

    def test_provider_returns_structured_draft_and_usage_metadata(self) -> None:
        response = {
            "choices": [{"message": {"content": json.dumps(self._story(), ensure_ascii=False)}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300},
        }
        runtime = {
            "slug": "baribudos",
            "name": "Baribudos",
            "default_language": "pt-PT",
            "canons": {"pedagogical": {"approved_values": ["Paciência"]}},
            "resolved": {"target_age": "4-10"},
        }
        with patch.dict(os.environ, {
            "BARIBUDOS_STORY_PROVIDER": "openai_compatible",
            "BARIBUDOS_STORY_API_KEY": "test-key",
            "BARIBUDOS_STORY_MODEL": "test-model",
        }, clear=True), patch.object(provider, "_request_json", return_value=response):
            result = provider.generate_story_with_provider(
                payload={"language": "pt-PT", "title": "A semente"},
                runtime=runtime,
            )

        self.assertEqual(result["language"], "pt-PT")
        self.assertEqual(result["generation_status"], "generated_needs_review")
        self.assertEqual(result["provider_status"], "generated_needs_review")
        self.assertEqual(result["generation_usage"]["total_tokens"], 300)
        self.assertEqual(result["pages"][0]["pageNumber"], 1)

    def test_provider_rejects_pages_with_more_than_five_nonempty_lines(self) -> None:
        story = self._story()
        story["pages"][0]["text"] = "um\ndois\ntres\nquatro\ncinco\nseis"
        with self.assertRaisesRegex(provider.StoryProviderError, "page_exceeds_five_lines"):
            provider._validate_story(story, language="pt-PT")

    def test_provider_rejects_missing_required_story_fields(self) -> None:
        story = self._story()
        story["final_phrase"] = ""
        with self.assertRaisesRegex(provider.StoryProviderError, "missing_field:final_phrase"):
            provider._validate_story(story, language="pt-PT")

    def test_provider_rejects_noncanonical_characters(self) -> None:
        story = self._story()
        story["characters"] = ["Roko", "Personagem Inventada"]
        with self.assertRaisesRegex(provider.StoryProviderError, "unknown_canonical_character"):
            provider._validate_story(
                story,
                language="pt-PT",
                allowed_characters={"roko", "mila", "tilo", "luma", "magnus"},
            )

    def test_provider_rejects_values_outside_approved_pedagogical_canon(self) -> None:
        story = self._story()
        story["value_theme"] = "Tema não aprovado"
        with self.assertRaisesRegex(provider.StoryProviderError, "value_not_in_approved_canon"):
            provider._validate_story(
                story,
                language="pt-PT",
                approved_values={"paciência", "partilha"},
            )

    def test_provider_failure_does_not_silently_fall_back(self) -> None:
        runtime = {"slug": "baribudos", "resolved": {}, "canons": {}}
        with patch.dict(os.environ, {
            "BARIBUDOS_STORY_PROVIDER": "openai_compatible",
            "BARIBUDOS_STORY_API_KEY": "test-key",
            "BARIBUDOS_STORY_MODEL": "test-model",
            "BARIBUDOS_STORY_RETRIES": "0",
        }, clear=True), patch.object(
            provider, "_request_json", side_effect=provider.StoryProviderError("provider unavailable")
        ):
            with self.assertRaisesRegex(provider.StoryProviderError, "story_provider_failed"):
                provider.generate_story_with_provider(payload={"language": "pt-PT"}, runtime=runtime)


if __name__ == "__main__":
    unittest.main()
