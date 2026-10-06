from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from typesafe_sdk import TypeSafeClient


def create_client() -> TypeSafeClient:
    sample_dir = Path(__file__).resolve().parent
    load_dotenv(sample_dir / ".env")
    load_dotenv(sample_dir.parent / ".env")

    api_key = os.getenv("TYPESAFE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing API key. Set TYPESAFE_API_KEY in .env."
        )

    return TypeSafeClient(api_key=api_key)
