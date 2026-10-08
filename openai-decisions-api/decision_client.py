from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


DEFAULT_MODEL = "gpt-6-luna"


def create_client() -> OpenAI:
    sample_dir = Path(__file__).resolve().parent
    load_dotenv(sample_dir / ".env")
    load_dotenv(sample_dir.parent / ".env")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY. Add it to openai-decisions-api/.env or the repo root .env.")

    return OpenAI(api_key=api_key)


def decisions_model() -> str:
    return os.getenv("OPENAI_DECISIONS_MODEL", DEFAULT_MODEL)


def answer_by_name(decision: Any, name: str) -> Any:
    for answer in decision.answers:
        if getattr(answer, "name", None) == name:
            return answer
    raise KeyError(f"No answer named {name!r}.")


def describe_probability(value: float, threshold: float = 0.5) -> str:
    return "yes" if value >= threshold else "no"


def describe_score(score: float, labels: list[str]) -> str:
    index = round(score)
    index = max(0, min(index, len(labels) - 1))
    return labels[index]


def print_probabilities(answer: Any) -> None:
    probabilities = getattr(answer, "probabilities", None) or []
    for item in probabilities:
        label = getattr(item, "label", None) or getattr(item, "value", None)
        print(f"  - {label}: {item.probability:.2f}")


def print_input(value: str) -> None:
    print("input:")
    print(value)
    print()
    print("output:")
