from decision_client import (
    answer_by_name,
    create_client,
    decisions_model,
    describe_probability,
    describe_score,
    print_input,
    print_probabilities,
)


SEVERITY_LEVELS = [
    "Low",
    "Medium",
    "High",
]


def main() -> None:
    client = create_client()

    ticket = (
        "Our CSV export fails for one teammate in Safari, but the rest of the team "
        "can still export from Chrome. We need this fixed before tomorrow's report."
    )

    decision = client.decisions.create(
        model=decisions_model(),
        input=ticket,
        questions=[
            {
                "type": "choice",
                "name": "department",
                "instructions": "Which team should handle this support ticket?",
                "choices": [
                    {"value": "billing", "description": "Payments, invoices, and refunds."},
                    {"value": "technical", "description": "Bugs, errors, integrations, or product issues."},
                    {"value": "account", "description": "Login, identity, or account access issues."},
                    {"value": "other", "description": "Requests outside these categories."},
                ],
            },
            {
                "type": "score",
                "name": "severity",
                "instructions": "How severe is this issue?",
                "levels": [
                    {"label": "Low", "description": "Minor issue or feature request."},
                    {"label": "Medium", "description": "Important task affected, but a workaround exists."},
                    {"label": "High", "description": "Critical workflow blocked with no workaround."},
                ],
            },
            {
                "type": "predicate",
                "name": "deadline_pressure",
                "instructions": "Does the message mention deadline pressure or time sensitivity?",
            },
        ],
    )

    department = answer_by_name(decision, "department")
    severity = answer_by_name(decision, "severity")
    deadline_pressure = answer_by_name(decision, "deadline_pressure")

    print_input(ticket)
    print(f"department: {department.choice} (team that should handle this ticket)")
    print(f"department confidence: {department.confidence:.2f}")
    print("department probabilities:")
    print_probabilities(department)
    print()
    print(f"severity: {severity.score:.2f} ({describe_score(severity.score, SEVERITY_LEVELS)})")
    print(f"severity confidence: {severity.confidence:.2f}")
    print("severity probabilities:")
    print_probabilities(severity)
    print()
    print(
        "deadline_pressure: "
        f"{deadline_pressure.probability:.2f} "
        f"({describe_probability(deadline_pressure.probability)} - time-sensitive request)"
    )


if __name__ == "__main__":
    main()
