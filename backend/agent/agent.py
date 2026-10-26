# A simple rule-based "agent" that turns a saved file into an analyzed,
# saved note. Every decision below is a plain if/else rule — comments mark
# the spots where an LLM could make the same call later (e.g. judging
# whether a PDF is worth an OCR fallback, or whether text "looks" usable),
# instead of relying on fixed length/confidence thresholds.

import os
import tempfile

import pymupdf

from extractors.pdf_extractor import extract_text_from_pdf
from extractors.image_extractor import extract_text_from_image
from extractors.audio_extractor import extract_text_from_audio
from ai.analyzer import analyze_note
from db.crud import save_note

MIN_TEXT_LENGTH = 30       # extracted text shorter than this isn't useful
MIN_OCR_CONFIDENCE = 0.4   # OCR confidence below this gets flagged for review

EXTENSION_TO_TYPE = {
    ".pdf": "pdf",
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
    ".mp3": "audio",
    ".wav": "audio",
    ".m4a": "audio",
}


def _detect_file_type(file_path: str) -> str:
    extension = os.path.splitext(file_path)[1].lower()
    file_type = EXTENSION_TO_TYPE.get(extension)
    if file_type is None:
        raise ValueError(
            f"Unsupported file type '{extension}'. "
            f"Supported types: {', '.join(sorted(EXTENSION_TO_TYPE))}"
        )
    return file_type


def _ocr_pdf_pages(pdf_path: str) -> dict:
    """
    Fallback for scanned PDFs: renders each page as an image and runs the
    same OCR extractor we use for photos. Returns {"text", "confidence"},
    same shape as extract_text_from_image.
    """
    doc = pymupdf.open(pdf_path)
    page_texts = []
    confidences = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        for page_number, page in enumerate(doc):
            image_path = os.path.join(tmp_dir, f"page_{page_number}.png")
            page.get_pixmap(dpi=200).save(image_path)
            try:
                result = extract_text_from_image(image_path)
            except ValueError:
                continue  # this page had no readable text either, skip it
            page_texts.append(result["text"])
            confidences.append(result["confidence"])

    text = "\n".join(page_texts).strip()
    confidence = round(sum(confidences) / len(confidences), 2) if confidences else 0.0
    return {"text": text, "confidence": confidence}


def run_agent(file_path: str, original_filename: str = None) -> dict:
    """
    Runs the full pipeline on an already-saved file: detect its type, extract
    text, judge the quality, analyze it with the LLM, and save the note.

    Returns {"note": <Note row>, "steps_log": [...]}.
    Raises ValueError for problems the user can fix (bad file, unsupported
    type, no usable text), and RuntimeError for LLM/API problems.
    """
    steps_log = []

    file_type = _detect_file_type(file_path)
    steps_log.append(f"Detected file type: {file_type}")

    confidence = None  # only OCR (image, or PDF-via-OCR-fallback) gives us this

    if file_type == "pdf":
        try:
            text = extract_text_from_pdf(file_path)
            steps_log.append(f"Extracted {len(text)} characters from the PDF's text layer.")
        except ValueError:
            # Rule: no text layer usually means a scanned PDF, so try OCR on
            # its pages. An LLM could instead decide whether OCR is worth
            # trying (e.g. by looking at a rendered page first).
            steps_log.append("PDF has no text layer, trying OCR on its pages as a fallback.")
            ocr_result = _ocr_pdf_pages(file_path)
            text = ocr_result["text"]
            confidence = ocr_result["confidence"]
            if text:
                steps_log.append(
                    f"OCR fallback extracted {len(text)} characters (confidence {confidence})."
                )
            else:
                steps_log.append("OCR fallback found no readable text either.")

    elif file_type == "image":
        result = extract_text_from_image(file_path)
        text = result["text"]
        confidence = result["confidence"]
        steps_log.append(f"Extracted {len(text)} characters from the image (confidence {confidence}).")

    else:  # audio
        result = extract_text_from_audio(file_path)
        text = result["text"]
        steps_log.append(
            f"Transcribed {len(text)} characters from the audio (language: {result['language']})."
        )

    # Rule: text shorter than this isn't worth analyzing — stop here.
    # An LLM could instead judge the text's quality directly, not just its length.
    if len(text.strip()) < MIN_TEXT_LENGTH:
        steps_log.append(f"Extracted text is too short ({len(text.strip())} characters) — stopping.")
        if file_type == "pdf":
            raise ValueError("This PDF looks scanned and has no readable text, even after trying OCR.")
        raise ValueError("Not enough readable text was found in this file.")

    # Rule: low OCR confidence doesn't stop the pipeline — it just flags the
    # note so a human can double check it later.
    needs_review = False
    if confidence is not None and confidence < MIN_OCR_CONFIDENCE:
        needs_review = True
        steps_log.append(f"OCR confidence is low ({confidence}), flagging this note for review.")

    try:
        analysis = analyze_note(text)
    except RuntimeError as e:
        # analyze_note already retries once internally for bad JSON replies;
        # this retries the whole call again for a temporary API-level error.
        steps_log.append(f"Analysis failed ({e}), retrying once.")
        try:
            analysis = analyze_note(text)
            steps_log.append("Retry succeeded.")
        except RuntimeError as retry_error:
            steps_log.append(f"Retry also failed ({retry_error}).")
            raise

    steps_log.append(f"Analyzed note: title='{analysis['title']}'.")

    note = save_note(
        filename=original_filename or os.path.basename(file_path),
        file_type=file_type,
        extracted_text=text,
        title=analysis["title"],
        summary=analysis["summary"],
        tags=analysis["tags"],
        category=analysis["category"],
        needs_review=needs_review,
    )
    steps_log.append(f"Saved note id {note.id}" + (" (flagged for review)." if needs_review else "."))

    return {"note": note, "steps_log": steps_log}
