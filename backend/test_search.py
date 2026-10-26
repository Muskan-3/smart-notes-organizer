# Quick manual test: saves 3 sample notes on different topics, searches for a
# word that should match only one of them, prints the results, then cleans up.
#
# Run from the backend/ folder with the venv active:
#   python test_search.py

from db.database import init_db
from db.crud import save_note, search_notes, delete_note

SAMPLE_NOTES = [
    {
        "filename": "python_basics.txt",
        "file_type": "pdf",
        "extracted_text": (
            "Python is a popular programming language used for web development, "
            "data science, and automation."
        ),
        "title": "Python Programming Basics",
        "summary": "Intro to Python syntax, variables, and loops.",
        "tags": ["python", "coding", "basics", "loops", "functions"],
        "category": "technology",
    },
    {
        "filename": "french_revolution.txt",
        "file_type": "pdf",
        "extracted_text": (
            "The French Revolution was a period of radical political and "
            "societal change in France."
        ),
        "title": "French Revolution Overview",
        "summary": "The French Revolution began in 1789 and ended the monarchy.",
        "tags": ["history", "france", "revolution", "monarchy", "1789"],
        "category": "history",
    },
    {
        "filename": "stock_market.txt",
        "file_type": "pdf",
        "extracted_text": (
            "The stock market allows people to buy and sell shares of publicly "
            "traded companies."
        ),
        "title": "Stock Market Fundamentals",
        "summary": "Basics of how the stock market works.",
        "tags": ["finance", "stocks", "investing", "market", "shares"],
        "category": "finance",
    },
]

if __name__ == "__main__":
    init_db()

    saved_notes = [save_note(**note) for note in SAMPLE_NOTES]
    print(f"Saved {len(saved_notes)} sample notes.")

    query = "python"
    results = search_notes(query)
    print(f"\nSearch results for '{query}': {len(results)} match(es)")
    for note, matched_in in results:
        print(f"- id={note.id}, title='{note.title}', matched_in={matched_in}")

    for note in saved_notes:
        delete_note(note.id)
    print(f"\nCleaned up {len(saved_notes)} sample notes.")
