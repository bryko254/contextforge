# Gemma 4 Challenge Submission Checklist

Use this checklist before publishing the DEV post for the Build With Gemma 4 track.

## Required Links

- Live demo: optional; local Docker demo instructions are included in the article.
- GitHub repository: https://github.com/bryko254/contextforge.
- Demo video: optional; add a recording URL if one is prepared before the deadline.

## Local Verification

- Backend tests:

```bash
cd backend
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

- Frontend build:

```bash
cd frontend
npm install
npm run build
```

- End-to-end local demo:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up --build
```

Open `http://localhost:5173` and click `Try sample project`.

## Submission Notes

- Submit under `Gemma 4 Challenge: Build with Gemma 4`.
- Explain that ContextForge uses `gemma-4-26b-a4b-it` through the Gemini API.
- Call out why that model is appropriate: structured codebase-context synthesis, JSON-following, and generation of practical documentation for humans and AI coding agents.
- Mention that `USE_MOCK_AI=true` is only for local testing; judging the live AI path requires `USE_MOCK_AI=false` and `GEMINI_API_KEY`.
- Add teammate DEV handles in the post body if this is submitted as a team entry.
