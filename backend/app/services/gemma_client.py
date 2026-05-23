from __future__ import annotations

import json
from typing import Any

import httpx

from app.config import get_settings

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
REQUEST_TIMEOUT_SECONDS = 60.0


class GemmaClientError(RuntimeError):
    pass


async def generate_with_gemma(prompt: str) -> str:
    settings = get_settings()

    if settings.use_mock_ai:
        return _mock_docs_response()

    if not settings.gemini_api_key:
        raise GemmaClientError("Gemini API key is missing. Add GEMINI_API_KEY or enable USE_MOCK_AI=true.")

    url = GEMINI_ENDPOINT.format(model=settings.gemma_model)
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(
                url,
                params={"key": settings.gemini_api_key},
                json=payload,
            )
    except httpx.HTTPError as exc:
        raise GemmaClientError(f"Gemini API request failed: {exc.__class__.__name__}") from exc

    if response.status_code != 200:
        raise GemmaClientError(_format_api_error(response))

    return _extract_text(response.json())


def _extract_text(data: dict[str, Any]) -> str:
    try:
        candidates = data["candidates"]
        if not candidates:
            raise KeyError("candidates")
        parts = candidates[0]["content"]["parts"]
    except (KeyError, TypeError) as exc:
        raise GemmaClientError("Gemini API response did not include generated text.") from exc

    text_parts = [
        part.get("text", "")
        for part in parts
        if isinstance(part, dict) and isinstance(part.get("text"), str)
    ]
    text = "\n".join(part for part in text_parts if part).strip()
    if not text:
        raise GemmaClientError("Gemini API returned an empty text response.")
    return text


def _format_api_error(response: httpx.Response) -> str:
    try:
        body = response.json()
    except json.JSONDecodeError:
        body = response.text[:300]

    if isinstance(body, dict):
        message = body.get("error", {}).get("message") or body.get("message")
        if message:
            return f"Gemini API returned HTTP {response.status_code}: {message}"

    return f"Gemini API returned HTTP {response.status_code}."


def _mock_docs_response() -> str:
    return json.dumps(
        {
            "readme": "# Sample Project\n\nA practical generated README for local testing.",
            "agent_md": "# AGENT.md\n\nUse this document to understand project structure, safe edit areas, and validation steps.",
            "setup": "# Setup\n\nInstall dependencies and run the project using commands supported by the scanned files.",
            "architecture": "# Architecture\n\nThe project is summarized from scanned files and detected framework signals.",
            "summary": {
                "project_name_guess": "sample-project",
                "detected_stack": ["Python"],
                "main_features": ["Demonstrates ContextForge documentation generation."],
                "risks_or_unknowns": ["Mock AI mode was used, so these docs are illustrative."],
            },
        },
        indent=2,
    )
