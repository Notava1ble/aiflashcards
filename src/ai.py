import logging
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os

# Access the variable
load_dotenv(dotenv_path="./.env")
API_KEY = os.getenv("GEMINI_API_KEY")


def generate(INSTRUCTIONS: str, PROMPT: str) -> str:
    """
    Generates content using an AI model based on the provided prompt and system instructions.
    Parameters:
        PROMPT (str): The prompt text provided by the user to guide content generation.
        INSTRUCTIONS (str): The system instructions that influence the AI model's behavior during content generation.
    Returns:
        str: The generated content as a string.
    """
    client = genai.Client(
        api_key=API_KEY,
    )

    model = "gemini-2.5-pro-exp-03-25"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=PROMPT),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text=INSTRUCTIONS),
        ],
    )

    logging.info("Generating content using AI model...")

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    if response.text:
        logging.info("Response from AI generated successfully.")
        return response.text
    else:
        logging.fatal("No response received from AI. Exiting.")
        sys.exit(1)
