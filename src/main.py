import io
from dotenv import load_dotenv
import csv

from ai import generate
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


def main():
    configure_logger()
    INSTRUCTIONS = load_instructions()
    NOTES = load_notes()
    COMBINED_NOTES = "\n\n---\n[End of Note]\n---\n\n".join(NOTES)

    clean_previous_output()

    generated_response = remove_csv_fencing(
        generate(PROMPT=COMBINED_NOTES, INSTRUCTIONS=INSTRUCTIONS)
    )
    log_response_as_csv(generated_response)

    formatted_response = format_csv_to_text(generated_response)

    write_flashcards_to_file(formatted_response)


if __name__ == "__main__":
    main()
