from typesafe_sdk import Choice, Noul, Score

from jev_client import create_client


FRUSTRATION_LEVELS = [
    "Calm, just stating facts",
    "Frustrated but civil",
    "Very angry, strong language",
]

QUESTIONS = {
    "department": Choice(
        instructions="Which team should handle this message?",
        criteria={
            "billing": "Payment, invoice, or subscription issues",
            "technical": "Bugs, errors, integration, or product issues",
            "sales": "Pricing, plan, purchase, or account expansion questions",
        },
    ),
    "frustration": Score(
        instructions="How frustrated does the sender appear?",
        criteria=FRUSTRATION_LEVELS,
    ),
    "is_urgent": Noul(
        instructions="The message conveys urgency or time-sensitivity",
    ),
}


def describe_noul(value: float) -> str:
    return "yes" if value >= 0.5 else "no"


def describe_score(value: float, levels: list[str]) -> str:
    index = round(value)
    index = max(0, min(index, len(levels) - 1))
    return levels[index]


def main() -> None:
    client = create_client()

    print("Paste a message to classify. Type 'exit' to quit.")

    while True:
        state = input("\nMessage: ").strip()
        if state.lower() in {"exit", "quit"}:
            break

        response = client.system_one(state=state, questions=QUESTIONS)

        department = response.answers["department"].choice
        frustration = response.answers["frustration"].score
        is_urgent = response.answers["is_urgent"].noul

        print(f"department: {department} (team that should handle this message)")
        print(f"frustration: {frustration} ({describe_score(frustration, FRUSTRATION_LEVELS)})")
        print(f"is_urgent: {is_urgent} ({describe_noul(is_urgent)} - time-sensitive request)")


if __name__ == "__main__":
    main()
