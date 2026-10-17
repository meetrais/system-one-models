# JevEval: Jev as a judge

Custom single-turn, multi-turn, and trajectory evaluation using DeepEval's `JevEval` and `ConversationalJevEval`. You write bounded questions; Jev returns probabilities; DeepEval maps the answers to values in `[0, 1]` and combines applicable values with a weighted mean.

These examples evaluate fixed interactions without generating a new response. The judge uses Jev through TypeSafe, so no OpenAI API key or generative evaluation model is required. Reasons are formatted in code from the answers, without an additional model call. Identical answers produce identical reasons; that does not guarantee unchanged answers across model versions or API runs.

[Repository overview](../README.md) · [Official JevEval guide](https://deepeval.com/docs/metrics-jev-eval)

## Setup

Use Python 3.10 or later. The dependencies pin DeepEval 4.3.1 and TypeSafe SDK 0.7.5, which provide the interfaces used here. Start at the repository root; skip `cd JevEval` if already in this folder.

### Windows PowerShell

```powershell
cd JevEval
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If this folder does not already contain `.env`, create it:

```powershell
Copy-Item .env.example .env
```

If PowerShell blocks activation, substitute `.\.venv\Scripts\python.exe` for `python` in installation and run commands.

### macOS or Linux

```bash
cd JevEval
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

If this folder does not already contain `.env`, create it:

```bash
cp .env.example .env
```

### Configure and run

Replace the placeholder in `JevEval/.env`:

```dotenv
TYPESAFE_API_KEY=your_real_key
TYPESAFE_DEFAULT_MODEL=jev-latest
DEEPEVAL_TELEMETRY_OPT_OUT=YES
```

Configuration priority is existing process variables, then `JevEval/.env`, then the repository root `.env`. The helper resolves these paths relative to its file and loads configuration before importing DeepEval. It defaults telemetry opt-out to `YES` if unset. Jev evaluation still sends the selected interaction data to TypeSafe over the network.

Run from this folder:

```bash
python 01_single_turn.py
python 02_multi_turn.py
python 03_trajectory.py
python 04_answer_correctness.py
python 05_coherence.py
python 06_tonality.py
python 07_safety_pii.py
python 08_custom_rag.py
```

## Examples

| Script | Metric | What it evaluates |
| --- | --- | --- |
| [01_single_turn.py](./01_single_turn.py) | Tool Faithfulness | A weather response adds wind and humidity absent from the tool output. |
| [02_multi_turn.py](./02_multi_turn.py) | Refund Handling | A conversation ends with a refund timeline but never confirms the requested amount. |
| [03_trajectory.py](./03_trajectory.py) | Tool Use | An observed agent calls `order_lookup` and reports its result. The agent and tool are fixed Python functions. |
| [04_answer_correctness.py](./04_answer_correctness.py) | Correctness | Compare dispatch and tracking claims with a reference answer or expected conversation outcome. |
| [05_coherence.py](./05_coherence.py) | Clarity | Beginner-friendly explanations, explained jargon, and coherence across turns. |
| [06_tonality.py](./06_tonality.py) | Professionalism | Professional wording and respectful handling of a rude user in the conversation version. |
| [07_safety_pii.py](./07_safety_pii.py) | PII Leakage | Anonymization of synthetic support data; conversations distinguish volunteered information from assistant-introduced details. |
| [08_custom_rag.py](./08_custom_rag.py) | Medical Faithfulness | Grounding in fictional documents, including per-assistant-turn retrieval context for conversations. |

All examples except the trajectory script use standalone `measure()` by default and print the metric score, threshold, success, reason, and `score_breakdown`. They can also run through DeepEval's evaluation runner:

```bash
python 01_single_turn.py --evaluate
python 02_multi_turn.py --evaluate
python 04_answer_correctness.py --multi-turn --evaluate
```

The trajectory example uses `EvaluationDataset.evals_iterator` and DeepEval's result reporting. It intentionally omits `evaluation_params`. Calling a trajectory metric with an ordinary, untraced `LLMTestCase` raises `MissingTestCaseParamsError`. `ConversationalJevEval` has no trajectory mode.

Scripts 04 through 08 each support both single-turn (default) and conversation evaluation. Add `--multi-turn` to select the conversation fixture and rubric. These commands work in PowerShell and Linux/macOS shells after environment activation:

```bash
python 04_answer_correctness.py --multi-turn
python 05_coherence.py --multi-turn
python 06_tonality.py --multi-turn
python 07_safety_pii.py --multi-turn
python 08_custom_rag.py --multi-turn
```

The five single-turn rubrics follow your supplied JevEval Examples. Their conversation versions adapt the checks to the full turns list and selected conversation fields. Weights and questions are examples to tune for your own requirements. A higher PII Leakage score means better privacy behavior. Medical Faithfulness measures support in the supplied documents; it does not establish medical correctness. The medical documents describe an invented condition and protocol solely to demonstrate grounding.

All scripts accept:

| Flag | Behavior |
| --- | --- |
| `--strict` | Binary score; every applicable question must pass. Threshold becomes `1`. |
| `--score-only` | Set threshold to `None`; report a score without a passing threshold. |
| `--verbose` | Print DeepEval's detailed question logs. |
| `--help` | Show usage without loading credentials or calling Jev. |

`--strict` and `--score-only` are mutually exclusive. Example:

```bash
python 01_single_turn.py --strict --verbose
```

## Write your own metric

Edit the rubric factories in [metrics.py](./metrics.py) and interactions in [sample_cases.py](./sample_cases.py). Import question types from `deepeval.metrics.jev_eval`; these are DeepEval wrappers with weights and credit mappings, rather than the raw TypeSafe SDK question classes.

- `Noul`: a proposition whose value is `P(true)`. Use independent checks, with larger weights for more important requirements.
- `Score`: ordered levels from worst to best. Value is the expected zero-based level index divided by `number_of_levels - 1`. Supply between 2 and 10 levels.
- `Choice`: unordered option names mapped to credit in `[0, 1]`, or `None` for not applicable. Value is expected credit, renormalized over applicable options.

Each question defaults to weight `1.0`. Normal scoring is:

```text
score = sum(weight * value for applicable questions) / sum(applicable weights)
```

A Choice question is skipped if its `None` options have combined probability at least `0.5`. If all questions are skipped, DeepEval returns `1`. Otherwise skipped questions contribute neither value nor weight.

In strict mode, Noul passes at `P(true) >= 0.5`; Score passes when the most probable level is the highest; Choice passes when the most probable applicable option has full credit. Strict mode uses these checks instead of the weighted mean.

For single turns, include every field your question mentions in `evaluation_params`, using `SingleTurnParams`. The weather example includes `INPUT`, `ACTUAL_OUTPUT`, and `TOOLS_CALLED`. Unlisted fields are invisible to the judge. Conversations include `turns` automatically; use `MultiTurnParams` to select additional conversation fields such as `SCENARIO` and `EXPECTED_OUTCOME`.

For trajectory questions, refer to tool or agent spans by name. The compact trace includes inputs, outputs, tool calls, and children, but omits prompts, token counts, and costs.

Metric settings include `system_one_model` (default `jev-latest`), `threshold` (default `0.5`), `strict_mode`, `async_mode` (default `True`), `verbose_mode`, `flaky`, and `include_reason` (default `True`). There is no generative `model` argument. Use `system_one_model` to select Jev or inject a `DeepEvalBaseSystemOneModel` implementation.

## Offline verification

```bash
python -m unittest discover -s tests -v
```

The tests use fixed System One answers with the real DeepEval metrics. They require installed dependencies, but no API key or live judge. They verify weighted scoring, applicability, strict mode, field visibility, and trace requirements, plus all five new rubrics in both modes and the conversation CLI path. Live API results are not asserted as exact scores.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Missing TypeSafe key | Replace the placeholder in `.env` or set `TYPESAFE_API_KEY` in the process environment. |
| Missing `JevEval`, `SingleTurnParams`, or SDK imports | Activate this folder's environment and reinstall `requirements.txt`. |
| Changed `.env` seems ignored | Check for an existing process variable, which takes precedence. |
| `MissingTestCaseParamsError` | Include the fields named in your rubric, or supply an observed trace for trajectory mode. |
| Unexpected score | Inspect applicability and probabilities in `score_breakdown`; check level order and weights. |

Reference: [DeepEval JevEval documentation](https://deepeval.com/docs/metrics-jev-eval).
