from __future__ import annotations

import unittest
from unittest.mock import patch

from studio_core.services import project_factory_engine as factory


class ProjectFactoryVideoSequenceTests(unittest.TestCase):
    def test_passes_all_approved_storyboard_frames_to_video_builder(self) -> None:
        frames = [
            {"index": 1, "image_path": "/tmp/baribudos-frame-1.png"},
            {"index": 2, "image_path": "/tmp/baribudos-frame-2.png"},
        ]
        captured = {}

        def fake_build_series_episode(story, payload):
            captured["story"] = story
            captured["payload"] = payload
            return {"type": "video", "file_path": "/tmp/episode.mp4"}

        with patch.object(
            factory,
            "build_video_frame_sequence",
            return_value={"frames_count": len(frames), "frames": frames},
        ), patch.object(
            factory,
            "build_series_episode",
            side_effect=fake_build_series_episode,
        ):
            result = factory._build_video_outputs(
                project={
                    "id": "project-1",
                    "title": "A floresta dos Baribudos",
                    "cover_image": "/tmp/cover.png",
                },
                story_variants={
                    "pt-PT": {
                        "title": "A floresta dos Baribudos",
                        "language": "pt-PT",
                    }
                },
                cover_output=None,
                audiobook_outputs={
                    "pt-PT": {"file_path": "/tmp/audiobook.wav"}
                },
            )

        self.assertEqual(captured["payload"]["sequence_frames"], frames)
        self.assertEqual(captured["payload"]["cover_path"], frames[0]["image_path"])
        self.assertEqual(captured["payload"]["audio_path"], "/tmp/audiobook.wav")
        self.assertEqual(result["pt-PT"]["storyboard_frames_count"], 2)

    def test_passes_empty_sequence_when_no_approved_frames_exist(self) -> None:
        captured = {}

        def fake_build_series_episode(story, payload):
            captured["payload"] = payload
            return {"type": "video", "file_path": "/tmp/episode.mp4"}

        with patch.object(
            factory,
            "build_video_frame_sequence",
            return_value={"frames_count": 0, "frames": []},
        ), patch.object(
            factory,
            "build_series_episode",
            side_effect=fake_build_series_episode,
        ):
            result = factory._build_video_outputs(
                project={
                    "id": "project-2",
                    "title": "Uma história",
                    "cover_image": "/tmp/cover.png",
                },
                story_variants={
                    "pt-PT": {
                        "title": "Uma história",
                        "language": "pt-PT",
                    }
                },
                cover_output=None,
                audiobook_outputs={},
            )

        self.assertEqual(captured["payload"]["sequence_frames"], [])
        self.assertEqual(captured["payload"]["cover_path"], "/tmp/cover.png")
        self.assertEqual(result["pt-PT"]["storyboard_frames_count"], 0)


if __name__ == "__main__":
    unittest.main()
