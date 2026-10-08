from decision_client import answer_by_name, create_client, decisions_model, print_input, print_probabilities


def main() -> None:
    client = create_client()

    ticket = "I was charged twice for this month. Can you refund the extra payment?"

    decision = client.decisions.create(
        model=decisions_model(),
        input=ticket,
        questions=[
            {
                "type": "choice",
                "name": "department",
                "instructions": "Which department should handle this complaint?",
                "choices": [
                    {"value": "billing", "description": "Payments, invoices, and refunds."},
                    {"value": "technical", "description": "Problems using the product."},
                    {"value": "shipping", "description": "Delivery and tracking."},
                    {"value": "other", "description": "Requests outside these categories."},
                ],
            }
        ],
    )

    department = answer_by_name(decision, "department")
    print_input(ticket)
    print(f"department: {department.choice} (team that should handle this ticket)")
    print(f"confidence: {department.confidence:.2f}")
    print("probabilities:")
    print_probabilities(department)


if __name__ == "__main__":
    main()
