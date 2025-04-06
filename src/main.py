import io
from dotenv import load_dotenv
import os
import base64
import csv
from google import genai
from google.genai import types

load_dotenv(dotenv_path="./.env")

# Access the variable
API_KEY = os.getenv("GEMINI_2.5_API_KEY")

with open("./src/instructions.txt", "r", encoding="utf-8") as file:
    INSTRUCTIONS = file.read()

NOTES = []
for file in os.listdir("./notes"):
    with open(f"./notes/{file}", "r", encoding="utf-8") as file:
        NOTE = file.read()
        NOTES.append(NOTE)

COMBINED_NOTES = "\n\n---\n[End of Note]\n---\n\n".join(NOTES)

# Clean the previous output file
if os.path.exists("./output/flashcards.csv"):
    os.remove("./output/flashcards.csv")


def generate():
    client = genai.Client(
        api_key=API_KEY,
    )

    model = "gemini-2.5-pro-exp-03-25"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=COMBINED_NOTES),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text=INSTRUCTIONS),
        ],
    )

    text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if chunk.text:
            text += chunk.text

    return remove_csv_fencing(text)


def remove_csv_fencing(text: str) -> str:
    """
    Remove CSV fencing from the text.
    """
    if text.startswith("```") and text.endswith("```"):
        # Remove the first and last lines
        lines = text.split("\n")
        lines = lines[1:-1]

        # Join the remaining lines
        return "\n".join(lines)
    else:
        # If there is no fencing, return the text as is
        return text


def format_csv_to_text(csv_data: str) -> str:
    """
    Converts a CSV-formatted string (question, answer) into a specific
    text format with a header and tab-separated data.

    Args:
        csv_data: A string containing CSV data with a header row
                  (e.g., "question,answer") followed by data rows.
                  Values containing commas or newlines should be enclosed
                  in double quotes.

    Returns:
        A formatted string with the specified header and tab-separated
        question/answer pairs, suitable for import into certain tools.
        Returns just the header if the input CSV has no data rows after
        the header. Returns an empty string if the input is empty or
        lacks a valid header row.
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
        # Optional: You could add validation here to check if the header
        # matches expected columns if needed.
        # e.g., if header != ['question', 'answer']: print("Warning...")

    except StopIteration:
        # This occurs if the input string is empty or doesn't even contain
        # one line (the header). In this case, return an empty string
        # or perhaps just the header depending on desired behavior.
        # Let's return an empty string for truly empty/invalid input.
        return ""
    except Exception as e:
        # Catch other potential errors during initial read
        print(f"Error reading CSV header: {e}")
        return ""

    # Process the actual data rows
    for row in reader:
        # Ensure the row has at least two columns (question and answer)
        if len(row) >= 2:
            question = row[0]
            answer = row[1]
            # Format the output line with a tab character (\t) as separator
            formatted_data_lines.append(f"{question}\t{answer}")
        # else:
        # Optional: Handle or log rows that don't have enough columns
        # print(f"Skipping malformed row: {row}")
        # pass

    # Combine the fixed header lines and the formatted data lines
    all_output_lines = output_header_lines + formatted_data_lines

    # Join all lines with newline characters to create the final string
    return "\n".join(all_output_lines)


if __name__ == "__main__":
    csv_input = generate()
    print("csv created.")

    # Log the response to a file for debugging purposes
    with open("./logs/response.csv", "w", encoding="utf-8") as file:
        file.write(csv_input)

    print("Creating flashcard file")

    formatted_output = format_csv_to_text(csv_input)
    with open("./output/flashcards.txt", "w", encoding="utf-8") as file:
        file.write(formatted_output)
    print("Flashcard file created")
