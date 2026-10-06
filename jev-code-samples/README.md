# Jev System One Python Code Samples

Python examples for calling System One models such as Jev through the official TypeSafe Python SDK.

## Setup

Run these commands from the `jev-code-samples` folder.

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
   TYPESAFE_API_KEY=your_real_key
   TYPESAFE_BASE_URL=https://api.typesafe.ai
   TYPESAFE_DEFAULT_MODEL=jev-latest
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
   TYPESAFE_API_KEY=your_real_key
   TYPESAFE_BASE_URL=https://api.typesafe.ai
   TYPESAFE_DEFAULT_MODEL=jev-latest
   ```

If your endpoint or model identifier is different, update `TYPESAFE_BASE_URL` or `TYPESAFE_DEFAULT_MODEL`.

The helper loads `.env` from either `jev-code-samples/.env` or the repo root `.env`.

## Samples

After setup, run any sample from the `jev-code-samples` folder.

```bash
python 01_urgency_noul.py
python 02_support_triage.py
python 03_lead_qualification.py
python 04_interactive_classifier.py
```

## Environment Variables

| Name | Required | Description |
| --- | --- | --- |
| `TYPESAFE_API_KEY` | Yes | Your TypeSafe AI API key. |
| `TYPESAFE_BASE_URL` | No | TypeSafe API base URL. The SDK defaults to `https://api.typesafe.ai`. |
| `TYPESAFE_DEFAULT_MODEL` | No | Default model name. The SDK defaults to `jev-latest`. |

These samples use `TypeSafeClient.system_one` with `Choice`, `Score`, and `Noul` questions, matching the official Python SDK sample shape.

## Troubleshooting

If you see `Unknown model: jev`, update your `.env` file to use:

```dotenv
TYPESAFE_DEFAULT_MODEL=jev-latest
```
