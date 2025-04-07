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
        logging.fatal(f"Instructions file not found at {path}. Exiting.")
        sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as file:
            INSTRUCTIONS = file.read()
            logging.info(f"Loaded instructions from {path}")
        return INSTRUCTIONS
    except Exception as e:
        logging.error(f"Error reading instructions file: {e}")
        sys.exit(1)


def load_notes(path: str = "./notes/") -> List[str]:
    """
    Load notes from the specified directory.
    This function reads all files within the given directory, assuming each file contains a single note.
    If the directory does not exist, it logs a warning and exits the program.
    Parameters:
        path (str): The directory path where note files are stored. Defaults to "./notes/".
    Returns:
        list: A list of strings, each representing the content of a note file.
    """
    NOTES = []
    if not os.path.exists(path):
        logging.warning(f"Notes directory not found at {path}. Exiting.")
        sys.exit(1)
    for file in os.listdir(path):
        # Skip directories and hidden files
        if os.path.isdir(file) or file.startswith("."):
            logging.debug(f"Skipping directory or hidden file: {file}")
            continue

        file_path = os.path.join(path, file)
        with open(file_path, "r", encoding="utf-8") as file:
            NOTE = file.read()
            NOTES.append(NOTE)
            logging.debug(f"Loaded note from {file_path}")

    logging.info(f"Finished loading {len(NOTES)} notes from {path}")
    return NOTES


def clean_previous_output(path: str = "./output/") -> None:
    """
    Clean previous output files in the specified directory.
    This function removes all files within the given directory.
    Parameters:
        path (str): The directory path where output files are stored. Defaults to "./output/".
    """
    filepath = f"{path}/flashcards.txt"
    if os.path.exists(filepath):
        logging.warning(f"Cleaning previous output file: {filepath}")
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
        logging.debug(
            "The csv fencing removed is %s ... %s",
            lines[0],
            lines[-1],
        )

        # Remove the first and last lines
        lines = lines[1:-1]

        # Join the remaining lines
        return "\n".join(lines)
    else:
        # If there is no fencing, return the text as is
        logging.debug(
            "No csv fencing found. The first and last lines are %s ... %s",
            lines[0],
            lines[-1],
        )
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
    # Ensure the directory exists
    if not os.path.exists(path):
        logging.debug(f"Creating log directory at {path}")
        os.makedirs(path)

    logpath = os.path.join(path, "response.csv")
    with open(logpath, "w", encoding="utf-8") as file:
        file.write(response)
        logging.info(f"Logged csv response to {logpath}")


def format_csv_to_text(csv_data: str) -> str:
    """
    Converts CSV data into a formatted text that's parspable by Anki

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

    # Use io.StringIO to treat the input string like an in-memory text file
    # This allows the csv module to read from it directly.
    csv_file = io.StringIO(csv_data)

    # Create a CSV reader object. It automatically handles quoted fields.
    # Default delimiter is comma, default quote character is double-quote.
    reader = csv.reader(csv_file)

    try:
        # Read and discard the header row (e.g., "question,answer")
        header = next(reader)

    except StopIteration:
        # This occurs if the input string is empty or doesn't even contain
        # one line (the header). In this case, return an empty string
        logging.warning("CSV data is empty or lacks a header row.")
        return ""
    except Exception as e:
        # Catch other potential errors during initial read
        logging.error(f"Error reading CSV header: {e}")
        return ""

    # Process the actual data rows
    for row in reader:
        # Ensure the row has at least two columns (question and answer)
        if len(row) >= 2:
            question = row[0]
            answer = row[1]
            # Format the output line with a tab character (\t) as separator
            formatted_data_lines.append(f"{question}\t{answer}")
            logging.debug("Formatted row: %s\t%s", question, answer)
        else:
            logging.warning("Skipping malformed row: %s", row)

    logging.info("Created %s flashcards", len(formatted_data_lines))
    # Combine the fixed header lines and the formatted data lines
    all_output_lines = output_header_lines + formatted_data_lines

    # Join all lines with newline characters to create the final string
    return "\n".join(all_output_lines)


def write_flashcards_to_file(content: str, path: str = "./output/") -> None:
    """
    Write the provided content to a file named 'flashcards.txt' in the specified directory.

    Parameters:
        content (str): The content to be written to the file.
        path (str): The directory where the file will be saved. Defaults to './output/'.
    """
    if not os.path.exists(path):
        logging.debug(f"Creating output directory at {path}")
        os.makedirs(path)

    filepath = os.path.join(path, "flashcards.txt")
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content)
        logging.info(f"Written flashcards to {filepath}")
