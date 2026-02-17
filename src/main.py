import argparse
import logging
import time

from ai import generate
from config import (
    INSTRUCTIONS_PATH,
    LOG_FILE,
    LOG_LEVEL,
    LOGS_DIR,
    MAX_OUTPUT_TOKENS,
    MODEL_NAME,
    NOTES_DIR,
    OUTPUT_DIR,
    TEMPERATURE,
)
from logging_config import configure_logger
from utils import (
    clean_previous_output,
    format_csv_to_text,
    load_instructions,
    load_notes,
    log_response_as_csv,
    remove_csv_fencing,
    write_flashcards_to_file,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the flashcard generator.

    Returns:
        argparse.Namespace: Parsed arguments including `model`, `temperature`, `max_output_tokens`,
            `notes_dir`, `instructions_path`, `output_dir`, `logs_dir`, `log_file`, and `log_level`.
    """
    parser = argparse.ArgumentParser(description="Generate Anki flashcards from notes using Gemini.")
    parser.add_argument("--model", default=MODEL_NAME, help=f"Gemini model name (default: {MODEL_NAME})")
    parser.add_argument(
        "--temperature",
        type=float,
        default=TEMPERATURE,
        help=f"Sampling temperature (default: {TEMPERATURE})",
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=MAX_OUTPUT_TOKENS,
        help=f"Maximum output tokens (default: {MAX_OUTPUT_TOKENS})",
    )
    parser.add_argument("--notes-dir", default=NOTES_DIR, help=f"Notes directory (default: {NOTES_DIR})")
    parser.add_argument(
        "--instructions-path",
        default=INSTRUCTIONS_PATH,
        help=f"Instructions file path (default: {INSTRUCTIONS_PATH})",
    )
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help=f"Output directory (default: {OUTPUT_DIR})")
    parser.add_argument("--logs-dir", default=LOGS_DIR, help=f"Logs directory (default: {LOGS_DIR})")
    parser.add_argument("--log-file", default=LOG_FILE, help=f"Application log file (default: {LOG_FILE})")
    parser.add_argument("--log-level", default=LOG_LEVEL, help=f"Console log level (default: {LOG_LEVEL})")
    return parser.parse_args()


def main():
    """Run the flashcard generation pipeline.

    This function performs the following steps:
    - Parse CLI args and configure logging
    - Load instructions and notes
    - Clean previous output file
    - Call the AI generation routine and remove fencing
    - Log the raw CSV response and convert it into Anki-compatible text
    - Write the formatted flashcards to the output file
    It logs progress and exits the process on fatal errors encountered by helper functions.
    """
    args = parse_args()
    configure_logger(log_file=args.log_file, log_level=args.log_level)
    start = time.perf_counter()

    logging.info("Starting flashcard generation run")
    instructions = load_instructions(path=args.instructions_path)
    notes = load_notes(path=args.notes_dir)
    combined_notes = "\n\n---\n[End of Note]\n---\n\n".join(notes)
    logging.info("Loaded %s note(s), total characters=%s", len(notes), len(combined_notes))

    clean_previous_output(path=args.output_dir)

    generated_response = remove_csv_fencing(
        generate(
            PROMPT=combined_notes,
            INSTRUCTIONS=instructions,
            model=args.model,
            temperature=args.temperature,
            max_output_tokens=args.max_output_tokens,
        )
    )
    log_response_as_csv(generated_response, path=args.logs_dir)

    formatted_response = format_csv_to_text(generated_response)
    write_flashcards_to_file(formatted_response, path=args.output_dir)

    elapsed = time.perf_counter() - start
    logging.info("Run completed successfully in %.2f seconds", elapsed)


if __name__ == "__main__":
    main()
