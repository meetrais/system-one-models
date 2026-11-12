"""Show expected severity, normalized severity, and the most likely rubric level."""

from decision_client import create_client, decisions_model, print_result


def main() -> None:
    message = "Export fails in Safari but works in Chrome."
    with create_client() as client:
        result = client.decisions.create(
            model=decisions_model(),
            input=message,
            questions={
                "severity": {
                    "type": "score",
                    "instructions": "How severe is this issue for the user?",
                    "criteria": [
                        "Cosmetic: appearance only, no lost functionality.",
                        "Workaround available: a task fails, but another way works.",
                        "Fully blocked: a task fails with no workaround.",
                    ],
                },
            },
        )
    print(f"input: {message}\n")
    print_result(result)


if __name__ == "__main__":
    main()
