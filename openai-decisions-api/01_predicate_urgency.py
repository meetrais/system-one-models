from decision_client import (
    answer_by_name,
    create_client,
    decisions_model,
    describe_probability,
    print_input,
)


def main() -> None:
    client = create_client()

    ticket = (
        "Hi, I've been trying to connect my Stripe account for 3 days and "
        "the integration keeps failing. I'm losing sales. Please help ASAP."
    )

    decision = client.decisions.create(
        model=decisions_model(),
        input=ticket,
        questions=[
            {
                "type": "predicate",
                "name": "is_urgent",
                "instructions": "Does this message convey urgency or time-sensitivity?",
            }
        ],
    )

    urgency = answer_by_name(decision, "is_urgent")
    print_input(ticket)
    print(f"is_urgent: {urgency.probability:.2f} ({describe_probability(urgency.probability)} - time-sensitive request)")


if __name__ == "__main__":
    main()
