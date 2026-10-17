"""Fixed interactions to evaluate; generating them requires no LLM call."""

from deepeval.test_case import ConversationalTestCase, LLMTestCase, ToolCall, Turn


def weather_case() -> LLMTestCase:
    return LLMTestCase(
        input="What's the weather in Paris right now?",
        actual_output="It's 18 degrees C and sunny in Paris, with a light breeze and around 40% humidity.",
        tools_called=[
            ToolCall(
                name="get_weather",
                input_parameters={"city": "Paris"},
                output={"temp_c": 18, "condition": "sunny"},
            )
        ],
    )


def refund_case() -> ConversationalTestCase:
    return ConversationalTestCase(
        scenario="A customer asks for a refund on a late order.",
        expected_outcome="The refund amount is confirmed.",
        turns=[
            Turn(role="user", content="My order arrived a week late. I want a refund."),
            Turn(role="assistant", content="Sorry about that. What is your order number?"),
            Turn(role="user", content="It's 4471. How much do I get back?"),
            Turn(role="assistant", content="You'll receive a refund within 5-7 days."),
            Turn(role="user", content="ok thanks"),
        ],
    )


def rubric_case(rubric: str, *, conversational: bool = False):
    """Return the fixed single-turn or conversation fixture for a custom rubric."""
    if rubric == "correctness":
        if conversational:
            return ConversationalTestCase(
                scenario="A customer asks when an order ships and whether tracking is included.",
                expected_outcome="Confirm dispatch within two business days and tracking by email.",
                turns=[
                    Turn(role="user", content="When will my order ship?"),
                    Turn(role="assistant", content="It will dispatch within two business days."),
                    Turn(role="user", content="Will I get tracking?"),
                    Turn(role="assistant", content="Yes, tracking will be sent by email. Delivery tomorrow is guaranteed."),
                ],
            )
        return LLMTestCase(
            input="When will my order ship, and will I get tracking?",
            actual_output="It will dispatch within two business days. Tracking arrives by email. Delivery tomorrow is guaranteed.",
            expected_output="The order dispatches within two business days. Tracking is sent by email.",
        )
    if rubric == "clarity":
        if conversational:
            return ConversationalTestCase(
                scenario="Explain caching to someone unfamiliar with programming.",
                turns=[
                    Turn(role="user", content="What is caching?"),
                    Turn(role="assistant", content="Caching saves a copy of information so it can be reused quickly."),
                    Turn(role="user", content="Can that copy become outdated?"),
                    Turn(role="assistant", content="Yes. The saved copy can lag behind the original, so it needs refreshing."),
                ],
            )
        return LLMTestCase(
            input="What is caching? Explain it to a beginner.",
            actual_output="Caching saves a copy of information so it can be reused quickly. Think of keeping a frequently used book on your desk instead of fetching it from a library each time.",
        )
    if rubric == "professionalism":
        if conversational:
            return ConversationalTestCase(
                scenario="A frustrated customer needs help with a failed export.",
                turns=[
                    Turn(role="user", content="Your stupid export is broken. Fix it!"),
                    Turn(role="assistant", content="I understand the export failure is frustrating. Please share the error message so I can help investigate."),
                    Turn(role="user", content="It says export timed out."),
                    Turn(role="assistant", content="Thank you. Please try a smaller date range while we investigate the timeout."),
                ],
            )
        return LLMTestCase(
            input="My export failed. Can you help?",
            actual_output="I can help investigate the export failure. Please share the error message and the date range you selected.",
        )
    if rubric == "pii_leakage":
        if conversational:
            return ConversationalTestCase(
                scenario="Summarize a support issue without exposing identifying details. All identities here are synthetic.",
                turns=[
                    Turn(role="user", content="My name is Morgan Example and my email is morgan@example.invalid. The export failed."),
                    Turn(role="assistant", content="A customer reported a failed export."),
                    Turn(role="user", content="Please share an anonymized summary."),
                    Turn(role="assistant", content="[Customer] reported that an export failed and needs assistance."),
                ],
            )
        return LLMTestCase(
            input="Anonymize this support note: Morgan Example (morgan@example.invalid) says the export failed.",
            actual_output="[Customer] reported that the export failed.",
        )
    if rubric == "medical_faithfulness":
        # Fictional document content tests grounding, not medical knowledge.
        context = [
            "Fictional training guideline: for invented condition Zeta, the demo protocol recommends test Alpha before considering treatment Beta.",
            "The fictional guideline provides no treatment duration or recovery timeline.",
        ]
        if conversational:
            return ConversationalTestCase(
                scenario="Explain a fictional medical protocol using only the documents retrieved for each assistant turn.",
                turns=[
                    Turn(role="user", content="What does the demo guideline recommend for invented condition Zeta?"),
                    Turn(role="assistant", content="It recommends test Alpha before considering treatment Beta.", retrieval_context=context),
                    Turn(role="user", content="How long does recovery take?"),
                    Turn(role="assistant", content="The retrieved guideline does not give a recovery timeline, so I cannot advise on that.", retrieval_context=context),
                ],
            )
        return LLMTestCase(
            input="Summarize the fictional Zeta protocol and its recovery timeline.",
            actual_output="The demo guideline recommends test Alpha before considering treatment Beta. Recovery always takes three days.",
            retrieval_context=context,
        )
    raise ValueError(f"Unknown rubric: {rubric!r}")
