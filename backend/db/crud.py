# Simple functions for creating, reading, and deleting notes.
# Each function opens its own short-lived database session and closes it when done.

from db.database import SessionLocal
from db.models import Note


def save_note(filename, file_type, extracted_text, title, summary, tags, category):
    """Creates a new note row and returns it."""
    db = SessionLocal()
    try:
        note = Note(
            filename=filename,
            file_type=file_type,
            extracted_text=extracted_text,
            title=title,
            summary=summary,
            tags=tags,
            category=category,
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        return note
    finally:
        db.close()


def list_notes():
    """Returns all notes, most recently created first."""
    db = SessionLocal()
    try:
        return db.query(Note).order_by(Note.created_at.desc()).all()
    finally:
        db.close()


def get_note(note_id):
    """Returns one note by id, or None if no note has that id."""
    db = SessionLocal()
    try:
        return db.query(Note).filter(Note.id == note_id).first()
    finally:
        db.close()


def delete_note(note_id):
    """Deletes a note by id. Returns True if it was deleted, False if it didn't exist."""
    db = SessionLocal()
    try:
        note = db.query(Note).filter(Note.id == note_id).first()
        if note is None:
            return False
        db.delete(note)
        db.commit()
        return True
    finally:
        db.close()
