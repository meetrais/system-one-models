# Gemini Decisions API Python samples

Ask typed questions about shared text or media using Gemini Decision 1. These examples call `client.decisions.create` on the Gemini Developer API (`v1beta`) and print probabilities, confidence, and token usage. The API generates no text tokens.

[Back to the repository overview](../README.md)

The implementation follows the supplied [Decisions API guide](https://aistudio.google.com/docs/decisions-api). Its SDK examples require `google-genai>=3.2.0`.

## Folder layout

```text
gemini-decisions-api/
  .env.example                    # Configuration template; copy to .env
  .gitignore                      # Keeps credentials and local environments out of Git
  requirements.txt                # Google GenAI SDK and dotenv dependencies
  decision_client.py              # Client setup, media blocks, and result display
  01_quickstart.py                # Basic yes/no check
  02_noul_product_defect.py        # Yes/no check with explicit criteria
  03_choice_support_routing.py    # Department selection
  04_score_severity.py            # Ordered severity rubric
  05_multi_question_triage.py     # Multiple questions and routing logic
  06_multimodal_check.py          # Image, audio, video, and PDF CLI
  tests/
    test_samples.py               # Offline tests
```

## Setup

Use Python 3.10 or later and a Gemini API key with access to `gemini-decision-1`. From the repository root:

### Windows PowerShell

```powershell
cd gemini-decisions-api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# Create .env only if it does not already exist:
Copy-Item .env.example .env
```

### macOS or Linux

```bash
cd gemini-decisions-api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
# Create .env only if it does not already exist:
cp .env.example .env
```

Edit `.env`, replacing the placeholder:

```dotenv
GEMINI_API_KEY=your_real_key
GEMINI_DECISIONS_MODEL=gemini-decision-1
```

Then run:

```bash
python 01_quickstart.py
```

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe` in place of `python`. All paths to `.env` files are resolved from the helper, so scripts can also run from the repository root.

## Examples

| Script | Demonstrates |
| --- | --- |
| [01_quickstart.py](./01_quickstart.py) | One `noul` question: did an item arrive damaged? |
| [02_noul_product_defect.py](./02_noul_product_defect.py) | Explicit true/false criteria distinguishing defects from preferences. |
| [03_choice_support_routing.py](./03_choice_support_routing.py) | Department selection with a catch-all option and confidence gate. |
| [04_score_severity.py](./04_score_severity.py) | Ordered rubric, expected score, most likely level, and normalized score. |
| [05_multi_question_triage.py](./05_multi_question_triage.py) | Structured order data and a customer message; independent `noul`, `choice`, and `score` questions combined in code. |
| [06_multimodal_check.py](./06_multimodal_check.py) | A configurable yes/no check on image, audio, video, or PDF input. |

Edit the message and questions in each text sample to try your own data. The triage sample prints workflow suggestions; a replacement goes to review and no external action is performed.

Run the text examples individually from this folder:

```bash
python 01_quickstart.py
python 02_noul_product_defect.py
python 03_choice_support_routing.py
python 04_score_severity.py
python 05_multi_question_triage.py
```

The quickstart prints output in this form. Values below are illustrative, not a recorded API response:

```text
input: The blue mug I ordered on Monday arrived cracked on Wednesday.

is_damaged (noul):
  P(yes): 0.990; P(no): 0.010
  confidence: 0.990
usage:
  input tokens: 100
  output tokens: 0
  total tokens: 100
    text: 100
```

## Add your own decision

Create a Python script in this folder so it can import the shared helper:

```python
from decision_client import create_client, decisions_model, print_result


def main():
    with create_client() as client:
        result = client.decisions.create(
            model=decisions_model(),
            input="Please update the delivery address for my order.",
            questions={
                "address_change": {
                    "type": "noul",
                    "instructions": "Is the customer requesting a delivery address change?",
                    "criteria": {
                        "true_description": "An explicit request to change the delivery address.",
                        "false_description": "Other requests or insufficient information.",
                    },
                },
            },
        )
    print_result(result)
    answer = result.answers["address_change"]
    workflow = "address_change_review" if answer.noul >= 0.9 else "general_review"
    print(f"suggested workflow: {workflow}")


if __name__ == "__main__":
    main()
```

For a `choice` question, use a dictionary mapping option IDs to descriptions as `criteria`. For a `score` question, use a list of level descriptions from lowest to highest. Retrieve each answer with the same key used in `questions`. Add independent questions to the same dictionary when they share input.

## Media examples

Run from this folder. Replace local filenames with your own files. Commands are single lines so they work in PowerShell and Bash.

```bash
python 06_multimodal_check.py earcup.jpg --type image --mime-type image/jpeg --resolution low --question "Does the device show physical damage? Ignore packaging."
python 06_multimodal_check.py "https://storage.googleapis.com/generativeai-downloads/data/Apollo-11_Day-01-Highlights-10s.mp3" --type audio --mime-type audio/mp3 --question "Is the speaker discussing spaceflight or a rocket launch?"
python 06_multimodal_check.py "https://storage.googleapis.com/generativeai-downloads/videos/ForBiggerBlazes.mp4" --type video --mime-type video/mp4 --resolution low --question "Does the video show fire or flames?"
python 06_multimodal_check.py invoice.pdf --type document --mime-type application/pdf --question "Does this document contain an invoice?"
```

Local files are base64 encoded; HTTPS URLs and existing Files API `file.uri` values are sent as `uri`. Supply the real MIME type; the server validates format and supported types. Inline media is limited to 100 MB per request, or 50 MB for PDFs; external URL downloads are limited to 15 MB per URL. For larger files, upload separately with the Files API and pass its URI. This CLI sends one media file per request.

Images and videos accept `low`, `medium`, or `high` resolution; `ultra_high` is image-only. Audio and PDF blocks do not accept resolution. YouTube URLs and `gs://` URIs are unsupported.

## Understanding the answers

| Type | Result | Interpretation |
| --- | --- | --- |
| `noul` | `noul`, `confidence` | `noul` is P(yes), from 0.01 to 0.99; P(no) is `1 - noul`. |
| `choice` | `choice`, `probabilities`, `confidence` | Highest-probability option and a distribution across all supplied options. |
| `score` | `score`, `probabilities`, `legend`, `confidence` | Probability-weighted average of zero-based rubric indices; can lie between levels. |

Confidence is the top outcome's probability. A confident `noul` answer can mean **no**: for `noul=0.01`, confidence is `0.99`. Use the yes probability when testing a positive condition. Thresholds in these samples are illustrative and should be tuned on labeled examples from your own traffic.

For a discrete score level, select the highest-probability entry rather than rounding the expected score. The display helper uses the returned legend and divides the expected score by the highest level index to normalize it to 0–1.

Each question sees only the shared input and its own instructions and criteria. Question keys are identifiers, so write the full question in `instructions`. Compose dependent checks in Python or make a subsequent request. JSON data must be serialized as text; adjacent text blocks need explicit separators, as in the triage sample.

Choice options are sorted alphabetically by UTF-8 bytes, with exact ties resolved to the first key. Add a described `other` option or a scope check for inputs outside your categories. Score criteria should describe distinct, linearly ordered levels.

## Configuration and failures

[decision_client.py](./decision_client.py) loads values without overwriting existing ones, in this order:

1. Process environment variables.
2. `gemini-decisions-api/.env`.
3. Repository root `.env` for missing values.

`GEMINI_API_KEY` is required. `GEMINI_DECISIONS_MODEL` defaults to `gemini-decision-1`, the model supported by the supplied guide. The client explicitly selects the Developer API rather than Vertex AI.

If `client.decisions.create` is missing, upgrade in the same Python environment: `python -m pip install --upgrade "google-genai>=3.2.0"`. API authentication, access, and HTTP errors propagate to the terminal; the examples do not replace failed requests with fabricated answers. Safety-blocked input returns HTTP 400 with an error instead of `answers`.

The guide limits requests to 1–1,000 questions, 2–255 choice options or score levels, and 262,144 context tokens. Question keys must match `[A-Za-z0-9_-]+` and contain at most 64 characters. Instructions are text-only. Context caching, Batch API, Flex/Priority inference, conversation-history blocks, thoughts, and tool-call blocks are unsupported; serialize relevant history as text.

### Troubleshooting

| Symptom | Resolution |
| --- | --- |
| `Missing GEMINI_API_KEY` | Copy `.env.example` to `.env` and replace the placeholder, or set `GEMINI_API_KEY` in the process environment. |
| Missing `google` or `dotenv` module | Activate the intended virtual environment and run `python -m pip install -r requirements.txt`. |
| SDK upgrade error mentioning `client.decisions` | Run `python -m pip install --upgrade "google-genai>=3.2.0"` using the same interpreter that runs the sample. |
| Authentication or model access error | Check the API key and its access to `gemini-decision-1`; confirm `GEMINI_DECISIONS_MODEL` has the intended value. |
| Editing `.env` has no effect | Check for an existing process environment variable, which takes precedence over `.env` values. |
| PowerShell blocks `Activate.ps1` | Use `.\.venv\Scripts\python.exe` directly for installation and execution. |
| Media CLI reports an invalid resolution | Use resolution only for images or videos; use `ultra_high` only for images. |
| Local media file cannot be found | Resolve the path from the terminal's current directory or supply an absolute path; quote paths containing spaces. |
| HTTP 400 for media | Check the actual format, MIME type, size, and URL support against the guide. |

## Offline verification

```bash
python -m unittest discover -s tests -v
```

Tests cover environment precedence, SDK compatibility errors, confidence gates (including confident negative answers), score interpretation, media block construction, and the text samples' request wiring. They do not require credentials or call the API. Live scripts require credentials, model access, and network access.

## References

- [Official documentation index](https://aistudio.google.com/llms.txt)
- [Decisions API guide](https://aistudio.google.com/docs/decisions-api)
- [Gemini Decision 1](https://aistudio.google.com/docs/models/gemini-decision-1)
- [Files API](https://aistudio.google.com/docs/files)
