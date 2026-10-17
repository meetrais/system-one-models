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
