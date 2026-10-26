# Project context for Claude

## What this is
"Agentic AI-Powered Smart Notes Organizer" — a college project built by a beginner.
It takes handwritten note photos, PDFs, and audio recordings, extracts the text,
uses an LLM to generate a summary, tags, and a category, saves everything in a
database, and lets the user search their notes.

## Tech stack
- Backend: Python + FastAPI
- OCR (handwriting/images): EasyOCR
- PDF text extraction: pypdf
- Audio transcription: faster-whisper
- Summaries/tags/category: an LLM API
- Database: SQLite first, PostgreSQL later
- Frontend: Next.js + Tailwind CSS

## Folder structure
```
inHouse_project/
├── backend/     # FastAPI app, OCR/PDF/audio processing, LLM calls, database
├── frontend/    # Next.js + Tailwind web app
├── README.md
└── CLAUDE.md
```

## Rules for working with this user
- The user is a **beginner**. Explain each step in simple English.
- Build in **small steps** — add one piece at a time and **wait for the user to
  test it** before moving on to the next step.
- Keep code **simple** and add **short comments** explaining non-obvious parts.
- Never put API keys or secrets in code — always use a `.env` file, and make sure
  `.env` is listed in `.gitignore`.
- Do not add extra features, abstractions, or files beyond what the current step
  asks for.

## Current state
Folder structure only (`backend/`, `frontend/`, `README.md`, `CLAUDE.md`).
No application code has been written yet.
