from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from studio_core.services import audiobook_service, ebook_service, video_service
from studio_core.services.story_bundle_service import (
    build_five_story_bundle,
    select_complete_story_groups,
)


@unittest.skipUnless(
    shutil.which("ffmpeg") and shutil.which("ffprobe") and (shutil.which("espeak-ng") or shutil.which("espeak")),
    "FFmpeg, FFprobe and eSpeak are required for cloud production integration",
)
class CloudStoryProductionIntegrationTests(unittest.TestCase):
    def test_one_story_generates_epub_real_audiobook_and_miniseries_then_five_story_bundle(self) -> None:
        with tempfile.TemporaryDirectory(prefix="baribudos-production-cloud-") as temp:
            root = Path(temp)
            storage = root / "storage"
            project_id = "cloud-production-story-001"
            story = {
                "id": "story-001",
                "title": "A Floresta que Aprendeu a Escutar",
                "language": "pt-PT",
                "subtitle": "Uma história sobre escutar e pedir ajuda",
                "raw_text": "Tilo ouviu um som estranho junto às árvores.\n\nEm vez de avançar sozinho, chamou um adulto de confiança.\n\nJuntos descobriram que era apenas um passarinho preso entre dois ramos baixos.",
                "pages": [
                    {"pageNumber": 1, "title": "O som", "text": "Tilo ouviu um som estranho junto às árvores."},
                    {"pageNumber": 2, "title": "Pedir ajuda", "text": "Em vez de avançar sozinho, chamou um adulto de confiança."},
                    {"pageNumber": 3, "title": "A descoberta", "text": "Juntos ajudaram o passarinho e aprenderam que pedir ajuda é uma escolha corajosa."},
                ],
                "value_theme": "Pedir ajuda",
                "final_phrase": "Pedir ajuda também é coragem.",
            }
            runtime = {
                "metadata": {
                    "author_default": "Baribudo Estúdio",
                    "series_name": "Baribudos",
                    "producer": "Baribudo Estúdio",
                    "description": "Histórias originais para crianças e famílias",
                },
                "name": "Baribudos",
            }
            with patch.object(ebook_service, "resolve_storage_path", side_effect=lambda *parts: storage.joinpath(*parts)), patch.object(ebook_service, "load_ip_runtime", return_value=runtime):
                ebook = ebook_service.build_epub(
                    story,
                    project_id=project_id,
                    project_title=story["title"],
                    language="pt-PT",
                    author="Baribudo Estúdio",
                    saga_id="baribudos",
                )

            epub_path = Path(ebook["file_path"])
            self.assertTrue(epub_path.is_file())
            self.assertGreater(epub_path.stat().st_size, 1000)
            with zipfile.ZipFile(epub_path) as archive:
                self.assertIn("mimetype", archive.namelist())
                self.assertIn("META-INF/container.xml", archive.namelist())
                self.assertIn("OEBPS/content.opf", archive.namelist())
                self.assertIn("OEBPS/text/page_001.xhtml", archive.namelist())
                self.assertEqual(archive.read("mimetype"), b"application/epub+zip")

            with patch.object(audiobook_service, "resolve_storage_path", side_effect=lambda *parts: storage.joinpath(*parts)):
                audio_outputs = audiobook_service.build_audiobook(
                    {"pt-PT": story},
                    {"project_id": project_id, "project_title": story["title"], "provider": "system_tts"},
                )
            audio = audio_outputs["pt-PT"]
            audio_path = Path(audio["file_path"])
            self.assertTrue(audio_path.is_file())
            self.assertGreater(audio_path.stat().st_size, 1000)
            self.assertEqual(audio["format"], "wav")
            self.assertGreater(audio["segments_count"], 0)

            frame_dir = root / "frames"
            frame_dir.mkdir()
            first = frame_dir / "frame-001.png"
            second = frame_dir / "frame-002.png"
            Image.new("RGB", (640, 360), (230, 24, 24)).save(first)
            Image.new("RGB", (640, 360), (24, 24, 230)).save(second)
            with patch.object(video_service, "resolve_storage_path", side_effect=lambda *parts: storage.joinpath(*parts)):
                mini_series = video_service.build_series_episode(
                    story,
                    {
                        "project_id": project_id,
                        "project_title": story["title"],
                        "language": "pt-PT",
                        "audio_path": str(audio_path),
                        "sequence_frames": [
                            {"index": 1, "image_path": str(first)},
                            {"index": 2, "image_path": str(second)},
                        ],
                    },
                )
            mini_path = Path(mini_series["file_path"])
            self.assertTrue(mini_path.is_file())
            self.assertGreater(mini_path.stat().st_size, 1000)
            self.assertEqual(mini_series["format"], "mp4")

            production_outputs = [
                {"story": story, "ebook": ebook, "audio": audio, "mini_series": mini_series}
            ]
            for index in range(2, 6):
                next_story = {
                    **story,
                    "id": f"story-{index:03d}",
                    "title": f"História {index} — A floresta aprende em conjunto",
                    "raw_text": f"História {index}. Tilo e os amigos escutaram, conversaram e pediram ajuda a um adulto de confiança.",
                    "pages": [
                        {**page, "text": f"História {index}. {page['text']}"}
                        for page in story["pages"]
                    ],
                }
                next_project_id = f"{project_id}-{index:03d}"
                with patch.object(ebook_service, "resolve_storage_path", side_effect=lambda *parts: storage.joinpath(*parts)), patch.object(ebook_service, "load_ip_runtime", return_value=runtime):
                    next_ebook = ebook_service.build_epub(
                        next_story,
                        project_id=next_project_id,
                        project_title=next_story["title"],
                        language="pt-PT",
                        author="Baribudo Estúdio",
                        saga_id="baribudos",
                    )
                with patch.object(audiobook_service, "resolve_storage_path", side_effect=lambda *parts: storage.joinpath(*parts)):
                    next_audio = audiobook_service.build_audiobook(
                        {"pt-PT": next_story},
                        {"project_id": next_project_id, "project_title": next_story["title"], "provider": "system_tts"},
                    )["pt-PT"]
                with patch.object(video_service, "resolve_storage_path", side_effect=lambda *parts: storage.joinpath(*parts)):
                    next_video = video_service.build_series_episode(
                        next_story,
                        {
                            "project_id": next_project_id,
                            "project_title": next_story["title"],
                            "language": "pt-PT",
                            "audio_path": next_audio["file_path"],
                            "sequence_frames": [
                                {"index": 1, "image_path": str(first)},
                                {"index": 2, "image_path": str(second)},
                            ],
                        },
                    )
                production_outputs.append({
                    "story": next_story,
                    "ebook": next_ebook,
                    "audio": next_audio,
                    "mini_series": next_video,
                })

            five_stories = [
                {
                    "id": item["story"]["id"],
                    "title": item["story"]["title"],
                    "saga_slug": "baribudos",
                    "language": "pt-PT",
                    "sequence_number": index,
                    "editorial_status": "approved",
                    "value_theme": "Pedir ajuda",
                    "mini_series_path": item["mini_series"]["file_path"],
                }
                for index, item in enumerate(production_outputs, start=1)
            ]
            groups = select_complete_story_groups(five_stories)
            self.assertEqual(len(groups), 1)
            self.assertEqual(groups[0]["story_count"], 5)

            bundle_output = build_five_story_bundle(
                five_stories,
                output_dir=root / "bundle",
                title="Baribudos — primeiras cinco histórias",
            )
            self.assertEqual(bundle_output["status"], "completed")
            self.assertEqual(bundle_output["story_count"], 5)
            self.assertTrue(Path(bundle_output["guide"]["file_path"]).is_file())
            self.assertTrue(Path(bundle_output["compilation"]["file_path"]).is_file())
            self.assertEqual(bundle_output["compilation"]["video_codec"], "h264")
            self.assertEqual(bundle_output["compilation"]["audio_codec"], "aac")
            self.assertGreater(bundle_output["compilation"]["duration_seconds"], 0)

            report = {
                "status": "passed",
                "story_id": story["id"],
                "ebook": {"format": ebook["format"], "bytes": epub_path.stat().st_size},
                "audiobook": {"format": audio["format"], "bytes": audio_path.stat().st_size, "segments": audio["segments_count"]},
                "mini_series": {"format": mini_series["format"], "bytes": mini_path.stat().st_size, "engine": mini_series["engine"]},
                "five_story_outputs": [
                    {
                        "story_id": item["story"]["id"],
                        "ebook_bytes": Path(item["ebook"]["file_path"]).stat().st_size,
                        "audiobook_bytes": Path(item["audio"]["file_path"]).stat().st_size,
                        "audiobook_segments": item["audio"]["segments_count"],
                        "mini_series_bytes": Path(item["mini_series"]["file_path"]).stat().st_size,
                    }
                    for item in production_outputs
                ],
                "five_story_bundle": {
                    "story_count": bundle_output["story_count"],
                    "guide": bundle_output["guide"]["file_path"],
                    "compilation": bundle_output["compilation"],
                },
            }
            report_path = root / "production-validation-report.json"
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(report, ensure_ascii=False, indent=2))
            self.assertTrue(report_path.is_file())

            artifact_dir_value = os.environ.get("BARIBUDOS_PRODUCTION_TEST_OUTPUT_DIR")
            if artifact_dir_value:
                artifact_dir = Path(artifact_dir_value)
                artifact_dir.mkdir(parents=True, exist_ok=True)
                for source in (
                    *[Path(item["ebook"]["file_path"]) for item in production_outputs],
                    *[Path(item["audio"]["file_path"]) for item in production_outputs],
                    *[Path(item["mini_series"]["file_path"]) for item in production_outputs],
                    Path(bundle_output["guide"]["file_path"]),
                    Path(bundle_output["compilation"]["file_path"]),
                    report_path,
                ):
                    shutil.copy2(source, artifact_dir / source.name)

    def test_grouping_never_mixes_ip_language_or_unapproved_stories(self) -> None:
        stories = []
        for index in range(1, 11):
            stories.append({
                "id": f"approved-{index}",
                "saga_slug": "baribudos",
                "language": "pt-PT",
                "sequence_number": index,
                "editorial_status": "approved",
            })
        stories.extend([
            {"id": "draft", "saga_slug": "baribudos", "language": "pt-PT", "sequence_number": 7, "editorial_status": "draft"},
            {"id": "other-ip", "saga_slug": "other-ip", "language": "pt-PT", "sequence_number": 1, "approved": True},
            {"id": "other-language", "saga_slug": "baribudos", "language": "en", "sequence_number": 1, "approved": True},
        ])
        groups = select_complete_story_groups(stories)
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups[0]["story_ids"], [f"approved-{index}" for index in range(1, 6)])
        self.assertEqual(groups[1]["story_ids"], [f"approved-{index}" for index in range(6, 11)])
        self.assertEqual(groups[0]["saga_slug"], "baribudos")
        self.assertEqual(groups[0]["language"], "pt-PT")
        reversed_groups = select_complete_story_groups(list(reversed(stories)))
        self.assertEqual([item["id"] for item in groups], [item["id"] for item in reversed_groups])


if __name__ == "__main__":
    unittest.main()
