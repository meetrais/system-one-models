"""Custom rubrics using DeepEval's Jev-backed question types."""

from deepeval.metrics import ConversationalJevEval, JevEval
from deepeval.metrics.jev_eval import Choice, Noul, Score
from deepeval.test_case import MultiTurnParams, SingleTurnParams


def tool_faithfulness(**options) -> JevEval:
    return JevEval(
        name="Tool Faithfulness",
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.TOOLS_CALLED,
        ],
        questions=[
            Noul("Every fact and figure in actual_output appears in the output of a tool in tools_called.", weight=2),
            Noul("actual_output reports every value returned in tools_called accurately."),
            Score(
                "How much of actual_output is grounded in the outputs in tools_called?",
                levels=["Fabricated", "Mostly fabricated", "Mostly grounded", "Fully grounded"],
            ),
            Choice(
                "What did actual_output do with information the tools did not return?",
                options={
                    "left_it_out": 1.0,
                    "flagged_it_as_unknown": 1.0,
                    "hedged_it": 0.5,
                    "stated_it_as_fact": 0.0,
                    "nothing_missing": None,
                },
            ),
        ],
        **options,
    )


def refund_handling(**options) -> ConversationalJevEval:
    return ConversationalJevEval(
        name="Refund Handling",
        evaluation_params=[MultiTurnParams.SCENARIO, MultiTurnParams.EXPECTED_OUTCOME],
        questions=[
            Noul("The assistant verifies the order before acting on the refund."),
            Score(
                "How fully is the user's request settled by the end of turns?",
                levels=["Not addressed", "Partly settled", "Fully resolved"],
            ),
            Choice(
                "What did the assistant do about the amount the user asked for?",
                options={"stated_it": 1.0, "deferred_it": 0.5, "ignored_it": 0.0, "never_asked": None},
            ),
        ],
        **options,
    )


def tool_use(**options) -> JevEval:
    # Omitting evaluation_params selects trace mode, not an empty field list.
    return JevEval(
        name="Tool Use",
        questions=[
            Noul("The agent called the order_lookup tool before answering.", weight=2),
            Noul("The order_id passed to order_lookup matches the order the user asked about."),
            Choice(
                "How does the agent's final output relate to what order_lookup returned?",
                options={"consistent": 1.0, "partly_consistent": 0.5, "contradicts_it": 0.0, "no_tool_called": None},
            ),
        ],
        **options,
    )
