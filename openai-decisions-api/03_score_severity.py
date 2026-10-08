from decision_client import (
    answer_by_name,
    create_client,
    decisions_model,
    describe_score,
    print_input,
    print_probabilities,
)


SEVERITY_LEVELS = [
    "Cosmetic",
    "Workaround available",
    "Fully blocked",
]


def main() -> None:
    client = create_client()

    issue = "Checkout is failing for every customer. We have not processed an order in 20 minutes."

    decision = client.decisions.create(
        model=decisions_model(),
        input=issue,
        questions=[
            {
                "type": "score",
                "name": "severity",
                "instructions": "How severe is this issue?",
                "levels": [
                    {"label": "Cosmetic", "description": "Appearance only; no lost functionality."},
                    {"label": "Workaround available", "description": "A task fails, but another way works."},
                    {"label": "Fully blocked", "description": "A task fails with no workaround."},
                ],
            }
        ],
    )

    severity = answer_by_name(decision, "severity")
    print_input(issue)
    print(f"severity: {severity.score:.2f} ({describe_score(severity.score, SEVERITY_LEVELS)})")
    print(f"confidence: {severity.confidence:.2f}")
    print("probabilities:")
    print_probabilities(severity)


if __name__ == "__main__":
    main()
