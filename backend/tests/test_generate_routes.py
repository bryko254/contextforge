from io import BytesIO
from unittest.mock import patch
from zipfile import ZipFile
import unittest

from fastapi import HTTPException

from app.config import get_settings
from app.routes import generate as generate_routes


class GenerateRouteTests(unittest.IsolatedAsyncioTestCase):
    def tearDown(self) -> None:
        get_settings.cache_clear()

    async def test_sample_endpoint_runs_generation_pipeline_with_mock_ai(self) -> None:
        with patch.dict("os.environ", {"USE_MOCK_AI": "true", "GEMINI_API_KEY": ""}, clear=False):
            get_settings.cache_clear()
            response = await generate_routes.generate_from_sample()

        self.assertEqual(response.source, "sample")
        self.assertEqual(response.project_name, "django-api-demo")
        self.assertIn("README.md", response.file_summary.files)
        self.assertTrue(response.docs.readme.startswith("#"))

    async def test_generate_endpoint_accepts_zip_and_returns_docs(self) -> None:
        upload = _upload_from_zip(
            {
                "demo/README.md": "# Demo\n",
                "demo/requirements.txt": "fastapi\n",
                "demo/app/main.py": "from fastapi import FastAPI\n",
            }
        )

        with patch.dict("os.environ", {"USE_MOCK_AI": "true", "GEMINI_API_KEY": ""}, clear=False):
            get_settings.cache_clear()
            response = await generate_routes.generate_from_zip(upload)

        self.assertEqual(response.source, "zip")
        self.assertEqual(response.project_name, "demo")
        self.assertIn("README.md", response.file_summary.files)
        self.assertIn("FastAPI", response.file_summary.tech_stack.frameworks)
        self.assertTrue(response.docs.agent_md.startswith("#"))

    async def test_generate_endpoint_rejects_zip_path_traversal(self) -> None:
        upload = _upload_from_zip({"../evil.py": "print('bad')\n"})

        with self.assertRaises(HTTPException) as raised:
            await generate_routes.generate_from_zip(upload)

        self.assertEqual(raised.exception.status_code, 400)

    async def test_generate_endpoint_rejects_large_uploads(self) -> None:
        upload = _FakeUpload("large.zip", b"x" * 20)

        with patch.object(generate_routes, "MAX_UPLOAD_BYTES", 10):
            with self.assertRaises(HTTPException) as raised:
                await generate_routes.generate_from_zip(upload)

        self.assertEqual(raised.exception.status_code, 413)


def _upload_from_zip(files: dict[str, str]) -> "_FakeUpload":
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        for path, content in files.items():
            archive.writestr(path, content)
    return _FakeUpload("project.zip", buffer.getvalue())


class _FakeUpload:
    def __init__(self, filename: str, content: bytes) -> None:
        self.filename = filename
        self._file = BytesIO(content)

    async def read(self, size: int = -1) -> bytes:
        return self._file.read(size)


if __name__ == "__main__":
    unittest.main()
