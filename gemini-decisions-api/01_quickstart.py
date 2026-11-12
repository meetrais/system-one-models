"""Ask a single yes/no question using Gemini Decision 1."""

from decision_client import create_client, decisions_model, print_result


def main() -> None:
    message = "The blue mug I ordered on Monday arrived cracked on Wednesday."
    with create_client() as client:
        result = client.decisions.create(
            model=decisions_model(),
            input=message,
            questions={
                "is_damaged": {
                    "type": "noul",
                    "instructions": "Did the item arrive damaged?",
                },
            },
        )
    print(f"input: {message}\n")
    print_result(result)


if __name__ == "__main__":
    main()
