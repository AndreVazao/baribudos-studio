from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from studio_core.services import video_service


@unittest.skipUnless(
    shutil.which("ffmpeg") and shutil.which("ffprobe"),
    "FFmpeg and FFprobe are required for the real video integration test",
)
class VideoServiceFFmpegIntegrationTests(unittest.TestCase):
    def test_build_series_episode_renders_ordered_frames_with_real_audio(self) -> None:
        configured_output = os.environ.get("BARIBUDOS_FFMPEG_TEST_OUTPUT_DIR")
        temporary = None
        if configured_output:
            root = Path(configured_output).resolve()
            if root.exists():
                shutil.rmtree(root)
            root.mkdir(parents=True)
        else:
            temporary = tempfile.TemporaryDirectory(prefix="baribudos-ffmpeg-")
            root = Path(temporary.name)

        try:
            source_dir = root / "source"
            source_dir.mkdir(parents=True, exist_ok=True)
            red_frame = source_dir / "frame-001-red.png"
            blue_frame = source_dir / "frame-002-blue.png"
            audio_path = source_dir / "voice-test.wav"

            Image.new("RGB", (640, 360), (230, 24, 24)).save(red_frame)
            Image.new("RGB", (640, 360), (24, 24, 230)).save(blue_frame)

            subprocess.run(
                [
                    "ffmpeg",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=440:duration=3",
                    "-c:a",
                    "pcm_s16le",
                    str(audio_path),
                ],
                check=True,
                timeout=60,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            storage_root = root / "storage"
            with patch.object(
                video_service,
                "resolve_storage_path",
                side_effect=lambda *parts: storage_root.joinpath(*parts),
            ):
                result = video_service.build_series_episode(
                    {
                        "title": "Cloud FFmpeg integration",
                        "language": "pt-PT",
                        "pages": [],
                    },
                    {
                        "project_id": "cloud-ffmpeg-integration",
                        "project_title": "Cloud FFmpeg integration",
                        "language": "pt-PT",
                        "audio_path": str(audio_path),
                        "sequence_frames": [
                            {"index": 1, "image_path": str(red_frame)},
                            {"index": 2, "image_path": str(blue_frame)},
                        ],
                    },
                )

            output_path = Path(result["file_path"])
            self.assertTrue(output_path.is_file(), "The video service did not create an MP4")
            self.assertGreater(output_path.stat().st_size, 10_000)
            self.assertEqual(result["format"], "mp4")
            self.assertEqual(result["engine"], "ffmpeg-slideshow+audio")
            self.assertEqual(result["frames_used"], 2)

            probe = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-count_frames",
                    "-show_entries",
                    "format=duration,size:stream=codec_type,codec_name,width,height,nb_read_frames",
                    "-of",
                    "json",
                    str(output_path),
                ],
                check=True,
                timeout=30,
                capture_output=True,
                text=True,
            )
            metadata = json.loads(probe.stdout)
            streams = metadata.get("streams", [])
            video_stream = next((item for item in streams if item.get("codec_type") == "video"), None)
            audio_stream = next((item for item in streams if item.get("codec_type") == "audio"), None)

            self.assertIsNotNone(video_stream, "MP4 is missing its video stream")
            self.assertIsNotNone(audio_stream, "MP4 is missing its audio stream")
            self.assertEqual(video_stream["codec_name"], "h264")
            self.assertEqual(audio_stream["codec_name"], "aac")
            self.assertEqual((video_stream["width"], video_stream["height"]), (1600, 900))
            self.assertGreater(int(video_stream.get("nb_read_frames", 0)), 20)

            duration = float(metadata["format"]["duration"])
            self.assertGreaterEqual(duration, 2.5)
            self.assertLessEqual(duration, 4.0)

            extracted_red = root / "sample-red.png"
            extracted_blue = root / "sample-blue.png"
            for timestamp, destination in ((0.5, extracted_red), (2.1, extracted_blue)):
                subprocess.run(
                    [
                        "ffmpeg",
                        "-hide_banner",
                        "-loglevel",
                        "error",
                        "-y",
                        "-ss",
                        str(timestamp),
                        "-i",
                        str(output_path),
                        "-frames:v",
                        "1",
                        str(destination),
                    ],
                    check=True,
                    timeout=30,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

            red_pixel = Image.open(extracted_red).convert("RGB").getpixel((800, 450))
            blue_pixel = Image.open(extracted_blue).convert("RGB").getpixel((800, 450))
            self.assertGreater(red_pixel[0], red_pixel[2] + 80, "First storyboard frame is not the red frame")
            self.assertGreater(blue_pixel[2], blue_pixel[0] + 80, "Second storyboard frame is not the blue frame")

            report = {
                "status": "passed",
                "engine": result["engine"],
                "frames_used": result["frames_used"],
                "output": str(output_path.relative_to(root)),
                "output_size_bytes": output_path.stat().st_size,
                "duration_seconds": duration,
                "video_stream": video_stream,
                "audio_stream": audio_stream,
                "sampled_frame_center_rgb": {
                    "first": red_pixel,
                    "second": blue_pixel,
                },
            }
            (root / "validation-report.json").write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(json.dumps(report, ensure_ascii=False, indent=2))
        finally:
            if temporary is not None:
                temporary.cleanup()


if __name__ == "__main__":
    unittest.main()
