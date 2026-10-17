"""Configuration and terminal output shared by the JevEval examples."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


def parse_args(description: str, *, trajectory: bool = False) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--strict", action="store_true", help="Require every applicable question to pass.")
    parser.add_argument("--score-only", action="store_true", help="Disable the passing threshold.")
    parser.add_argument("--verbose", action="store_true", help="Print DeepEval's question-level logs.")
    if not trajectory:
        parser.add_argument("--evaluate", action="store_true", help="Use DeepEval evaluate() instead of measure().")
    args = parser.parse_args()
    if args.strict and args.score_only:
        parser.error("--strict and --score-only cannot be combined: strict mode sets threshold to 1.")
    return args


def configure_environment() -> str:
    """Load local configuration before importing DeepEval and return the model."""
    sample_dir = Path(__file__).resolve().parent
    load_dotenv(sample_dir / ".env")
    load_dotenv(sample_dir.parent / ".env")
    os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "YES")
    os.environ.setdefault("DEEPEVAL_NO_INSPECT_PROMPT", "1")
    key = os.getenv("TYPESAFE_API_KEY", "").strip()
    if not key or key in {"your_api_key_here", "your_real_key"}:
        raise SystemExit("Set TYPESAFE_API_KEY in JevEval/.env, the repository root .env, or your environment.")
    return os.getenv("TYPESAFE_DEFAULT_MODEL", "jev-latest")


def metric_options(args: argparse.Namespace, model: str) -> dict[str, Any]:
    return {
        "system_one_model": model,
        "threshold": None if args.score_only else 0.5,
        "strict_mode": args.strict,
        "verbose_mode": args.verbose,
        "include_reason": True,
    }


def print_result(metric: Any) -> None:
    print(f"\nMetric: {metric.name}")
    print(f"Score: {metric.score:.4f}")
    if metric.threshold is None:
        print("Mode: score only (no pass/fail threshold)")
    else:
        print(f"Threshold: {metric.threshold:.2f}; passed: {metric.is_successful()}")
    print(f"\nReason:\n{metric.reason}")
    print("\nScore breakdown:")
    print(json.dumps(metric.score_breakdown, indent=2, ensure_ascii=False))


def run_case(metric: Any, test_case: Any, *, use_evaluate: bool = False) -> None:
    if use_evaluate:
        from deepeval import evaluate
        from deepeval.evaluate import DisplayConfig

        evaluate(
            test_cases=[test_case],
            metrics=[metric],
            display_config=DisplayConfig(inspect_after_run=False),
        )
    else:
        metric.measure(test_case)
        print_result(metric)
