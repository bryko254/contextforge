# ContextForge

ContextForge is a developer tool that scans a codebase and generates AI-ready project documentation with Gemma 4 through the Gemini API.

Its main output is not just `README.md`. ContextForge also generates `AGENT.md`, a practical handoff file for future AI coding agents that need to understand the project after a chat is cleared, a new session starts, or a different agent joins the work.

## Short Pitch

Developers already use AI coding agents, but most repositories are not documented for agents. ContextForge turns a ZIP upload or sample repository into structured docs that help both humans and AI agents quickly understand what the project is, how to run it, where the important files live, and what safety rules to follow while editing.

## Problem

AI coding sessions often lose context. A new agent might not know:

- which framework or package manager the project uses
- where core business logic lives
- which setup commands are actually supported
- which folders are generated or should be ignored
- what assumptions are uncertain
- how to make safe edits without damaging user code

Traditional README files are usually written for humans. ContextForge generates documentation for humans and agents together, with special attention to `AGENT.md`.

## Why Gemma 4

Gemma 4 is a good fit for ContextForge because the task is documentation synthesis: the model needs to read structured codebase context, identify project patterns, avoid unsupported claims, and produce concise Markdown. Gemma 4 gives the app strong instruction following while keeping the architecture simple enough for a hackathon MVP.

The hosted demo uses the Gemini API for easy judging and setup. The architecture is intentionally provider-isolated so it can later support local Gemma 4 inference for private repositories.

## How Gemma 4 Is Used

1. The backend scans selected files from the uploaded or sample project.
2. The scanner filters out large, generated, binary, and irrelevant files.
3. Stack detection summarizes languages, frameworks, databases, infrastructure, and package managers.
4. ContextForge builds a structured prompt with file summaries, selected file content, and safety rules.
5. Gemma 4 returns valid JSON containing:
   - `readme`
   - `agent_md`
   - `setup`
   - `architecture`
   - `summary`
6. The frontend renders the generated docs in tabs with copy and ZIP download actions.

## Features

- Upload a ZIP codebase.
- Try a built-in Django sample project.
- Safe ZIP extraction with path traversal protection.
- File scanning with ignored folders such as `.git`, `node_modules`, `.venv`, `dist`, `build`, `.next`, and `coverage`.
- Text/code file selection with file and total prompt-size limits.
- Stack detection for Python, Django, FastAPI, Flask, Node.js, React, Vite, Next.js, Vue, Laravel, PHP, Docker, PostgreSQL, MySQL, SQLite, Tailwind, and TypeScript.
- Gemma 4 documentation generation through the Gemini API.
- Mock AI mode for local UI testing without an API key.
- Tabs for `README.md`, `AGENT.md`, `SETUP.md`, and `ARCHITECTURE.md`.
- Individual copy buttons for each generated document.
- Download all generated docs as a ZIP.

## Architecture

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
  | safe extract / sample path
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
  | JSON docs
  v
Frontend tabs, copy buttons, ZIP download
```

## Tech Stack

- Backend: FastAPI, Python, httpx, Pydantic Settings
- Frontend: React, Vite, TypeScript, plain CSS, JSZip
- AI: Gemma 4 through the Gemini API, configured as `gemma-4-26b-a4b-it`
- Sample project: Django REST Framework task API
- Local orchestration: Docker Compose

## Environment Variables

Backend: `backend/.env`

```env
GEMINI_API_KEY=
GEMMA_MODEL=gemma-4-26b-a4b-it
USE_MOCK_AI=true
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Frontend: `frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:8000
```

Use `USE_MOCK_AI=true` for local testing without an API key. Set `USE_MOCK_AI=false` and provide `GEMINI_API_KEY` to call the Gemini API.

## Local Setup

Create env files:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

## Run Without Docker

Start the backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend URLs:

- Health: `http://localhost:8000/api/health`
- Docs: `http://localhost:8000/docs`

Start the frontend in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

- App: `http://localhost:5173`

## Run With Docker Compose

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up --build
```

Services:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## How To Use

1. Open `http://localhost:5173`.
2. Click `Try sample project` to generate docs from the included Django sample.
3. Or click `Upload ZIP` and select a ZIP file containing a codebase.
4. Wait for scanning and Gemma generation.
5. Review the generated tabs:
   - `README.md`
   - `AGENT.md`
   - `SETUP.md`
   - `ARCHITECTURE.md`
6. Copy individual docs or download all docs as a ZIP.

## Demo Flow For Judges

1. Start the app with Docker Compose.
2. Keep `USE_MOCK_AI=false` and provide `GEMINI_API_KEY` if judging the live Gemini API flow.
3. Open the frontend at `http://localhost:5173`.
4. Click `Try sample project`.
5. Show the file summary panel:
   - detected Django/Python/PostgreSQL/Docker stack
   - selected files count
   - skipped files count
6. Open `AGENT.md` and highlight that it is written for future AI coding agents.
7. Copy one generated document.
8. Download all docs as a ZIP.
9. Optionally upload a small ZIP project to show the same pipeline on another codebase.

## Safety And Privacy Note

Uploaded code is processed for documentation generation. In the default hosted-demo flow, selected file contents are sent to Gemma 4 through the Gemini API unless mock mode or a future local model mode is configured.

For private repositories, users should avoid uploading sensitive code unless they are comfortable with that API processing path. ContextForge already isolates the AI client behind a backend service, and the architecture can later support local Gemma 4 inference for private repos.

## Limitations

- MVP scanning is heuristic-based and does not fully parse every language.
- Very large repositories are summarized by selected files and size limits.
- Generated docs depend on the files included in the scan.
- GitHub clone support is not currently exposed in the final frontend flow.
- The app does not yet persist generated documents server-side.
- Local Gemma 4 inference is planned but not implemented in this MVP.

## Future Improvements

- Add local Gemma 4 inference for private repositories.
- Add GitHub repository cloning in the frontend.
- Add richer language-aware parsing for Python, JavaScript, TypeScript, PHP, and Docker files.
- Add repository diff awareness so regenerated docs can focus on changes.
- Add export templates for different agent ecosystems.
- Add background jobs for large repositories.
- Add optional server-side generated-doc history.
- Add better prompt compression for very large codebases.

## License

MIT. See [LICENSE](LICENSE).
