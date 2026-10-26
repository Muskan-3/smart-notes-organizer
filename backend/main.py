# This is the entry point of our backend API.
# It accepts file uploads, extracts text, asks the LLM to analyze it, and
# stores/retrieves the results from the database.

import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from db.database import init_db
from db.crud import save_note, list_notes, get_note, delete_note
from extractors.pdf_extractor import extract_text_from_pdf
from extractors.image_extractor import extract_text_from_image
from extractors.audio_extractor import extract_text_from_audio
from ai.analyzer import analyze_note

UPLOAD_DIR = "uploads"

# Maps a file extension to the note's file_type. Also used to reject
# unsupported file types before we try to process anything.
EXTENSION_TO_TYPE = {
    ".pdf": "pdf",
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
    ".mp3": "audio",
    ".wav": "audio",
    ".m4a": "audio",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the server starts, before it accepts any requests.
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

# Lets the Next.js frontend (running on localhost:3000) call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    # A simple health-check style response.
    return {"message": "Notes Organizer is running"}


def _extract_text(file_type: str, file_path: str) -> str:
    """Runs the extractor that matches the file type and returns plain text."""
    if file_type == "pdf":
        return extract_text_from_pdf(file_path)
    if file_type == "image":
        return extract_text_from_image(file_path)["text"]
    return extract_text_from_audio(file_path)["text"]  # only "audio" is left


def _note_to_dict(note) -> dict:
    """Converts a Note database row into a plain dict FastAPI can return as JSON."""
    return {
        "id": note.id,
        "filename": note.filename,
        "file_type": note.file_type,
        "extracted_text": note.extracted_text,
        "title": note.title,
        "summary": note.summary,
        "tags": note.tags,
        "category": note.category,
        "created_at": note.created_at.isoformat() if note.created_at else None,
    }


@app.post("/upload")
async def upload_note(file: UploadFile = File(...)):
    original_name = file.filename or "upload"
    extension = os.path.splitext(original_name)[1].lower()

    file_type = EXTENSION_TO_TYPE.get(extension)
    if file_type is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{extension}'. "
            f"Supported types: {', '.join(sorted(EXTENSION_TO_TYPE))}",
        )

    # Save with a random filename so two uploads never collide or overwrite each other.
    safe_filename = f"{uuid.uuid4().hex}{extension}"
    saved_path = os.path.join(UPLOAD_DIR, safe_filename)

    contents = await file.read()
    with open(saved_path, "wb") as saved_file:
        saved_file.write(contents)

    try:
        extracted_text = _extract_text(file_type, saved_path)
    except (FileNotFoundError, ValueError) as e:
        # Bad/unreadable/empty file — the user should fix the file and retry.
        raise HTTPException(status_code=400, detail=str(e))

    try:
        analysis = analyze_note(extracted_text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # LLM problem (bad key, rate limit, no internet, bad JSON) — not the user's file.
        raise HTTPException(status_code=502, detail=str(e))

    note = save_note(
        filename=original_name,
        file_type=file_type,
        extracted_text=extracted_text,
        title=analysis["title"],
        summary=analysis["summary"],
        tags=analysis["tags"],
        category=analysis["category"],
    )

    return _note_to_dict(note)


@app.get("/notes")
def get_all_notes():
    return [_note_to_dict(note) for note in list_notes()]


@app.get("/notes/{note_id}")
def get_one_note(note_id: int):
    note = get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found.")
    return _note_to_dict(note)


@app.delete("/notes/{note_id}")
def delete_one_note(note_id: int):
    was_deleted = delete_note(note_id)
    if not was_deleted:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found.")
    return {"message": f"Note {note_id} deleted."}
