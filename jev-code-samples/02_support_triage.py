from typesafe_sdk import Choice, Noul, Score

from jev_client import create_client


FRUSTRATION_LEVELS = [
    "Calm, just stating facts",
    "Frustrated but civil",
    "Very angry, strong language",
]


def describe_noul(value: float) -> str:
    return "yes" if value >= 0.5 else "no"


def describe_score(value: float, levels: list[str]) -> str:
    index = round(value)
    index = max(0, min(index, len(levels) - 1))
    return levels[index]


def main() -> None:
    client = create_client()

    ticket = (
        "Hi, I've been trying to connect my Stripe account for 3 days and "
        "the integration keeps failing. I'm losing sales. Please help ASAP."
    )

    response = client.system_one(
        state=ticket,
        questions={
            "department": Choice(
                instructions="Which team should handle this",
                criteria={
                    "billing": "Payment or subscription issues",
                    "technical": "Bugs or integration problems",
                    "sales": "Pricing or account questions",
                },
            ),
            "frustration": Score(
                instructions="How frustrated the customer appears",
                criteria=FRUSTRATION_LEVELS,
            ),
            "is_urgent": Noul(
                instructions="The message conveys urgency or time-sensitivity",
            ),
        },
    )

    department = response.answers["department"].choice
    frustration = response.answers["frustration"].score
    is_urgent = response.answers["is_urgent"].noul

    print(f"department: {department} (team that should handle this ticket)")
    print(f"frustration: {frustration} ({describe_score(frustration, FRUSTRATION_LEVELS)})")
    print(f"is_urgent: {is_urgent} ({describe_noul(is_urgent)} - time-sensitive request)")


if __name__ == "__main__":
    main()
