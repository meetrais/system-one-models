from typesafe_sdk import Noul

from jev_client import create_client


def describe_noul(value: float) -> str:
    return "yes" if value >= 0.5 else "no"


def main() -> None:
    client = create_client()

    ticket = (
        "Hi, I've been trying to connect my Stripe account for 3 days and "
        "the integration keeps failing. I'm losing sales. Please help ASAP."
    )

    response = client.system_one(
        state=ticket,
        questions={
            "is_urgent": Noul(
                instructions="The message conveys urgency or time-sensitivity",
            ),
        },
    )

    is_urgent = response.answers["is_urgent"].noul

    print(f"is_urgent: {is_urgent} ({describe_noul(is_urgent)} - message conveys urgency)")


if __name__ == "__main__":
    main()
