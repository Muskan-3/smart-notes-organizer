# Simple functions for creating, reading, and deleting notes.
# Each function opens its own short-lived database session and closes it when done.

from db.database import SessionLocal
from db.models import Note


def save_note(filename, file_type, extracted_text, title, summary, tags, category, needs_review=False):
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
            needs_review=needs_review,
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


# Fields that count as a "top tier" match — short, specific fields where a
# match is a strong signal. Everything else (summary, then extracted_text) ranks lower.
_TOP_TIER_FIELDS = {"title", "tags", "category"}


def search_notes(query):
    """
    Case-insensitive search across title, summary, tags, category, and extracted_text.
    Returns a list of (note, matched_in) tuples, where matched_in lists which
    fields matched (e.g. ["title", "tags"]). Results are ranked so title/tags/category
    matches come first, then summary, then extracted_text-only matches. Returns at most 20.
    """
    query_lower = query.lower()

    db = SessionLocal()
    try:
        all_notes = db.query(Note).order_by(Note.created_at.desc()).all()
    finally:
        db.close()

    ranked_results = []
    for note in all_notes:
        matched_in = []
        if query_lower in note.title.lower():
            matched_in.append("title")
        if any(query_lower in tag.lower() for tag in note.tags):
            matched_in.append("tags")
        if query_lower in note.category.lower():
            matched_in.append("category")
        if query_lower in note.summary.lower():
            matched_in.append("summary")
        if query_lower in note.extracted_text.lower():
            matched_in.append("extracted_text")

        if not matched_in:
            continue

        if _TOP_TIER_FIELDS & set(matched_in):
            rank = 0
        elif "summary" in matched_in:
            rank = 1
        else:
            rank = 2

        ranked_results.append((rank, note, matched_in))

    # Sort by rank only — Python's sort is stable, so notes with the same rank
    # stay in the most-recent-first order they were queried in.
    ranked_results.sort(key=lambda item: item[0])

    return [(note, matched_in) for _rank, note, matched_in in ranked_results[:20]]
