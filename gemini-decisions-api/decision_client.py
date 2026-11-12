"""Shared configuration and display helpers for the Gemini Decisions samples."""

from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from dotenv import load_dotenv
from google import genai


DEFAULT_MODEL = "gemini-decision-1"
SAMPLE_DIR = Path(__file__).resolve().parent


def create_client() -> genai.Client:
    """Use the Developer API, preserving process > local .env > root .env."""
    load_dotenv(SAMPLE_DIR / ".env", override=False)
    load_dotenv(SAMPLE_DIR.parent / ".env", override=False)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not api_key.strip() or api_key == "your_gemini_api_key":
        raise RuntimeError(
            "Missing GEMINI_API_KEY. Set it in the environment, "
            "gemini-decisions-api/.env, or the repository root .env."
        )
    client = genai.Client(
        api_key=api_key,
        vertexai=False,
        http_options={"api_version": "v1beta"},
    )
    if not callable(getattr(getattr(client, "decisions", None), "create", None)):
        client.close()
        raise RuntimeError(
            'Gemini Decisions requires google-genai>=3.2.0. Run '
            'python -m pip install --upgrade "google-genai>=3.2.0".'
        )
    return client


def decisions_model() -> str:
    """Call after create_client(), which loads environment files."""
    return os.getenv("GEMINI_DECISIONS_MODEL", DEFAULT_MODEL)


def print_result(result: Any) -> None:
    """Print typed values, full distributions, and input/output token usage."""
    for name, answer in result.answers.items():
        print(f"{name} ({answer.type}):")
        if answer.type == "noul":
            print(f"  P(yes): {answer.noul:.3f}; P(no): {1 - answer.noul:.3f}")
        elif answer.type == "choice":
            print(f"  choice: {answer.choice}")
        elif answer.type == "score":
            print(f"  expected score: {answer.score:.3f}")
            level = max(answer.probabilities, key=answer.probabilities.get)
            print(f"  most likely level: {level} - {answer.legend[level]}")
            highest_index = max(int(index) for index in answer.legend)
            print(f"  normalized score: {answer.score / highest_index:.3f}")
        print(f"  confidence: {answer.confidence:.3f}")
        if answer.type in {"choice", "score"}:
            for label, probability in answer.probabilities.items():
                print(f"    {label}: {probability:.3f}")
    if result.usage is not None:
        print("usage:")
        print(f"  input tokens: {result.usage.total_input_tokens}")
        print(f"  output tokens: {result.usage.total_output_tokens}")
        print(f"  total tokens: {result.usage.total_tokens}")
        for entry in result.usage.input_tokens_by_modality or []:
            print(f"    {entry.modality}: {entry.tokens}")


def media_block(
    source: str, media_type: str, mime_type: str, resolution: str | None = None
) -> dict[str, str]:
    """Build inline local media or an HTTPS/Files API URI block."""
    if media_type not in {"image", "audio", "video", "document"}:
        raise ValueError("Media type must be image, audio, video, or document.")
    if media_type == "document":
        valid_mime = mime_type == "application/pdf"
    else:
        valid_mime = mime_type.startswith(f"{media_type}/")
    if not valid_mime:
        raise ValueError("MIME type must match the media type; documents must be PDF.")
    block = {"type": media_type, "mime_type": mime_type}
    if resolution is not None:
        allowed = {"low", "medium", "high"}
        if media_type == "image":
            allowed.add("ultra_high")
        if media_type not in {"image", "video"} or resolution not in allowed:
            raise ValueError("Resolution is supported on images and videos only; ultra_high is image-only.")
        block["resolution"] = resolution
    parsed = urlparse(source)
    if parsed.scheme == "https":
        hostname = (parsed.hostname or "").lower()
        if not hostname or hostname in {"youtu.be", "youtube.com"} or hostname.endswith(".youtube.com"):
            raise ValueError("Use an HTTPS media URL or Files API URI, not a YouTube URL.")
        block["uri"] = source
    elif "://" in source:
        raise ValueError("Remote media requires HTTPS; gs:// and YouTube URLs are unsupported.")
    else:
        path = Path(source)
        limit_mb = 50 if media_type == "document" else 100
        if path.stat().st_size > limit_mb * 1_000_000:
            raise ValueError(f"Inline {media_type} exceeds the {limit_mb} MB limit; use a Files API URI.")
        data = path.read_bytes()
        if not data:
            raise ValueError("Media file must not be empty.")
        block["data"] = base64.b64encode(data).decode("ascii")
    return block
