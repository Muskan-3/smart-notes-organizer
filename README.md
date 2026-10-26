# Agentic AI-Powered Smart Notes Organizer

A college project that takes handwritten note photos, PDFs, and audio recordings,
pulls the text out of them, uses an LLM to write a summary with tags and a category,
saves everything in a database, and lets you search your notes later.

## What it does
1. You upload a photo, PDF, or audio recording of your notes.
2. The backend reads the text (OCR for images, text extraction for PDFs, speech-to-text for audio).
3. An LLM summarizes the content and suggests tags + a category.
4. Everything is saved in a database.
5. You can search and browse your notes from the web frontend.

## Tech stack
- **Backend:** Python + FastAPI
- **OCR (images/handwriting):** EasyOCR
- **PDF text extraction:** pypdf
- **Audio transcription:** faster-whisper
- **Summaries/tags/category:** an LLM API
- **Database:** SQLite (to start), PostgreSQL later
- **Frontend:** Next.js + Tailwind CSS

## Project status
Folder structure only right now — no app code yet. Code is being built one small
step at a time; see [CLAUDE.md](CLAUDE.md) for the working context and folder layout.

## Folder structure
```
inHouse_project/
├── backend/     # FastAPI app, OCR/PDF/audio processing, LLM calls, database
├── frontend/    # Next.js + Tailwind web app
├── README.md
└── CLAUDE.md
```

## Setup
Setup instructions will be added here once the backend and frontend code exist.
