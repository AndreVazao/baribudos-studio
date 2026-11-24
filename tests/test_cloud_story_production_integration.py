from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from typing import Any
import zipfile
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from studio_core.services import audiobook_service, ebook_service, video_service
from studio_core.services.story_bundle_service import (
    _safe_compilation_target,
    build_five_story_bundle,
    select_complete_story_groups,
)


@unittest.skipUnless(
    shutil.which("ffmpeg") and shutil.which("ffprobe") and (shutil.which("espeak-ng") or shutil.which("espeak")),
    "FFmpeg, FFprobe and eSpeak are required for cloud production integration",
)
class VolumeOutputPathSecurityTests(unittest.TestCase):
    def test_output_path_must_resolve_inside_approved_storage(self) -> None:
        with tempfile.TemporaryDirectory(prefix="baribudos-volume-path-") as temp:
            root = Path(temp) / "storage"
            root.mkdir()
            target, temporary = _safe_compilation_target(
                root / "volumes" / "volume-001.mp4",
                root.resolve(),
            )
            self.assertEqual(target.parent, (root / "volumes").resolve())
            self.assertTrue(target.is_relative_to(root.resolve()))
            self.assertTrue(temporary.parent.is_relative_to(root.resolve()))

            outside = Path(temp) / "outside" / "volume.mp4"
            with self.assertRaisesRegex(ValueError, "compilation_output_outside_approved_storage"):
                _safe_compilation_target(outside, root.resolve())

    def test_output_path_rejects_symlinked_parent_and_target(self) -> None:
        with tempfile.TemporaryDirectory(prefix="baribudos-volume-symlink-") as temp:
            base = Path(temp)
            root = base / "storage"
            root.mkdir()
            outside = base / "outside"
            outside.mkdir()
            (root / "escape").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "compilation_output_outside_approved_storage"):
                _safe_compilation_target(root / "escape" / "volume.mp4", root.resolve())

            target = root / "linked.mp4"
            target.symlink_to(outside / "existing.mp4")
            with self.assertRaisesRegex(ValueError, "compilation_output_must_not_be_symlink"):
                _safe_compilation_target(target, root.resolve())


class CloudStoryProductionIntegrationTests(unittest.TestCase):
    def test_story_artifacts_generate_but_client_flags_cannot_open_volume_gate(self) -> None:
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
            self.assertEqual(mini_series["production_status"], "animatic_only")
            self.assertEqual(mini_series["audio_source"], "none")

            production_outputs = [
                {"story": story, "ebook": ebook, "audio": audio, "mini_series": mini_series}
            ]

            # Five fixture rows deliberately spoof every legacy approval field.
            # None is a human decision bound to an immutable revision/checksum.
            five_stories = [
                {
                    "id": f"fixture-story-{index:03d}",
                    "title": f"Synthetic fixture {index}",
                    "ip_slug": "baribudos",
                    "saga_slug": "baribudos",
                    "language": "pt-PT",
                    "sequence_number": index,
                    "approved": True,
                    "editorial_status": "approved",
                    "approval_state": "approved",
                    "mini_series_path": str(mini_path),
                }
                for index in range(1, 6)
            ]
            groups = select_complete_story_groups(five_stories)
            self.assertEqual(groups, [])

            bundle_result = build_five_story_bundle(
                five_stories,
                output_dir=storage / "bundle",
                storage_root=storage,
                title="Baribudos — fixture que não pode ser aprovado",
            )
            self.assertEqual(bundle_result["status"], "waiting_for_five_approved_stories")
            self.assertEqual(bundle_result["bundles_created"], 0)
            self.assertFalse((storage / "bundle" / "parents-guide.md").exists())
            self.assertFalse((storage / "bundle" / "five-story-mini-film.mp4").exists())

            bundle_output = {
                "technical_status": bundle_result["status"],
                "editorial_status": "not_approved",
                "fixture_rows": len(five_stories),
                "distinct_canonical_stories": False,
                "human_editorial_approvals": 0,
                "client_approval_flags_accepted": False,
                "guide_generated": False,
                "compilation_generated": False,
                "final_miniseries_count": 0,
                "season_created": False,
            }

            report = {
                "status": "passed",
                "validation_scope": "synthetic fixture validation only; no editorial approval or publication",
                "human_editorial_approvals": 0,
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
                "five_story_bundle": bundle_output,
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
                    report_path,
                ):
                    shutil.copy2(source, artifact_dir / source.name)

    def test_client_supplied_approval_fields_never_open_grouping(self) -> None:
        stories = []
        for index in range(1, 11):
            stories.append({
                "id": f"fixture-{index}",
                "ip_slug": "baribudos",
                "saga_slug": "baribudos",
                "language": "pt-PT",
                "sequence_number": index,
                "approved": True,
                "editorial_status": "approved",
                "approval_state": "approved",
            })
        self.assertEqual(select_complete_story_groups(stories), [])


if __name__ == "__main__":
    unittest.main()


