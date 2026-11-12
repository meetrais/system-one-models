"""Route a support message with a confidence gate and a catch-all option."""

from decision_client import create_client, decisions_model, print_result


def main() -> None:
    message = "I was charged twice for my order."
    with create_client() as client:
        result = client.decisions.create(
            model=decisions_model(),
            input=message,
            questions={
                "department": {
                    "type": "choice",
                    "instructions": "Which department should handle this request?",
                    "criteria": {
                        "billing": "Payments, invoices, and refunds.",
                        "technical": "Problems using the product.",
                        "shipping": "Delivery and tracking.",
                        "other": "Requests outside billing, technical support, and shipping.",
                    },
                },
            },
        )
    print(f"input: {message}\n")
    print_result(result)
    answer = result.answers["department"]
    route = answer.choice if answer.confidence >= 0.7 and answer.choice != "other" else "human_review"
    print(f"suggested queue: {route}")


if __name__ == "__main__":
    main()
