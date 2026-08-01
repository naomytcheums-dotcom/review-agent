# Review Agent

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat&logo=python&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat&logo=pydantic&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat&logo=vite&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)
![OpenAI SDK](https://img.shields.io/badge/OpenAI_SDK-412991?style=flat&logo=openai&logoColor=white)
![GitLab](https://img.shields.io/badge/GitLab-FC6D26?style=flat&logo=gitlab&logoColor=white)

Review Agent reads a GitLab merge request's changed files and gives each one a real code review — accept or reject, a score, and specific issues — posted as an inline comment on the exact line that matters.

## Why it exists

Small merge requests sit waiting for a human reviewer more often than they should, and a first pass often just needs someone to catch the obvious stuff — a magic number, a missing null check, an unnecessary dependency. Review Agent does that first pass automatically, so human reviewers spend their time on the things that actually need judgment.

## Features

### Real code review, not a linter
- The AI reads the actual diff — original code vs. new code — and reviews it like a senior engineer would: specific issues, not generic style nitpicks, with a clear accept/reject call and a 0-100 score.

### Inline, on the right line
- Reviews are posted as GitLab discussion comments positioned on the exact changed line, using the merge request's real diff refs — not a single dump comment at the top.

### Two ways to trigger it
- **Comment-triggered**: comment a configurable trigger phrase (default `/review`) on a real merge request once your GitLab webhook is wired up — the comment itself is your approval, so the review posts automatically.
- **Manual**: paste a project ID and MR number in the dashboard to analyze it on demand, review the AI's output, and click "Post to GitLab" yourself.

## How it works

```
Comment "/review" on a GitLab MR (or paste project/MR in the dashboard)
                │
       Fetch the merge request's file changes
                │
   Skip renamed/deleted files and non-code diffs
                │
    AI reviews each changed file: accept/reject, score, issues
                │
     Posted as an inline discussion comment on GitLab
```

## Tech stack

| Layer | Tools |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, Pydantic, Uvicorn |
| Database | SQLite (local), PostgreSQL (production) |
| Source control | GitLab REST API (Personal Access Token) |
| AI | OpenAI-compatible SDK (swappable between OpenAI, Gemini, Groq) |
| Frontend | React, Vite, JavaScript, CSS |
| Hosting | Render (backend + PostgreSQL), Vercel (frontend) |

## Run locally

### Backend

```bash
cd backend
python -m venv venv
./venv/Scripts/activate   # Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8080
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Setup

1. Get an LLM key (`LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL`) — see `.env.example` for free options (Gemini, Groq).
2. Create a free GitLab Personal Access Token with `api` scope at your GitLab instance's user settings (e.g. [gitlab.com/-/user_settings/personal_access_tokens](https://gitlab.com/-/user_settings/personal_access_tokens)).
3. Set `GITLAB_URL` and `GITLAB_TOKEN` in `backend/.env`.
4. To trigger reviews automatically: in your GitLab project, go to **Settings → Webhooks**, add `https://<your-backend-url>/api/webhook/gitlab`, enable the **Comments** trigger, and save. Comment your trigger phrase (default `/review`) on any merge request.

Each user brings their own GitLab token and LLM key — nothing shared, nothing public.

## What's next

- Reviewing the whole merge request as one pass instead of one comment per file.
- Support for GitHub pull requests alongside GitLab.
- A configurable review persona (strict, lenient, security-focused).

## What Review Agent will not do

- Will not post anything without either your explicit "Post to GitLab" click, or the trigger comment you typed yourself.
- Will not merge, approve, or close a merge request — it only reviews and comments.
- Will not review renamed or deleted files, or diffs it can't confidently parse.
