# System One model samples

Python examples for turning messages into typed decisions: classify a request, score an issue, or estimate whether a condition is true.

## Choose a collection

| Collection | Examples | Setup guide |
| --- | --- | --- |
| Jev / TypeSafe | Urgency detection, support triage, lead qualification, and an interactive classifier using `Noul`, `Choice`, and `Score`. | [Jev README](./jev-code-samples/README.md) |
| JevEval / DeepEval | Custom single-turn, conversation, and trajectory evaluation with weighted Jev questions. | [JevEval README](./JevEval/README.md) |
| OpenAI Decisions API | Urgency detection, department routing, severity scoring, and multiple questions in one request using `predicate`, `choice`, and `score`. | [OpenAI Decisions README](./openai-decisions-api/README.md) |

Each collection has its own dependencies, environment template, and client helper. The collections can be run independently.

## Getting started

1. Install Python with `pip` and virtual environment support.
2. Open a terminal at the repository root and choose a collection above.
3. Follow its Windows PowerShell or macOS/Linux setup instructions.
4. Add the relevant provider's API key to the collection's `.env` file.
5. Run the first sample, then explore the other scripts.

The scripts require network access and credentials for the chosen provider. The first three Jev samples and all OpenAI samples use messages defined in the source code. The interactive Jev sample accepts messages in the terminal.

## Repository layout

- [jev-code-samples/](./jev-code-samples/): four scripts, `jev_client.py`, `requirements.txt`, and `.env.example`.
- [JevEval/](./JevEval/): three evaluation examples, custom rubrics, offline tests, and setup instructions.
- [openai-decisions-api/](./openai-decisions-api/): four scripts, `decision_client.py`, `requirements.txt`, and `.env.example`.
- [LICENSE](./LICENSE): Apache License 2.0.

## Configuration

Jev requires `TYPESAFE_API_KEY`; the OpenAI samples require `OPENAI_API_KEY`. Copy the appropriate `.env.example` only if you do not already have a `.env` file in that folder, then replace the placeholder key.

The client and JevEval helpers load configuration in this order, preserving values already set:

1. Environment variables in the current process.
2. The sample collection's `.env` file.
3. The repository root `.env` file, which fills in missing values.

Environment file paths are resolved relative to the helper file. Each collection's README lists optional settings and troubleshooting steps.
