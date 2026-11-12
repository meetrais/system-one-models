"""Offline checks: configuration, routing gates, media, and SDK request wiring."""

import base64
import importlib.util
import io
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace as Answer
import unittest
from unittest.mock import MagicMock, patch


SAMPLE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SAMPLE_DIR))
import decision_client  # noqa: E402
from google.genai.decisions import CreateDecisionRequest, CreateDecisionResponse  # noqa: E402


def load_sample(filename):
    spec = importlib.util.spec_from_file_location(filename.removesuffix(".py"), SAMPLE_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ConfigurationTests(unittest.TestCase):
    def test_configuration_precedence_and_developer_api(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            local = root / "samples"
            local.mkdir()
            (root / ".env").write_text("GEMINI_API_KEY=root-key\nGEMINI_DECISIONS_MODEL=root-model\n")
            (local / ".env").write_text("GEMINI_API_KEY=local-key\n")
            with patch.object(decision_client, "SAMPLE_DIR", local), patch.dict(os.environ, {}, clear=True):
                with patch.object(decision_client.genai, "Client") as factory:
                    decision_client.create_client()
                    factory.assert_called_once_with(
                        api_key="local-key", vertexai=False, http_options={"api_version": "v1beta"}
                    )
                    self.assertEqual(decision_client.decisions_model(), "root-model")
                    os.environ["GEMINI_API_KEY"] = "process-key"
                    decision_client.create_client()
                    self.assertEqual(factory.call_args.kwargs["api_key"], "process-key")

    def test_missing_key_fails_before_client_creation(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(decision_client, "load_dotenv"):
            with patch.object(decision_client.genai, "Client") as factory:
                with self.assertRaisesRegex(RuntimeError, "Missing GEMINI_API_KEY"):
                    decision_client.create_client()
                factory.assert_not_called()

    def test_old_sdk_gives_upgrade_instructions_and_closes_client(self):
        client = Answer(close=MagicMock())
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True):
            with patch.object(decision_client, "load_dotenv"), patch.object(
                decision_client.genai, "Client", return_value=client
            ):
                with self.assertRaisesRegex(RuntimeError, "google-genai>=3.2.0"):
                    decision_client.create_client()
        client.close.assert_called_once()


class RoutingTests(unittest.TestCase):
    def test_routing_gates(self):
        sample = load_sample("05_multi_question_triage.py")
        for probability, confidence, choice, expected in [
            (0.95, 0.8, "replacement_review", "replacement_review"),
            (0.9, 0.7, "troubleshooting_flow", "troubleshooting_flow"),
            (0.01, 0.99, "replacement_review", "human_escalation"),
            (0.95, 0.69, "replacement_review", "human_escalation"),
            (0.89, 0.9, "replacement_review", "human_escalation"),
            (0.99, 0.99, "human_escalation", "human_escalation"),
            (0.99, 0.99, "unexpected", "human_escalation"),
            (float("nan"), 0.99, "replacement_review", "human_escalation"),
        ]:
            with self.subTest(probability=probability, confidence=confidence, choice=choice):
                answers = {
                    "is_defect": Answer(noul=probability),
                    "next_action": Answer(confidence=confidence, choice=choice),
                }
                self.assertEqual(sample.suggested_workflow(answers), expected)


class MediaTests(unittest.TestCase):
    def test_local_bytes_are_base64_encoded(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "photo.png"
            path.write_bytes(b"test image bytes")
            block = decision_client.media_block(str(path), "image", "image/png", "low")
        self.assertEqual(base64.b64decode(block["data"]), b"test image bytes")
        self.assertNotIn("uri", block)
        self.assertEqual(block["resolution"], "low")

    def test_files_api_uri_is_preserved(self):
        uri = "https://generativelanguage.googleapis.com/v1beta/files/example"
        self.assertEqual(decision_client.media_block(uri, "document", "application/pdf")["uri"], uri)

    def test_unsupported_sources_and_media_options_fail_locally(self):
        for args in [
            ("gs://bucket/clip.mp4", "video", "video/mp4", None),
            ("https://www.youtube.com/watch?v=123", "video", "video/mp4", None),
            ("https://youtu.be/123", "video", "video/mp4", None),
            ("https://example.com/clip.mp4", "video", "video/mp4", "ultra_high"),
            ("https://example.com/clip.mp3", "audio", "audio/mp3", "low"),
            ("https://example.com/file.pdf", "document", "application/octet-stream", None),
        ]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                decision_client.media_block(*args)


class SampleTests(unittest.TestCase):
    def test_all_text_samples_send_one_typed_request(self):
        # Fake only the transport: exercise each complete main() without API calls.
        for filename in sorted(SAMPLE_DIR.glob("0[1-5]_*.py")):
            with self.subTest(filename=filename.name):
                sample = load_sample(filename.name)
                result = Answer(answers={
                    "is_defect": Answer(noul=0.97),
                    "department": Answer(choice="billing", confidence=0.95),
                    "next_action": Answer(choice="replacement_review", confidence=0.95),
                })
                with patch.object(sample, "create_client") as factory, patch.object(
                    sample, "print_result"
                ), patch("sys.stdout", new_callable=io.StringIO):
                    client = factory.return_value.__enter__.return_value
                    client.decisions.create.return_value = result
                    sample.main()
                    client.decisions.create.assert_called_once()
                    request = client.decisions.create.call_args.kwargs
                    self.assertEqual(request["model"], decision_client.decisions_model())
                    self.assertTrue(request["input"])
                    self.assertIsInstance(request["questions"], dict)
                    # Verify the installed SDK accepts each example's actual payload.
                    CreateDecisionRequest.model_validate(request)
                    for question in request["questions"].values():
                        self.assertIn(question["type"], {"noul", "choice", "score"})
                        self.assertTrue(question["instructions"])

    def test_score_display_uses_distribution_instead_of_rounding(self):
        # Expected score rounds to 1, but level 0 is the most likely outcome.
        result = Answer(answers={"severity": Answer(
            type="score", score=0.8, confidence=0.6,
            probabilities={"0": 0.6, "1": 0.0, "2": 0.4},
            legend={"0": "Low", "1": "Medium", "2": "High"},
        )}, usage=None)
        with patch("sys.stdout", new_callable=io.StringIO) as output:
            decision_client.print_result(result)
        self.assertIn("most likely level: 0 - Low", output.getvalue())
        self.assertIn("normalized score: 0.400", output.getvalue())

    def test_actual_sdk_response_types_and_usage_can_be_displayed(self):
        result = CreateDecisionResponse.model_validate({
            "answers": {
                "damage": {"type": "noul", "noul": 0.99, "confidence": 0.99},
                "queue": {
                    "type": "choice", "choice": "billing", "confidence": 0.9,
                    "probabilities": {"billing": 0.9, "other": 0.1},
                },
                "severity": {
                    "type": "score", "score": 0.8, "confidence": 0.6,
                    "probabilities": {"0": 0.6, "1": 0.0, "2": 0.4},
                    "legend": {"0": "Low", "1": "Medium", "2": "High"},
                },
            },
            "usage": {
                "total_input_tokens": 100, "total_output_tokens": 0, "total_tokens": 100,
                "input_tokens_by_modality": [{"modality": "text", "tokens": 100}],
            },
        })
        with patch("sys.stdout", new_callable=io.StringIO) as output:
            decision_client.print_result(result)
        for expected in ["P(yes): 0.990", "choice: billing", "most likely level: 0 - Low",
                         "output tokens: 0", "text: 100"]:
            self.assertIn(expected, output.getvalue())


if __name__ == "__main__":
    unittest.main()
