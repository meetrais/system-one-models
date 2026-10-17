# Jev System One Python samples

Use the TypeSafe Python SDK to classify messages, score support tickets and sales leads, and detect urgency. The scripts call `TypeSafeClient.system_one` with `Choice`, `Score`, and `Noul` questions and print answers in the terminal.

[Back to the repository overview](../README.md)

## Setup

You need Python with `pip` and virtual environment support, network access, and a TypeSafe API key. Start at the repository root. If your terminal is already in `jev-code-samples`, skip the `cd` command.

### Windows PowerShell

```powershell
cd jev-code-samples
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If you do not already have a `.env` file in this folder, create one:

```powershell
Copy-Item .env.example .env
```

### macOS or Linux

```bash
cd jev-code-samples
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

If you do not already have a `.env` file in this folder, create one:

```bash
cp .env.example .env
```

### Add your API key and run

Edit `jev-code-samples/.env` and replace the placeholder key:

```dotenv
TYPESAFE_API_KEY=your_real_key
TYPESAFE_BASE_URL=https://api.typesafe.ai
TYPESAFE_DEFAULT_MODEL=jev-latest
```

From the same folder, run:

```bash
python 01_urgency_noul.py
```

The script prints `is_urgent` with a numeric value and a yes/no interpretation. Actual values can vary between requests.

## Samples

Run any script from this folder with `python <filename>`.

| Script | Demonstrates | Printed results |
| --- | --- | --- |
| [01_urgency_noul.py](./01_urgency_noul.py) | A single `Noul` question about urgency. | Urgency value and yes/no label. |
| [02_support_triage.py](./02_support_triage.py) | `Choice`, `Score`, and `Noul` questions about one ticket. | Department, frustration, and urgency. |
| [03_lead_qualification.py](./03_lead_qualification.py) | Evaluate a sales lead with multiple questions. | Segment, fit score, budget availability, and buying timeline. |
| [04_interactive_classifier.py](./04_interactive_classifier.py) | Classify messages entered in the terminal. | Department, frustration, and urgency for each message. |

The first three scripts use input defined in their source files. For interactive input, run:

```bash
python 04_interactive_classifier.py
```

Enter a message at the `Message:` prompt. Type `exit` or `quit` to end the session. Each submitted message makes a separate API request.

## Configuration

| Variable | Required | Purpose |
| --- | --- | --- |
| `TYPESAFE_API_KEY` | Yes | API key passed to `TypeSafeClient`. |
| `TYPESAFE_BASE_URL` | No | SDK endpoint setting; the example template uses `https://api.typesafe.ai`. |
| `TYPESAFE_DEFAULT_MODEL` | No | SDK model setting; the example template uses `jev-latest`. |

[jev_client.py](./jev_client.py) loads configuration in this order without overwriting existing values:

1. Environment variables already set in the process.
2. `jev-code-samples/.env`.
3. The repository root `.env`, for values still missing.

The helper passes the API key explicitly; endpoint and model configuration are left to the SDK. If an edited `.env` value appears to be ignored, check whether that variable is already set in your terminal environment.

## Reading and adapting results

`Choice` questions define named categories in a `criteria` dictionary. The scripts read the selected category from `.choice`. `Score` questions define an ordered list of criteria and read the numeric result from `.score`. `Noul` questions evaluate a condition and return a numeric value through `.noul`.

For display, the samples interpret a `Noul` value at or above `0.5` as `yes`. They round a score to select a label from the corresponding criteria list and clamp the index to that list's bounds. These interpretations are defined in each script's `describe_noul` and `describe_score` helpers.

To try your own task, edit the input string and question instructions in a script. Adjust the `Choice` criteria or ordered `Score` criteria as needed. The score criteria lists also supply the labels printed by the examples, so keep their order meaningful.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| `Missing API key. Set TYPESAFE_API_KEY in .env.` | Set the key in this folder's `.env`, the repository root `.env`, or the process environment. |
| `ModuleNotFoundError` for `typesafe_sdk` or `dotenv` | Activate the environment used for setup and run `python -m pip install -r requirements.txt`. |
| `Unknown model: jev` | Set `TYPESAFE_DEFAULT_MODEL=jev-latest`, matching the example template, or use the model identifier provided for your account. Check for an older process environment value as well. |
| Authentication or connection error | Check your key and endpoint configuration. |
| PowerShell blocks `Activate.ps1` | Use `.\.venv\Scripts\python.exe` in place of `python` for installation and sample commands; activation is optional. |