class StoryBundleIntegrityTests(unittest.TestCase):
    def _story(self, story_id: str, **overrides: Any) -> dict:
        story = {
            "id": story_id,
            "ip_slug": "baribudos",
            "saga_slug": "floresta",
            "language": "pt-PT",
            "sequence_number": int(story_id.rsplit("-", 1)[-1]) if story_id.rsplit("-", 1)[-1].isdigit() else 1,
            "editorial_status": "approved",
        }
        story.update(overrides)
        return story

    def test_string_false_is_not_an_approval(self) -> None:
        stories = [self._story(f"story-{i}", approved="false", editorial_status="draft") for i in range(1, 6)]
        self.assertEqual(select_complete_story_groups(stories), [])

    def test_valid_looking_bundle_is_rejected_without_server_decisions(self) -> None:
        from studio_core.services.story_bundle_service import _validate_bundle_members
        stories = [
            self._story(
                f"story-{index}",
                approved=True,
                editorial_status="approved",
                approval_state="approved",
            )
            for index in range(1, 6)
        ]
        bundle = {
            "ip_slug": "baribudos",
            "saga_slug": "floresta",
            "language": "pt-PT",
            "stories": stories,
        }
        with self.assertRaisesRegex(ValueError, "bundle_requires_five_explicitly_approved_stories"):
            _validate_bundle_members(bundle)

    def test_same_saga_slug_in_different_ips_never_mixes(self) -> None:
        stories = [self._story(f"a-{i}", ip_slug="ip-a") for i in range(1, 4)]
        stories += [self._story(f"b-{i}", ip_slug="ip-b") for i in range(1, 4)]
        self.assertEqual(select_complete_story_groups(stories), [])

    def test_missing_ip_or_saga_is_rejected(self) -> None:
        from studio_core.services.story_bundle_service import _validate_bundle_members
        stories = [self._story(f"story-{i}") for i in range(1, 6)]
        stories[-1]["ip_slug"] = ""
        bundle = {
            "ip_slug": "baribudos",
            "saga_slug": "floresta",
            "language": "pt-PT",
            "stories": stories,
        }
        with self.assertRaisesRegex(ValueError, "approved_story_requires_ip_saga_and_language"):
            _validate_bundle_members(bundle)

    def test_duplicate_story_ids_cannot_complete_a_bundle(self) -> None:
        from studio_core.services.story_bundle_service import _validate_bundle_members
        stories = [self._story(f"story-{i}") for i in range(1, 6)]
        stories[-1]["id"] = stories[0]["id"]
        bundle = {
            "ip_slug": "baribudos",
            "saga_slug": "floresta",
            "language": "pt-PT",
            "stories": stories,
        }
        with self.assertRaisesRegex(ValueError, "bundle_requires_five_distinct_story_ids"):
            _validate_bundle_members(bundle)

    def test_bundle_builders_reject_mixed_identity_and_duplicate_members(self) -> None:
        stories = [self._story(f"story-{i}") for i in range(1, 6)]
        bundle = {
            "ip_slug": "baribudos",
            "saga_slug": "floresta",
            "language": "pt-PT",
            "stories": stories,
        }
        bundle["stories"][-1]["ip_slug"] = "another-ip"
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "bundle_cannot_mix_ip_saga_or_language"):
                from studio_core.services.story_bundle_service import build_parent_guide
                build_parent_guide(bundle, output_path=Path(temp) / "guide.md")
        bundle["stories"] = stories
        bundle["stories"][-1]["ip_slug"] = "baribudos"
        bundle["stories"][-1]["id"] = bundle["stories"][0]["id"]
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "bundle_requires_five_distinct_story_ids"):
                from studio_core.services.story_bundle_service import build_parent_guide
                build_parent_guide(bundle, output_path=Path(temp) / "guide.md")

    def test_declared_story_ids_must_match_frozen_members(self) -> None:
        from studio_core.services.story_bundle_service import build_parent_guide
        stories = [self._story(f"story-{i}") for i in range(1, 6)]
        bundle = {
            "ip_slug": "baribudos",
            "saga_slug": "floresta",
            "language": "pt-PT",
            "story_ids": ["story-1", "story-2", "story-3", "story-4", "different-story"],
            "stories": stories,
        }
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "bundle_story_ids_do_not_match_members"):
                build_parent_guide(bundle, output_path=Path(temp) / "guide.md")

    def test_compilation_rejects_assets_outside_storage_root(self) -> None:
        from studio_core.services.story_bundle_service import _approved_clip_path
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "approved"
            root.mkdir()
            outside = Path(temp) / "private.mp4"
            outside.write_bytes(b"not-a-video")
            story = self._story("story-1", mini_series_path=str(outside))
            with self.assertRaisesRegex(ValueError, "mini_series_asset_outside_approved_storage"):
                _approved_clip_path(story, "pt-PT", root.resolve())


if __name__ == "__main__":
    unittest.main()
