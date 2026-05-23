from __future__ import annotations

import json
from typing import Any

MAX_INCLUDED_FILE_CHARS = 12_000


def build_documentation_prompt(
    project_summary: Any,
    stack_summary: Any,
    selected_files: list[Any],
) -> str:
    prompt_context = {
        "project_summary": _to_plain_data(project_summary),
        "stack_summary": _to_plain_data(stack_summary),
        "selected_files": [_normalize_file(file) for file in selected_files],
    }

    context_json = json.dumps(prompt_context, indent=2, ensure_ascii=False)

    return f"""
You are ContextForge, a senior software documentation generator for developer tooling.

Your task is to generate practical, AI-ready documentation for a software project using only the scanned project context below.

Return valid JSON only. Do not wrap the JSON in Markdown fences. Do not include commentary before or after the JSON.

The JSON must use this exact top-level structure:
{{
  "readme": "...markdown...",
  "agent_md": "...markdown...",
  "setup": "...markdown...",
  "architecture": "...markdown...",
  "summary": {{
    "project_name_guess": "...",
    "detected_stack": [],
    "main_features": [],
    "risks_or_unknowns": []
  }}
}}

Documentation requirements:
- Do not invent dependencies, services, commands, scripts, databases, cloud resources, or frameworks that are not supported by the provided files.
- Clearly mark uncertain assumptions with phrases like "Likely", "Appears to", or "Unknown".
- Generate "agent_md" specifically as AGENT.md for future AI coding agents that may enter this project after chat history is gone.
- In AGENT.md, include project map, important files/directories, safe development rules, testing guidance, and areas requiring extra caution.
- Include setup commands only when supported by files such as package.json, requirements.txt, pyproject.toml, composer.json, Dockerfile, docker-compose.yml, manage.py, or similar.
- Mention important directories and files from the selected files and file tree.
- Keep the docs practical and direct. Avoid marketing-heavy claims and generic filler.
- Prefer concise sections, clear bullet points, and actionable local-development notes.
- If information is missing, put it in summary.risks_or_unknowns and mention it briefly in the relevant document.
- Preserve exact filenames such as README.md, AGENT.md, SETUP.md, and ARCHITECTURE.md inside the Markdown when useful.

Document-specific guidance:
- "readme": Human-facing overview with purpose, detected stack, features inferred from files, and quickstart if supported.
- "agent_md": AI-agent-facing guide with repository orientation, editing constraints, safe development rules, and context recovery notes.
- "setup": Local setup steps, environment variables, dependency installation, run commands, and verification steps only when supported by evidence.
- "architecture": High-level modules, data flow, boundaries, notable directories, integration points, and extension notes.
- "summary.detected_stack": A compact array of detected languages, frameworks, databases, infrastructure, and package managers.
- "summary.main_features": Features inferred from code and configuration, not imagined product promises.
- "summary.risks_or_unknowns": Missing files, unclear commands, unsupported assumptions, security concerns, or scan limitations.

Scanned project context:
{context_json}
""".strip()


def _normalize_file(file: Any) -> dict[str, Any]:
    data = _to_plain_data(file)
    if not isinstance(data, dict):
        return {"path": "unknown", "content": "", "size": 0}

    content = str(data.get("content", ""))
    if len(content) > MAX_INCLUDED_FILE_CHARS:
        content = content[:MAX_INCLUDED_FILE_CHARS] + "\n...[truncated for prompt size]..."

    return {
        "path": str(data.get("path", "unknown")),
        "size": int(data.get("size", len(content.encode("utf-8", errors="ignore")))),
        "content": content,
    }


def _to_plain_data(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, dict):
        return value
    if isinstance(value, (list, tuple)):
        return [_to_plain_data(item) for item in value]
    return value
