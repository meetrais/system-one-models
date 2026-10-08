# OpenAI Decisions API Python Samples

Python examples for the OpenAI Decisions API.

The Decisions API evaluates shared input against typed questions. It can return:

- `predicate`: a probability from 0 to 1 that a condition is true.
- `choice`: one value from a fixed set of choices.
- `score`: a probability-weighted score across ordered levels.

The official OpenAI documentation currently describes Decisions as a public beta using the dedicated `POST /v1/decisions` endpoint with `gpt-6-luna` as the supported model.

## Setup

Run these commands from the `openai-decisions-api` folder.

### Windows PowerShell

1. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Create your local environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

4. Add your API key to `.env`:

   ```dotenv
   OPENAI_API_KEY=your_real_key
   OPENAI_DECISIONS_MODEL=gpt-6-luna
   ```

### Linux or macOS

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Create your local environment file:

   ```bash
   cp .env.example .env
   ```

4. Add your API key to `.env`:

   ```dotenv
   OPENAI_API_KEY=your_real_key
   OPENAI_DECISIONS_MODEL=gpt-6-luna
   ```

The helper loads `.env` from either `openai-decisions-api/.env` or the repo root `.env`.

## Samples

After setup, run any sample from the `openai-decisions-api` folder.

```bash
python 01_predicate_urgency.py
python 02_choice_support_routing.py
python 03_score_severity.py
python 04_multi_question_triage.py
```

## Environment Variables

| Name | Required | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | Yes | Your OpenAI API key. |
| `OPENAI_DECISIONS_MODEL` | No | Decisions model name. Defaults to `gpt-6-luna`. |

## Troubleshooting

If `client.decisions.create` is missing, upgrade the OpenAI Python SDK:

```bash
pip install --upgrade openai
```

