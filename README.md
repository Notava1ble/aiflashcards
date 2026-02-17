# AI Flashcards

AI Flashcards is a Python CLI tool that converts study notes into Anki-compatible flashcards using Google's Gemini models.

## Features

- Generates structured question/answer flashcards from local note files.
- Uses Gemini 3 Flash Preview by default (`gemini-3-flash-preview`).
- Outputs Anki-ready tab-separated text and keeps raw model CSV for traceability.
- Supports configurable model and runtime settings via environment variables and CLI flags.

## Requirements

- Python 3.10+
- A Google Gemini API key

Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

1. Export your API key:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

2. Add one or more note files to `./notes/`.

3. Run the generator:

```bash
python src/main.py
```

## Runtime Configuration

You can pass configuration at runtime (recommended for CI/CD and one-off runs):

```bash
python src/main.py \
  --model gemini-3-flash-preview \
  --temperature 0.2 \
  --max-output-tokens 8192 \
  --notes-dir ./notes \
  --instructions-path ./src/instructions.txt \
  --output-dir ./output \
  --logs-dir ./logs \
  --log-level INFO
```

### CLI Options

- `--model` (default from `GEMINI_MODEL` or `gemini-3-flash-preview`)
- `--temperature` (default from `GEMINI_TEMPERATURE` or `0.2`)
- `--max-output-tokens` (default from `GEMINI_MAX_OUTPUT_TOKENS` or `8192`)
- `--notes-dir` (default from `NOTES_DIR` or `./notes/`)
- `--instructions-path` (default from `INSTRUCTIONS_PATH` or `./src/instructions.txt`)
- `--output-dir` (default from `OUTPUT_DIR` or `./output/`)
- `--logs-dir` (default from `LOGS_DIR` or `./logs`)
- `--log-file` (default from `APP_LOG_FILE` or `aiflashcard.log`)
- `--log-level` (default from `APP_LOG_LEVEL` or `INFO`)

## Output Files

- `output/flashcards.txt` — Anki import file (tab-separated).
- `logs/response.csv` — Raw model output before formatting.
- `aiflashcard.log` — Detailed application logs.
