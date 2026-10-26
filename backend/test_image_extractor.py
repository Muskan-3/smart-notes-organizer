# Quick manual test: run this to check the image OCR extractor against a sample file.
# Put an image named "sample_note.jpg" in backend/samples/ before running.
#
# Run from the backend/ folder with the venv active:
#   python test_image_extractor.py
#
# Note: the first run downloads EasyOCR's text-detection models (one-time, needs internet).

from extractors.image_extractor import extract_text_from_image

SAMPLE_IMAGE_PATH = "samples/sample_note.jpg"

if __name__ == "__main__":
    try:
        result = extract_text_from_image(SAMPLE_IMAGE_PATH)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
    else:
        print("--- Extracted text ---")
        print(result["text"])
        print("-----------------------")
        print(f"Confidence: {result['confidence']}")
