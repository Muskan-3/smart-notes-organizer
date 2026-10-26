# Quick manual test: saves one sample note, lists notes, fetches it by id,
# deletes it, and prints the result of each step.
#
# Run from the backend/ folder with the venv active:
#   python test_db.py

from db.database import init_db
from db.crud import save_note, list_notes, get_note, delete_note

# Reusing the result test_analyzer.py already produced, so this test doesn't
# need to call the LLM API again.
SAMPLE_NOTE = {
    "filename": "cloud_computing_notes.txt",
    "file_type": "pdf",
    "extracted_text": (
        "Cloud computing lets people rent computing power, storage, and software "
        "over the internet instead of buying and maintaining their own servers."
    ),
    "title": "Introduction to Cloud Computing",
    "summary": (
        "Rent computing power and storage over the internet.\n"
        "Providers like AWS and Azure bill based on usage.\n"
        "Enables fast, cost-effective scaling without hardware."
    ),
    "tags": ["cloud", "servers", "infrastructure", "aws", "technology"],
    "category": "technology",
}

if __name__ == "__main__":
    init_db()
    print("Database ready.")

    note = save_note(**SAMPLE_NOTE)
    print(f"Saved note: id={note.id}, title='{note.title}'")

    all_notes = list_notes()
    print(f"Total notes in database: {len(all_notes)}")

    fetched = get_note(note.id)
    print(f"Fetched note: title='{fetched.title}', tags={fetched.tags}")

    was_deleted = delete_note(note.id)
    print(f"Deleted note id={note.id}: {was_deleted}")

    still_there = get_note(note.id)
    print(f"Note still in database after delete: {still_there is not None}")
