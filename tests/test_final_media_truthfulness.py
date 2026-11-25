from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from studio_core.services import editorial_media_pipeline_service as media_pipeline
from studio_core.services import final_media_render_service as final_media


class FinalMediaTruthfulnessTests(unittest.TestCase):
    def test_legacy_final_video_renderer_fails_closed_instead_of_emitting_silent_placeholder(self) -> None:
        with patch.object(final_media, "_get_project", return_value={"id": "project-1"}):
            with self.assertRaisesRegex(ValueError, "final_character_animation_pipeline_not_implemented"):
                final_media.render_video_from_package("project-1")

    def test_legacy_epub_export_requires_explicit_editorial_approval(self) -> None:
        project = {
            "id": "project-2",
            "language": "pt-PT",
            "editorial_status": "draft",
            "story": {
                "pages": [{"pageNumber": 1, "text": "Texto."}],
                "editorial_status": "draft",
                "approved": False,
            },
        }
        with patch.object(final_media, "_get_project", return_value=project), patch.object(
            final_media, "build_epub"
        ) as build:
            with self.assertRaisesRegex(ValueError, "Aprovação editorial explícita"):
                final_media.export_epub_from_story("project-2", "pt-PT")
        build.assert_not_called()

    def test_approved_epub_uses_real_epub_builder(self) -> None:
        project = {
            "id": "project-3",
            "title": "Livro real",
            "language": "pt-PT",
            "editorial_status": "approved",
            "saga_slug": "baribudos",
            "story": {
                "pages": [{"pageNumber": 1, "text": "Texto aprovado."}],
            },
        }
        expected = {"format": "epub", "file_path": "/tmp/book.epub"}
        with patch.object(final_media, "_get_project", return_value=project), patch.object(
            final_media, "load_ip_runtime", return_value={"metadata": {"author_default": "Baribudos"}}
        ), patch.object(final_media, "build_epub", return_value=expected) as build, patch.object(
            final_media, "update_json_item", side_effect=lambda _path, _id, updater: updater(project)
        ):
            result = final_media.export_epub_from_story("project-3", "pt-PT")
        build.assert_called_once()
        self.assertEqual(result["ebook"], expected)

    def test_video_package_rejects_missing_illustrations_instead_of_creating_empty_files(self) -> None:
        project = {
            "id": "project-4",
            "series_storyboard": {
                "shots": [{"scene_number": 1, "shot_title": "Cena 1", "narration": "Texto"}]
            },
            "illustration_pipeline": {
                "frames": [{"page_number": 1, "image_path": ""}]
            },
        }
        with tempfile.TemporaryDirectory() as temp, patch.object(
            media_pipeline, "_get_project", return_value=project
        ), patch.object(media_pipeline, "resolve_storage_path", side_effect=lambda *parts: Path(temp).joinpath(*parts)):
            with self.assertRaisesRegex(ValueError, "video_package_requires_real_nonempty_illustration_assets"):
                media_pipeline.build_video_package_from_storyboard("project-4")


if __name__ == "__main__":
    unittest.main()
