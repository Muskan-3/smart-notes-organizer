# Pulls plain text out of a PDF file using pypdf.

import os
from pypdf import PdfReader
from pypdf.errors import PdfReadError


def extract_text_from_pdf(file_path: str) -> str:
    """
    Reads a PDF and returns all of its text as one string.
    Raises an error with a clear message if the file is missing,
    unreadable, or has no extractable text.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)
    except PdfReadError as e:
        raise ValueError(f"Could not read '{file_path}' — the PDF looks corrupted or invalid: {e}")

    if len(reader.pages) == 0:
        raise ValueError(f"'{file_path}' has no pages.")

    # Collect text from every page, skipping pages that fail individually.
    text_chunks = []
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception as e:
            raise ValueError(f"Failed to read page {page_number} of '{file_path}': {e}")
        text_chunks.append(page_text)

    full_text = "\n".join(text_chunks).strip()

    if not full_text:
        raise ValueError(
            f"No extractable text found in '{file_path}'. "
            "It may be a scanned/handwritten PDF (needs OCR) or an empty document."
        )

    return full_text
