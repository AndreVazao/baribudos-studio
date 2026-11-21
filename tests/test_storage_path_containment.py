from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from studio_core.core.config import APP_CONFIG, resolve_storage_path


class StoragePathContainmentTests(unittest.TestCase):
    def test_resolves_normal_relative_path_inside_storage_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with patch.object(APP_CONFIG, "storage_root", root):
                resolved = resolve_storage_path("editorial/assets/story/cover.png")

        self.assertEqual(resolved, root / "editorial" / "assets" / "story" / "cover.png")
        self.assertTrue(resolved.is_relative_to(root))

    def test_rejects_parent_directory_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with patch.object(APP_CONFIG, "storage_root", root):
                with self.assertRaisesRegex(ValueError, "storage_path_outside_root"):
                    resolve_storage_path("editorial/assets/../../../../outside.txt")

    def test_rejects_absolute_path_outside_storage_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            outside = Path(directory).parent / "outside.txt"
            with patch.object(APP_CONFIG, "storage_root", root):
                with self.assertRaisesRegex(ValueError, "storage_path_must_be_relative"):
                    resolve_storage_path(str(outside))


    def test_normalizes_windows_separators_before_containment_check(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with patch.object(APP_CONFIG, "storage_root", root):
                resolved = resolve_storage_path(r"editorial\assets\story\cover.png")

        self.assertEqual(resolved, root / "editorial" / "assets" / "story" / "cover.png")

    def test_rejects_windows_style_parent_traversal_on_posix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with patch.object(APP_CONFIG, "storage_root", root):
                with self.assertRaisesRegex(ValueError, "storage_path_outside_root"):
                    resolve_storage_path(r"editorial\assets\..\..\..\outside.txt")

    def test_rejects_windows_drive_and_unc_absolute_paths_on_posix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with patch.object(APP_CONFIG, "storage_root", root):
                for unsafe in (r"C:\private\secret.txt", r"\server\share\secret.txt"):
                    with self.subTest(path=unsafe):
                        with self.assertRaisesRegex(ValueError, "storage_path_must_be_relative"):
                            resolve_storage_path(unsafe)

    def test_rejects_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "storage"
            outside = Path(directory) / "outside"
            root.mkdir()
            outside.mkdir()
            (root / "linked").symlink_to(outside, target_is_directory=True)

            with patch.object(APP_CONFIG, "storage_root", root):
                with self.assertRaisesRegex(ValueError, "storage_path_outside_root"):
                    resolve_storage_path("linked/secret.bin")


if __name__ == "__main__":
    unittest.main()
