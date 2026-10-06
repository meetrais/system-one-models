from typesafe_sdk import Choice, Noul, Score

from jev_client import create_client


FIT_LEVELS = [
    "Weak fit or unclear need",
    "Possible fit with some buying signals",
    "Strong fit with clear volume, timeline, and budget",
]


def describe_noul(value: float) -> str:
    return "yes" if value >= 0.5 else "no"


def describe_score(value: float, levels: list[str]) -> str:
    index = round(value)
    index = max(0, min(index, len(levels) - 1))
    return levels[index]


def main() -> None:
    client = create_client()

    lead = (
        "We are evaluating Jev for routing 50,000 monthly support messages. "
        "We need a production pilot this quarter and have budget approved."
    )

    response = client.system_one(
        state=lead,
        questions={
            "segment": Choice(
                instructions="Which sales segment best fits this lead?",
                criteria={
                    "self_serve": "Small user or hobby project",
                    "startup": "Small company with early production needs",
                    "enterprise": "High-volume or strategic production use case",
                },
            ),
            "fit_score": Score(
                instructions="How strong is this lead as a sales opportunity?",
                criteria=FIT_LEVELS,
            ),
            "has_budget": Noul(
                instructions="The message says budget is available or approved",
            ),
            "near_term_timeline": Noul(
                instructions="The message indicates a near-term buying timeline",
            ),
        },
    )

    segment = response.answers["segment"].choice
    fit_score = response.answers["fit_score"].score
    has_budget = response.answers["has_budget"].noul
    near_term_timeline = response.answers["near_term_timeline"].noul

    print(f"segment: {segment} (sales segment that best fits this lead)")
    print(f"fit_score: {fit_score} ({describe_score(fit_score, FIT_LEVELS)})")
    print(f"has_budget: {has_budget} ({describe_noul(has_budget)} - budget is available)")
    print(
        "near_term_timeline: "
        f"{near_term_timeline} ({describe_noul(near_term_timeline)} - buying timeline is near-term)"
    )


if __name__ == "__main__":
    main()
