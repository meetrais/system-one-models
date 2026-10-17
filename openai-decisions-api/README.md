# OpenAI Decisions API Python samples

Evaluate a shared message with typed questions: detect urgency, route support requests, or score severity. Each script sends one request through `client.decisions.create` and prints the results in the terminal.

[Back to the repository overview](../README.md)

## Question types

| Type | Use case | Main result |
| --- | --- | --- |
| `predicate` | Check whether a condition is true. | `probability`, from 0 to 1. |
| `choice` | Select a category, such as a support department. | `choice`, one of the supplied values. |
| `score` | Rate an input against ordered levels. | `score`, a probability-weighted average of zero-based level indices. |

Choice and score answers also include probabilities and a confidence value. See the [official Decisions guide](https://developers.openai.com/api/docs/guides/decisions) for answer semantics.

As of October 16, 2026, that guide describes Decisions as a public beta using `POST /v1/decisions`, with `gpt-6-luna` as the supported model. It requires OpenAI Python SDK 3.26.0 or later for its SDK examples.

## Setup

You need Python with `pip` and virtual environment support, network access, and an OpenAI API key with access to the Decisions API. Start at the repository root. If your terminal is already in `openai-decisions-api`, skip the `cd` command.

### Windows PowerShell

```powershell
cd openai-decisions-api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install --upgrade "openai>=3.26.0"
```

If you do not already have a `.env` file in this folder, create one:

```powershell
Copy-Item .env.example .env
```

### macOS or Linux

```bash
cd openai-decisions-api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install --upgrade "openai>=3.26.0"
```

If you do not already have a `.env` file in this folder, create one:

```bash
cp .env.example .env
```

The explicit SDK upgrade is needed because `requirements.txt` permits older versions that may not provide `client.decisions`.

### Add your API key and run

Edit `openai-decisions-api/.env` and replace the placeholder key:

```dotenv
OPENAI_API_KEY=your_real_key
OPENAI_DECISIONS_MODEL=gpt-6-luna
```

From the same folder, run:

```bash
python 01_predicate_urgency.py
```

The script prints the input message, followed by an urgency probability and a yes/no interpretation. Actual values can vary between requests.

## Samples

Run any script from this folder with `python <filename>`.

| Script | Demonstrates | Printed results |
| --- | --- | --- |
| [01_predicate_urgency.py](./01_predicate_urgency.py) | One predicate question about a support message. | Urgency probability and yes/no label. |
| [02_choice_support_routing.py](./02_choice_support_routing.py) | Route a duplicate-charge complaint to a department. | Department, confidence, and option probabilities. |
| [03_score_severity.py](./03_score_severity.py) | Score a checkout outage against three levels. | Numeric severity, nearest level label, confidence, and level probabilities. |
| [04_multi_question_triage.py](./04_multi_question_triage.py) | Ask choice, score, and predicate questions in one request. | Department, severity, and deadline pressure. |

## Configuration

| Variable | Required | Behavior |
| --- | --- | --- |
| `OPENAI_API_KEY` | Yes | API key passed to the OpenAI client. |
| `OPENAI_DECISIONS_MODEL` | No | Model sent with each request; defaults to `gpt-6-luna` in the helper. |

[decision_client.py](./decision_client.py) loads configuration in this order without overwriting existing values:

1. Environment variables already set in the process.
2. `openai-decisions-api/.env`.
3. The repository root `.env`, for values still missing.

If an edited `.env` value appears to be ignored, check whether that variable is already set in your terminal environment.

## Reading and adapting results

The helper retrieves answers by question `name`. Keep names unique within a request and update the matching `answer_by_name(...)` call if you rename a question.

Predicate output uses a threshold of `0.5`: values at or above it print as `yes`. Score output rounds the numeric result to choose a display label and clamps the index to the configured labels. With three levels, indices run from `0` to `2`; a score can fall between levels. These labels are formatting choices made by the sample helpers.

To try your own input, edit the `ticket` or `issue` string in a script. Change question instructions, choice descriptions, or ordered score levels to match your task. When changing score levels, also update the script's `SEVERITY_LEVELS` list so displayed labels stay aligned with the request.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| `Missing OPENAI_API_KEY` | Set the key in this folder's `.env`, the repository root `.env`, or the process environment. |
| `client.decisions` or `client.decisions.create` is missing | Activate the intended environment and run `python -m pip install --upgrade "openai>=3.26.0"`. |
| `ModuleNotFoundError` for `openai` or `dotenv` | Activate the environment used for setup and reinstall dependencies with `python -m pip install -r requirements.txt`. |
| Authentication or model access error | Check your key, account access, and `OPENAI_DECISIONS_MODEL` against the official guide. |
| PowerShell blocks `Activate.ps1` | Use `.\.venv\Scripts\python.exe` in place of `python` for installation and sample commands; activation is optional. |

## References

- [Official Decisions guide](https://developers.openai.com/api/docs/guides/decisions)
- [Python API reference: create a decision](https://developers.openai.com/api/reference/python/resources/decisions/methods/create)
