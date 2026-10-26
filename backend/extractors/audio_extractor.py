# Transcribes speech from an audio file to text using faster-whisper.

import os
from faster_whisper import WhisperModel

# Loading the Whisper model is slow, so we build it once and reuse it
# for every call, the same way we reuse the EasyOCR reader.
_model = None

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a"}


def _get_model():
    global _model
    if _model is None:
        # "base" is a small, fast model. compute_type="int8" keeps it light
        # enough to run on a normal laptop CPU (no GPU needed).
        _model = WhisperModel("base", device="cpu", compute_type="int8")
    return _model


def extract_text_from_audio(file_path: str) -> dict:
    """
    Transcribes an audio file and returns {"text": ..., "language": ...}.
    "language" is the language code faster-whisper detected (e.g. "en").
    Raises an error with a clear message if the file is missing, the type is
    unsupported, or no speech is found.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}' for '{file_path}'. "
            f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    model = _get_model()

    try:
        segments, info = model.transcribe(file_path)
        # transcribe() returns a generator — turning it into a list runs the
        # actual transcription now, so any failure raises here, not later.
        segments = list(segments)
    except Exception as e:
        raise ValueError(f"Could not transcribe '{file_path}': {e}")

    text = " ".join(segment.text.strip() for segment in segments).strip()

    if not text:
        raise ValueError(f"No speech found in '{file_path}'.")

    return {"text": text, "language": info.language}
