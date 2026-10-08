# system-one-models
Code examples, experiments, and practical patterns for System One models like Jev.

## Code samples

- [jev-code-samples](./jev-code-samples): Python examples for calling Jev through the TypeSafe Python SDK with an API key from `.env`.
- [openai-decisions-api](./openai-decisions-api): Python examples for the OpenAI Decisions API using `predicate`, `choice`, and `score` questions.

## Jev Quick Start

Run these commands from the `jev-code-samples` folder.

### Windows PowerShell

```powershell
cd jev-code-samples
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Add your API key to `jev-code-samples/.env`, then run a sample:

```powershell
python 01_urgency_noul.py
```

### Linux or macOS

```bash
cd jev-code-samples
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Add your API key to `jev-code-samples/.env`, then run a sample:

```bash
python 01_urgency_noul.py
```

The samples expect `TYPESAFE_API_KEY` in `.env`. You can optionally set `TYPESAFE_BASE_URL=https://api.typesafe.ai` and `TYPESAFE_DEFAULT_MODEL=jev-latest`.

## OpenAI Decisions Quick Start

Run these commands from the `openai-decisions-api` folder.

### Windows PowerShell

```powershell
cd openai-decisions-api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Add your API key to `openai-decisions-api/.env`, then run a sample:

```powershell
python 01_predicate_urgency.py
```

### Linux or macOS

```bash
cd openai-decisions-api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Add your API key to `openai-decisions-api/.env`, then run a sample:

```bash
python 01_predicate_urgency.py
```

The samples expect `OPENAI_API_KEY` in `.env`. You can optionally set `OPENAI_DECISIONS_MODEL=gpt-6-luna`.
