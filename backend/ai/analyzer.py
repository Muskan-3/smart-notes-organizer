# Uses an LLM (Google Gemini, free tier) to turn note text into a
# title, summary, tags, and category.

import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors

load_dotenv()

MODEL_NAME = "gemini-3.5-flash-lite"

# Longer notes are cut down to this many characters before being sent to the
# LLM, to keep prompts small, fast, and cheap.
MAX_INPUT_CHARS = 6000

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("LLM_API_KEY")
        if not api_key:
            raise RuntimeError(
                "LLM_API_KEY is missing. Add it to backend/.env like this:\n"
                "LLM_API_KEY=your-gemini-api-key-here"
            )
        _client = genai.Client(api_key=api_key)
    return _client


def call_llm(prompt: str) -> str:
    """
    Sends a prompt to the LLM and returns its raw text reply.
    This is the only function that talks to the API, so switching to a
    different provider later only means changing this function.
    """
    client = _get_client()

    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    except genai_errors.APIError as e:
        status = getattr(e, "code", None)
        if status in (401, 403):
            raise RuntimeError(
                "The LLM API rejected the request — check that LLM_API_KEY in .env is correct."
            )
        if status == 429:
            raise RuntimeError("The LLM API rate limit was hit. Wait a bit and try again.")
        raise RuntimeError(f"LLM API error: {e}")
    except Exception as e:
        raise RuntimeError(f"Could not reach the LLM API — check your internet connection: {e}")

    if not response.text:
        raise RuntimeError("The LLM API returned an empty response.")

    return response.text


def _strip_code_fences(text: str) -> str:
    # The model sometimes wraps its JSON in ```json ... ``` — remove that if present.
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _build_prompt(text: str) -> str:
    return (
        "You are analyzing a student's note. Reply with JSON only — no extra words, "
        "no markdown formatting — matching exactly this shape:\n"
        '{"title": "...", "summary": "...", "tags": ["...", "...", "...", "...", "..."], "category": "..."}\n\n'
        "Rules:\n"
        "- title: at most 8 words.\n"
        "- summary: at most 3 short lines (use \\n between lines).\n"
        "- tags: exactly 5 short lowercase tags.\n"
        "- category: one lowercase word, e.g. science, history, technology, finance, personal, or other.\n\n"
        f"Note text:\n{text}"
    )


def analyze_note(text: str) -> dict:
    """
    Sends note text to the LLM and returns a dict with title, summary, tags, and category.
    Raises ValueError for bad input (empty text), RuntimeError for API or
    parsing problems (including after one retry).
    """
    if not text or not text.strip():
        raise ValueError("Cannot analyze empty text.")

    # Truncate very long notes so the prompt stays small (see MAX_INPUT_CHARS above).
    truncated_text = text[:MAX_INPUT_CHARS]
    prompt = _build_prompt(truncated_text)

    required_keys = {"title", "summary", "tags", "category"}

    for attempt in range(2):  # try once, then retry once more if the JSON was invalid
        raw_reply = call_llm(prompt)
        cleaned_reply = _strip_code_fences(raw_reply)

        try:
            data = json.loads(cleaned_reply)
        except json.JSONDecodeError:
            continue

        if isinstance(data, dict) and required_keys.issubset(data.keys()):
            return data

    raise RuntimeError("The LLM did not return valid JSON after 2 attempts. Try again.")
