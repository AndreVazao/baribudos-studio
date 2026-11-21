from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi import HTTPException

from studio_core.api.routes import audiobooks, ebooks, videos


class DirectMediaEditorialGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = {
            "id": "project-draft",
            "title": "História em revisão",
            "language": "pt-PT",
            "editorial_status": "draft",
            "story": {
                "id": "story-draft",
                "title": "História em revisão",
                "raw_text": "Texto ainda não aprovado.",
                "editorial_status": "draft",
                "approved": False,
            },
            "language_variants": {},
        }

    def test_direct_epub_export_rejects_unapproved_story(self) -> None:
        with patch.object(ebooks, "_get_project", return_value=self.project), patch.object(
            ebooks, "load_ip_runtime", return_value={"metadata": {}}
        ), patch.object(ebooks, "build_epub") as build:
            with self.assertRaises(HTTPException) as raised:
                ebooks.export_ebook("project-draft", {"language": "pt-PT"})
        self.assertEqual(raised.exception.status_code, 409)
        build.assert_not_called()

    def test_direct_audiobook_export_rejects_unapproved_story(self) -> None:
        with patch.object(audiobooks, "_get_project", return_value=self.project), patch.object(
            audiobooks, "build_audiobook"
        ) as build:
            with self.assertRaises(HTTPException) as raised:
                audiobooks.export_audiobook("project-draft", {"language": "pt-PT"})
        self.assertEqual(raised.exception.status_code, 409)
        build.assert_not_called()

    def test_direct_miniseries_export_rejects_unapproved_story(self) -> None:
        with patch.object(videos, "_get_project", return_value=self.project), patch.object(
            videos, "build_series_episode"
        ) as build:
            with self.assertRaises(HTTPException) as raised:
                videos.export_video("project-draft", {"language": "pt-PT"})
        self.assertEqual(raised.exception.status_code, 409)
        build.assert_not_called()


if __name__ == "__main__":
    unittest.main()
