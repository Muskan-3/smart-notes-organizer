# Quick manual test: run this to check the audio transcriber against a sample file.
# Put an audio file named "sample_audio.mp3" in backend/samples/ before running.
#
# Run from the backend/ folder with the venv active:
#   python test_audio_extractor.py
#
# Note: the first run downloads the Whisper "base" model (one-time, needs internet).

from extractors.audio_extractor import extract_text_from_audio

SAMPLE_AUDIO_PATH = "samples/sample_audio.mp3"

if __name__ == "__main__":
    try:
        result = extract_text_from_audio(SAMPLE_AUDIO_PATH)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
    else:
        print("--- Transcribed text ---")
        print(result["text"])
        print("-----------------------")
        print(f"Detected language: {result['language']}")
