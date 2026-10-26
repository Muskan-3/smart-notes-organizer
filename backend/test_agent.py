# Quick manual test: runs the agent on sample.pdf and sample_note.jpg and
# prints each step's log, plus whether the note was flagged for review.
# Cleans up the notes it creates afterward.
#
# Run from the backend/ folder with the venv active:
#   python test_agent.py

from agent.agent import run_agent
from db.database import init_db
from db.crud import delete_note

SAMPLE_FILES = ["samples/sample.pdf", "samples/sample_note.jpg"]

if __name__ == "__main__":
    init_db()

    for file_path in SAMPLE_FILES:
        print(f"=== Running agent on {file_path} ===")
        try:
            result = run_agent(file_path)
        except (FileNotFoundError, ValueError, RuntimeError) as e:
            print(f"Error: {e}")
            print()
            continue

        for step in result["steps_log"]:
            print(f"- {step}")

        note = result["note"]
        print(f"needs_review: {note.needs_review}")

        delete_note(note.id)  # clean up so repeated test runs don't pile up notes
        print()
