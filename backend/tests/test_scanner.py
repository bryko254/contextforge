from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from app.services.scanner import (
    MAX_FILE_SIZE_BYTES,
    MAX_TOTAL_CONTENT_BYTES,
    scan_project,
)


class ScannerTests(unittest.TestCase):
    def test_scan_project_ignores_unwanted_files_and_selects_text_files(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "demo"
            root.mkdir()
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")
            (root / "manage.py").write_text("print('manage')\n", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("print('hello')\n", encoding="utf-8")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "ignored.js").write_text("ignored\n", encoding="utf-8")
            (root / "db.sqlite3").write_text("ignored\n", encoding="utf-8")
            (root / "image.png").write_bytes(b"\x89PNG\r\n")

            result = scan_project(root)

            self.assertEqual(result.project_name, "demo")
            self.assertIn("README.md", result.files)
            self.assertIn("manage.py", result.files)
            self.assertIn("src/app.py", result.files)
            self.assertNotIn("node_modules/ignored.js", result.file_tree)
            self.assertNotIn("db.sqlite3", result.files)
            self.assertNotIn("image.png", result.files)
            self.assertGreaterEqual(result.skipped_files, 2)
            self.assertGreater(result.total_size, 0)

    def test_scan_project_enforces_file_and_total_size_limits(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "large-demo"
            root.mkdir()
            (root / "too_big.py").write_text("x" * (MAX_FILE_SIZE_BYTES + 1), encoding="utf-8")

            for index in range(10):
                (root / f"file_{index}.py").write_text("y" * (40 * 1024), encoding="utf-8")

            result = scan_project(root)

            self.assertNotIn("too_big.py", result.files)
            self.assertLessEqual(result.total_size, MAX_TOTAL_CONTENT_BYTES)
            self.assertGreater(result.skipped_files, 0)


if __name__ == "__main__":
    unittest.main()
