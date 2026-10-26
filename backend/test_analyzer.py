# Quick manual test: run this to check the LLM analyzer on a sample paragraph.
#
# Run from the backend/ folder with the venv active:
#   python test_analyzer.py
#
# Needs LLM_API_KEY set in backend/.env.

from ai.analyzer import analyze_note

SAMPLE_TEXT = (
    "Cloud computing lets people rent computing power, storage, and software over "
    "the internet instead of buying and maintaining their own servers. Providers like "
    "AWS, Google Cloud, and Azure offer these services on demand, billed by usage. "
    "This makes it cheaper and faster for companies to scale up or down as their "
    "needs change, without large upfront hardware costs."
)

if __name__ == "__main__":
    try:
        result = analyze_note(SAMPLE_TEXT)
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")
    else:
        print("--- Analysis ---")
        print(f"Title: {result['title']}")
        print("Summary:")
        print(result["summary"])
        print(f"Tags: {', '.join(result['tags'])}")
        print(f"Category: {result['category']}")
