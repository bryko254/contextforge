import json
import unittest
from unittest.mock import AsyncMock, Mock, patch

import httpx

from app.config import get_settings
from app.services.gemma_client import GemmaClientError, generate_with_gemma


class GemmaClientTests(unittest.IsolatedAsyncioTestCase):
    def tearDown(self) -> None:
        get_settings.cache_clear()

    async def test_mock_mode_returns_fake_docs_without_api_key(self) -> None:
        with patch.dict("os.environ", {"USE_MOCK_AI": "true", "GEMINI_API_KEY": ""}, clear=False):
            get_settings.cache_clear()
            result = await generate_with_gemma("Generate docs")

        parsed = json.loads(result)
        self.assertIn("readme", parsed)
        self.assertIn("agent_md", parsed)
        self.assertIn("summary", parsed)

    async def test_missing_api_key_raises_clear_error(self) -> None:
        with patch.dict("os.environ", {"USE_MOCK_AI": "false", "GEMINI_API_KEY": ""}, clear=False):
            get_settings.cache_clear()
            with self.assertRaisesRegex(GemmaClientError, "Gemini API key is missing"):
                await generate_with_gemma("Generate docs")

    async def test_successful_response_returns_generated_text(self) -> None:
        response = httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {"text": "README content"},
                                {"text": "AGENT content"},
                            ]
                        }
                    }
                ]
            },
        )
        client = _mock_client(response)

        with patch.dict("os.environ", {"USE_MOCK_AI": "false", "GEMINI_API_KEY": "test-key"}, clear=False):
            get_settings.cache_clear()
            with patch("app.services.gemma_client.httpx.AsyncClient", return_value=client):
                result = await generate_with_gemma("Generate docs")

        self.assertEqual(result, "README content\nAGENT content")
        client.post.assert_awaited_once()

    async def test_non_200_response_raises_clean_error(self) -> None:
        response = httpx.Response(403, json={"error": {"message": "Permission denied"}})
        client = _mock_client(response)

        with patch.dict("os.environ", {"USE_MOCK_AI": "false", "GEMINI_API_KEY": "test-key"}, clear=False):
            get_settings.cache_clear()
            with patch("app.services.gemma_client.httpx.AsyncClient", return_value=client):
                with self.assertRaisesRegex(GemmaClientError, "HTTP 403: Permission denied"):
                    await generate_with_gemma("Generate docs")

    async def test_malformed_response_raises_clean_error(self) -> None:
        response = httpx.Response(200, json={"candidates": []})
        client = _mock_client(response)

        with patch.dict("os.environ", {"USE_MOCK_AI": "false", "GEMINI_API_KEY": "test-key"}, clear=False):
            get_settings.cache_clear()
            with patch("app.services.gemma_client.httpx.AsyncClient", return_value=client):
                with self.assertRaisesRegex(GemmaClientError, "did not include generated text"):
                    await generate_with_gemma("Generate docs")


def _mock_client(response: httpx.Response) -> Mock:
    client = Mock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    client.post = AsyncMock(return_value=response)
    return client


if __name__ == "__main__":
    unittest.main()
