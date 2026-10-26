# Quick manual test: run this to check the PDF extractor against a sample file.
# Put a PDF named "sample.pdf" in backend/samples/ before running.
#
# Run from the backend/ folder with the venv active:
#   python test_pdf_extractor.py

from extractors.pdf_extractor import extract_text_from_pdf

SAMPLE_PDF_PATH = "samples/sample.pdf"

if __name__ == "__main__":
    try:
        text = extract_text_from_pdf(SAMPLE_PDF_PATH)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
    else:
        print("--- Extracted text ---")
        print(text)
        print("-----------------------")
        print(f"Total characters extracted: {len(text)}")
