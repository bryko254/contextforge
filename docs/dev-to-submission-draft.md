---
title: I Built ContextForge with Gemma 4: A Project Memory Generator for Developers and AI Coding Agents
published: false
tags: devchallenge, gemmachallenge, gemma
---

*This is a submission for the [Gemma 4 Challenge: Build with Gemma 4](https://dev.to/challenges/google-gemma-2026-05-06).*

## What I Built

ContextForge is a developer tool that scans a codebase and generates practical, AI-ready project documentation using Gemma 4 through the Gemini API.

The goal is simple: when a developer or AI coding agent opens a project, they should not have to rediscover the whole repository from scratch. ContextForge generates `README.md`, `SETUP.md`, `ARCHITECTURE.md`, and especially `AGENT.md`, a durable handoff file designed for future AI coding sessions.

## The problem: AI coding agents lose context

AI coding agents are useful, but their context is fragile.

When a chat is cleared, a session expires, or a different agent starts working on the same repository, a lot of hard-won project understanding disappears:

- what framework the app uses
- which files matter most
- how to run the project locally
- what generated folders should be ignored
- what assumptions are still uncertain
- what safety rules an agent should follow before editing

Traditional README files help humans, but they are not always enough for AI agents. Agents need a project map, editing constraints, validation steps, and warnings about risky areas.

That is why ContextForge focuses on `AGENT.md`.

## What ContextForge does

ContextForge takes a ZIP upload or a built-in sample project and generates documentation from the actual files in the codebase.

The MVP can:

- upload a ZIP file
- load a built-in Django sample project
- safely extract and scan files
- ignore folders like `.git`, `node_modules`, `.venv`, `dist`, `build`, `.next`, and `coverage`
- detect the tech stack
- build a structured prompt for Gemma 4
- generate:
  - `README.md`
  - `AGENT.md`
  - `SETUP.md`
  - `ARCHITECTURE.md`
- display generated docs in tabs
- copy each generated document
- download all generated docs as a ZIP

The output is meant to be practical rather than marketing-heavy. If ContextForge is unsure about something, the prompt asks the model to mark that uncertainty instead of inventing details.

## Demo

Demo link: pending deployment URL.

Demo video: pending recording URL.

The judge-friendly demo flow is:

1. Open the ContextForge frontend.
2. Click **Try sample project**.
3. The backend scans the built-in Django task API sample.
4. ContextForge detects Python, Django, PostgreSQL, Docker, and pip.
5. The app asks Gemma 4 to generate docs.
6. The UI displays:
   - `README.md`
   - `AGENT.md`
   - `SETUP.md`
   - `ARCHITECTURE.md`
7. Open `AGENT.md` and show the AI-agent-focused project handoff.
8. Copy a generated document.
9. Download all docs as a ZIP.
10. Optionally upload a small ZIP project and run the same flow.

The app also supports mock mode, so the UI can be tested without a Gemini API key. For judging the real AI flow, run with `USE_MOCK_AI=false` and provide `GEMINI_API_KEY`.

## Code

Repository: pending GitHub repository URL.

The project is structured as a small full-stack app:

- `backend/`: FastAPI API, ZIP handling, scanning, stack detection, prompt construction, and Gemma API client.
- `frontend/`: React/Vite UI for uploads, sample generation, document tabs, copy buttons, and ZIP export.
- `sample-projects/django-api-demo/`: built-in Django REST Framework sample used for the default demo.
- `docs/dev-to-submission-draft.md`: this DEV submission draft.

## How I Used Gemma 4

ContextForge uses `gemma-4-26b-a4b-it` through the Gemini API. I chose this model because ContextForge is not trying to write arbitrary code; it is doing structured documentation synthesis over selected codebase context.

The model needs to:

- read selected project files
- follow a strict JSON response schema
- avoid inventing dependencies
- summarize architecture clearly
- generate instructions for both humans and AI coding agents

Gemma 4 works well for this kind of grounded, instruction-following task. The hosted demo uses the Gemini API so judges can try the app without running a local model.

The architecture is intentionally isolated behind a `gemma_client.py` service, so the project can later support local Gemma 4 inference for private repositories.

The Gemma 4 call is at the heart of the pipeline:

1. The backend scans selected files from the uploaded or sample project.
2. The scanner filters out large, generated, binary, and irrelevant files.
3. Stack detection summarizes languages, frameworks, databases, infrastructure, and package managers.
4. ContextForge builds a structured prompt with file summaries, selected file content, and safety rules.
5. Gemma 4 returns valid JSON containing `readme`, `agent_md`, `setup`, `architecture`, and `summary`.
6. The backend validates the JSON schema before returning it to the frontend.

## Architecture

The app has a small full-stack architecture:

```text
User
  |
  | ZIP upload or sample project
  v
React + Vite frontend
  |
  | HTTP request
  v
FastAPI backend
  |
  | safe ZIP extraction / sample project path
  v
Scanner
  |
  | selected files + file tree
  v
Stack detector
  |
  | structured stack summary
  v
Prompt builder
  |
  | documentation prompt
  v
Gemma 4 via Gemini API
  |
  | JSON response
  v
Generated docs UI
```

The backend is responsible for file handling, scan limits, prompt construction, and API calls. The frontend is responsible for upload controls, loading states, docs tabs, copy buttons, and ZIP download.

## How the codebase scanner works

The scanner is intentionally simple and safe for an MVP.

It walks an extracted project directory recursively and ignores noisy or risky paths, including:

- `.git`
- `node_modules`
- `venv`
- `.venv`
- `__pycache__`
- `dist`
- `build`
- `vendor`
- `.next`
- `.turbo`
- `coverage`

It also skips binary and large files such as databases, images, PDFs, and ZIPs.

The scanner only reads text/code files and applies limits:

- maximum individual file size: 80KB
- maximum collected content: about 300KB

Important files are prioritized, including:

- `README.md`
- `package.json`
- `requirements.txt`
- `pyproject.toml`
- `Dockerfile`
- `docker-compose.yml`
- `manage.py`
- `settings.py`
- `urls.py`
- `models.py`
- `views.py`
- `serializers.py`
- folders like `src`, `app`, and `routes`

The scanner returns a file tree summary, selected file contents, skipped file count, and total collected size.

## How AGENT.md is generated

`AGENT.md` is generated from the same scan context as the other docs, but the prompt gives it a specific job.

It asks Gemma 4 to write `AGENT.md` for future AI coding agents. That means the output should include:

- project map
- important directories and files
- setup and validation guidance
- safe development rules
- uncertain assumptions
- areas that need extra caution

This is the core idea behind ContextForge: make project context durable across AI coding sessions.

For example, after a chat is cleared, the next agent can open `AGENT.md` and immediately understand how to move safely inside the repository.

## Challenges faced

The biggest challenge was deciding how much code context to send to the model.

Sending everything is risky and inefficient. Sending too little gives weak documentation. The MVP solves this with a scanner that prioritizes important files, skips generated/binary folders, and keeps a strict total content limit.

Another challenge was making the model output predictable. ContextForge asks Gemma 4 for valid JSON with a fixed schema, then the backend validates that response before sending it to the frontend.

I also had to handle security basics around ZIP uploads. The backend checks for path traversal before extracting archives and cleans temporary folders after processing.

Finally, I wanted the project to work without a real API key during local testing, so I added `USE_MOCK_AI=true`.

## What I would improve next

Next improvements I would make:

- add GitHub repository cloning from the frontend
- support local Gemma 4 inference for private repositories
- add richer language-specific parsing
- generate docs from diffs after code changes
- add server-side history for generated docs
- support more output formats for different agent ecosystems
- improve prompt compression for large repositories
- add background jobs for larger scans

The local inference path is especially important. The hosted demo uses Gemini API for easy judging, but private repositories should eventually be able to use local Gemma 4 inference without sending selected code context to an external API.
