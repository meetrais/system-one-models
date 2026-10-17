"""Offline integration checks against DeepEval, using fixed judge answers."""

import asyncio
import os
from pathlib import Path
import sys
import unittest

os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"
os.environ["DEEPEVAL_NO_INSPECT_PROMPT"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from deepeval.errors import MissingTestCaseParamsError
from deepeval.metrics import JevEval
from deepeval.metrics.jev_eval import Choice, Noul
from deepeval.models import DeepEvalBaseSystemOneModel
from deepeval.models.system_one.schema import (
    ChoiceAnswer,
    NoulAnswer,
    ScoreAnswer,
    SystemOneAnswers,
)
from deepeval.test_case import SingleTurnParams

from metrics import refund_handling, tool_faithfulness, tool_use
from sample_cases import refund_case, weather_case


class FixedJudge(DeepEvalBaseSystemOneModel):
    """Return fixture answers and record state; never instantiate an API client."""

    def __init__(self, answers):
        self.answers = answers
        self.calls = []
        super().__init__(model="fixed-offline-judge")

    def load_model(self):
        return None

    def get_model_name(self):
        return "fixed-offline-judge"

    def decide(self, state, questions):
        self.calls.append((state, questions))
        return self.answers, 0.0

    async def a_decide(self, state, questions):
        return self.decide(state, questions)


def weather_answers():
    return SystemOneAnswers(
        nouls={"q_0": NoulAnswer(probability=0.3), "q_1": NoulAnswer(probability=0.9)},
        scores={
            "q_2": ScoreAnswer(
                score=1.7,
                probabilities={0: 0.05, 1: 0.3, 2: 0.55, 3: 0.1},
                confidence=0.4,
            )
        },
        choices={
            "q_3": ChoiceAnswer(
                choice="stated_it_as_fact",
                probabilities={
                    "left_it_out": 0.05, "flagged_it_as_unknown": 0.05,
                    "hedged_it": 0.25, "stated_it_as_fact": 0.6, "nothing_missing": 0.05,
                },
                confidence=0.5,
            )
        },
    )


class JevEvalIntegrationTests(unittest.TestCase):
    def test_weighted_mean_and_visible_fields(self):
        judge = FixedJudge(weather_answers())
        metric = tool_faithfulness(system_one_model=judge, async_mode=False)
        metric.measure(weather_case(), _show_indicator=False)
        expected = (2 * 0.3 + 0.9 + 1.7 / 3 + 0.225 / 0.95) / 5
        self.assertAlmostEqual(metric.score, expected)
        self.assertFalse(metric.is_successful())
        self.assertEqual(len(judge.calls), 1)
        state, questions = judge.calls[0]
        self.assertEqual(set(state["test_case"]), {"input", "actual_output", "tools_called"})
        self.assertEqual(len(questions), 4)
        self.assertEqual(len(metric.score_breakdown), 4)

    def test_identical_answers_produce_identical_async_reason(self):
        sync_metric = tool_faithfulness(system_one_model=FixedJudge(weather_answers()), async_mode=False)
        async_metric = tool_faithfulness(system_one_model=FixedJudge(weather_answers()))
        sync_metric.measure(weather_case(), _show_indicator=False)
        asyncio.run(async_metric.a_measure(weather_case(), _show_indicator=False))
        self.assertEqual(sync_metric.score, async_metric.score)
        self.assertEqual(sync_metric.reason, async_metric.reason)

    def test_choice_is_skipped_at_half_not_applicable_probability(self):
        judge = FixedJudge(SystemOneAnswers(
            nouls={"q_0": NoulAnswer(probability=0.2)},
            choices={"q_1": ChoiceAnswer(
                choice="unused", probabilities={"good": 0.5, "unused": 0.5}, confidence=0.0,
            )},
        ))
        metric = JevEval(
            name="Applicability", evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT],
            questions=[Noul("actual_output is correct."), Choice(
                "Does this apply?", options={"good": 1.0, "unused": None}, weight=10,
            )], system_one_model=judge, async_mode=False,
        )
        metric.measure(weather_case(), _show_indicator=False)
        self.assertAlmostEqual(metric.score, 0.2)
        self.assertFalse(metric.score_breakdown[1]["applicable"])

    def test_all_questions_skipped_scores_one(self):
        judge = FixedJudge(SystemOneAnswers(choices={"q_0": ChoiceAnswer(
            choice="unused", probabilities={"good": 0.1, "unused": 0.9}, confidence=0.8,
        )}))
        metric = JevEval(
            name="Not applicable", evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT],
            questions=[Choice("Does this apply?", options={"good": 1.0, "unused": None})],
            system_one_model=judge, async_mode=False,
        )
        metric.measure(weather_case(), _show_indicator=False)
        self.assertEqual(metric.score, 1.0)

    def test_strict_failure_and_pass_use_best_answers(self):
        answers = weather_answers()
        failing = tool_faithfulness(system_one_model=FixedJudge(answers), strict_mode=True, async_mode=False)
        failing.measure(weather_case(), _show_indicator=False)
        self.assertEqual(failing.threshold, 1)
        self.assertEqual(failing.score, 0)
        self.assertFalse(failing.score_breakdown[0]["passed"])
        answers.nouls["q_0"] = NoulAnswer(probability=0.6)
        answers.scores["q_2"] = ScoreAnswer(
            score=2.6, probabilities={0: 0.0, 1: 0.0, 2: 0.4, 3: 0.6}, confidence=0.46,
        )
        answers.choices["q_3"] = ChoiceAnswer(
            choice="left_it_out", probabilities={
                "left_it_out": 0.6, "flagged_it_as_unknown": 0.1, "hedged_it": 0.1,
                "stated_it_as_fact": 0.1, "nothing_missing": 0.1,
            }, confidence=0.5,
        )
        passing = tool_faithfulness(system_one_model=FixedJudge(answers), strict_mode=True, async_mode=False)
        passing.measure(weather_case(), _show_indicator=False)
        self.assertEqual(passing.score, 1)
        self.assertTrue(all(item["passed"] for item in passing.score_breakdown))

    def test_multi_turn_state_and_normalized_score(self):
        judge = FixedJudge(SystemOneAnswers(
            nouls={"q_0": NoulAnswer(probability=0.8)},
            scores={"q_1": ScoreAnswer(
                score=1.0, probabilities={0: 0.2, 1: 0.6, 2: 0.2}, confidence=0.4,
            )},
            choices={"q_2": ChoiceAnswer(
                choice="deferred_it", probabilities={
                    "stated_it": 0.1, "deferred_it": 0.6, "ignored_it": 0.2, "never_asked": 0.1,
                }, confidence=0.46,
            )},
        ))
        metric = refund_handling(system_one_model=judge, async_mode=False, threshold=None)
        metric.measure(refund_case(), _show_indicator=False)
        self.assertAlmostEqual(metric.score, (0.8 + 0.5 + 0.4 / 0.9) / 3)
        self.assertIsNone(metric.threshold)
        state, _ = judge.calls[0]
        self.assertIn("turns", state)
        self.assertIn("scenario", state["test_case"])
        self.assertIn("expected_outcome", state["test_case"])
        self.assertEqual(len(state["turns"]), 5)

    def test_trajectory_rejects_untraced_test_case_before_calling_judge(self):
        judge = FixedJudge(SystemOneAnswers())
        metric = tool_use(system_one_model=judge, async_mode=False)
        with self.assertRaises(MissingTestCaseParamsError):
            metric.measure(weather_case(), _show_indicator=False)
        self.assertEqual(judge.calls, [])


if __name__ == "__main__":
    unittest.main()
