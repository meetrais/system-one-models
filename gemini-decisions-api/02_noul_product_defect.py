"""Separate a product defect from a preference using explicit yes/no criteria."""

from decision_client import create_client, decisions_model, print_result


def main() -> None:
    message = "Customer returned the sweater because they preferred green over blue."
    with create_client() as client:
        result = client.decisions.create(
            model=decisions_model(),
            input=message,
            questions={
                "is_defect": {
                    "type": "noul",
                    "instructions": "Is the customer reporting a product defect?",
                    "criteria": {
                        "true_description": "The product itself is broken or faulty.",
                        "false_description": "Preference, sizing, shipping, or pricing complaint.",
                    },
                },
            },
        )
    print(f"input: {message}\n")
    print_result(result)
    answer = result.answers["is_defect"]
    # Confidence alone is insufficient: confident 'no' also has high confidence.
    print(f"defect detected: {answer.noul >= 0.9}")


if __name__ == "__main__":
    main()
