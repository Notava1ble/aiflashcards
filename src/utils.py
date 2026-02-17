import csv
import io
import logging
import os
import sys
from typing import List


def load_instructions(path: str = "./src/instructions.txt") -> str:
    """
    Loads instructions from the file located at './src/instructions.txt'.

    The function opens the file in read mode with UTF-8 encoding, reads its entire contents,
    and returns it as a string. If the file does not exist, it logs a fatal error and exits the program.

    Parameters:
        path (str): The file path to the instructions file. Defaults to './src/instructions.txt'.

    Returns:
        str: The contents of the instructions file.
    """
    if not os.path.exists(path):
        logging.fatal("Instructions file not found at %s. Exiting.", path)
        sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as file:
            instructions = file.read().strip()
            if not instructions:
                logging.fatal("Instructions file at %s is empty. Exiting.", path)
                sys.exit(1)
            logging.info("Loaded instructions from %s", path)
        return instructions
    except Exception as exc:
        logging.error("Error reading instructions file %s: %s", path, exc)
        sys.exit(1)


def load_notes(path: str = "./notes/") -> List[str]:
    """
    Load notes from the specified directory.

    This function reads all files within the given directory, assuming each file contains a single note.
    If the directory does not exist or no usable note files are found, the function logs a fatal error
    and exits the program.

    Parameters:
        path (str): The directory path where note files are stored. Defaults to "./notes/".

    Returns:
        List[str]: A list of strings, each representing the content of a note file.
    """
    notes = []
    if not os.path.exists(path):
        logging.fatal("Notes directory not found at %s. Exiting.", path)
        sys.exit(1)

    files = sorted(os.listdir(path))
    for file_name in files:
        file_path = os.path.join(path, file_name)

        # Skip directories and hidden files
        if os.path.isdir(file_path) or file_name.startswith("."):
            logging.debug("Skipping directory or hidden file: %s", file_path)
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                note = file.read().strip()
                if not note:
                    logging.warning("Skipping empty note file: %s", file_path)
                    continue
                notes.append(note)
                logging.debug("Loaded note from %s", file_path)
        except Exception as exc:
            logging.error("Failed reading note file %s: %s", file_path, exc)

    if not notes:
        logging.fatal("No usable notes found in %s. Exiting.", path)
        sys.exit(1)

    logging.info("Finished loading %s notes from %s", len(notes), path)
    return notes


def clean_previous_output(path: str = "./output/") -> None:
    """
    Clean previous output files in the specified directory.

    This function removes the previous `flashcards.txt` file from the given directory if it exists.

    Parameters:
        path (str): The directory path where output files are stored. Defaults to "./output/".
    """
    filepath = os.path.join(path, "flashcards.txt")
    if os.path.exists(filepath):
        logging.warning("Cleaning previous output file: %s", filepath)
        os.remove(filepath)


def remove_csv_fencing(text: str) -> str:
    """
    Removes CSV fencing from the provided text.
    This function checks whether the input text starts and ends with triple backticks ("```").
    If so, it removes the first and last lines (which are assumed to be the fencing) and returns the joined
    remaining lines. If the text is not fenced in this manner, it returns the original text unchanged.
    Parameters:
        text (str): The input string that may contain CSV fencing delineated by triple backticks.
    Returns:
        str: The processed string with fencing removed if present, otherwise the original string.
    """
    lines = text.split("\n")
    if text.startswith("```") and text.endswith("```"):
        logging.debug("CSV fencing removed: %s ... %s", lines[0], lines[-1])
        return "\n".join(lines[1:-1])

    logging.debug("No CSV fencing found: %s ... %s", lines[0], lines[-1])
    return text


def log_response_as_csv(response: str, path: str = "./logs") -> None:
    """
    Logs the provided response string as a CSV file.

    This function writes the given response into a file named "response.csv" within the specified directory.
    If the log directory does not exist, it will be created.

    Parameters:
        response (str): The CSV-formatted string to be logged.
        path (str): The directory where the "response.csv" file will be saved.
                    Defaults to "./logs".

    Returns:
        None

    Raises:
        IOError: If the file cannot be written due to an I/O related error.
    """
    if not os.path.exists(path):
        logging.debug("Creating log directory at %s", path)
        os.makedirs(path)

    logpath = os.path.join(path, "response.csv")
    with open(logpath, "w", encoding="utf-8") as file:
        file.write(response)
        logging.info("Logged raw CSV response to %s", logpath)


def format_csv_to_text(csv_data: str) -> str:
    """
    Converts CSV data into a formatted text that's parsable by Anki.

    The function reads CSV data from a string, expecting the first row to be a header (which is skipped) and each subsequent row
    to contain at least two columns representing a question and an answer. It prepends a fixed set of header lines to the output,
    formats each valid row into a tab-separated line, and returns the concatenation of these lines separated by newline characters.
    Parameters:
        csv_data (str): A string containing CSV-formatted data. The first row should be the header.
    Returns:
        str: A formatted multi-line string starting with header directives, followed by each valid CSV row in the format
             "question<tab>answer". Returns an empty string if the CSV data is empty, lacks a proper header, or an error occurs during processing.
    """
    output_header_lines = ["#separator:tab", "#html:true", "#tags column:3"]
    formatted_data_lines = []

    csv_file = io.StringIO(csv_data)
    reader = csv.reader(csv_file)

    try:
        _ = next(reader)
    except StopIteration:
        logging.warning("CSV data is empty or lacks a header row.")
        return ""
    except Exception as exc:
        logging.error("Error reading CSV header: %s", exc)
        return ""

    for row in reader:
        if len(row) >= 2:
            question = row[0].strip()
            answer = row[1].strip()
            if not question or not answer:
                logging.warning("Skipping incomplete row: %s", row)
                continue
            formatted_data_lines.append(f"{question}\t{answer}")
            logging.debug("Formatted row: %s\t%s", question, answer)
        else:
            logging.warning("Skipping malformed row: %s", row)

    logging.info("Created %s flashcards", len(formatted_data_lines))
    all_output_lines = output_header_lines + formatted_data_lines
    return "\n".join(all_output_lines)


def write_flashcards_to_file(content: str, path: str = "./output/") -> None:
    """
    Write the provided content to a file named 'flashcards.txt' in the specified directory.

    Parameters:
        content (str): The content to be written to the file.
        path (str): The directory where the file will be saved. Defaults to './output/'.
    """
    if not os.path.exists(path):
        logging.debug("Creating output directory at %s", path)
        os.makedirs(path)

    filepath = os.path.join(path, "flashcards.txt")
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content)
        logging.info("Written flashcards to %s", filepath)
