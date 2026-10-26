# Reads text out of an image (photo of a handwritten or printed note) using EasyOCR.

import os
import sys

# On some Windows setups, the console can't print the block character ("█")
# that EasyOCR's model-download progress bar uses, which crashes the download.
# Switching stdout to UTF-8 avoids that.
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import easyocr

# EasyOCR's reader loads a language model, which is slow to create.
# We build it once and reuse it for every call, instead of once per call.
_reader = None

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}


def _get_reader():
    global _reader
    if _reader is None:
        # gpu=False so this runs on a normal laptop with no graphics card needed.
        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


def extract_text_from_image(file_path: str) -> dict:
    """
    Reads an image and returns {"text": ..., "confidence": ...}.
    "confidence" is the average confidence (0 to 1) across all detected text, rounded to 2 decimals.
    Raises an error with a clear message if the file is missing, the type is unsupported,
    or no text is found.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}' for '{file_path}'. "
            f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    reader = _get_reader()

    try:
        # Each result is (bounding_box, text, confidence).
        results = reader.readtext(file_path)
    except Exception as e:
        raise ValueError(f"Could not read '{file_path}': {e}")

    if not results:
        raise ValueError(f"No text found in '{file_path}'.")

    lines = [text for (_box, text, _confidence) in results]
    confidences = [confidence for (_box, _text, confidence) in results]

    full_text = "\n".join(lines).strip()
    if not full_text:
        raise ValueError(f"No text found in '{file_path}'.")

    average_confidence = round(sum(confidences) / len(confidences), 2)

    return {"text": full_text, "confidence": average_confidence}
