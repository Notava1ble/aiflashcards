import logging
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import MAX_OUTPUT_TOKENS, MODEL_NAME, TEMPERATURE

load_dotenv(dotenv_path="./.env")
API_KEY = os.getenv("GEMINI_API_KEY")


def generate(
    INSTRUCTIONS: str,
    PROMPT: str,
    model: str = MODEL_NAME,
    temperature: float = TEMPERATURE,
    max_output_tokens: int = MAX_OUTPUT_TOKENS,
) -> str:
    """
    Generates content using an AI model based on the provided prompt and system instructions.
    Parameters:
        PROMPT (str): The prompt text provided by the user to guide content generation.
        INSTRUCTIONS (str): The system instructions that influence the AI model's behavior during content generation.
        model (str): The name of the AI model to use for content generation. Defaults to MODEL_NAME from config.
        temperature (float): The sampling temperature to use for content generation. Higher values produce more random output. Defaults to TEMPERATURE from config.
        max_output_tokens (int): The maximum number of tokens to generate in the response. Defaults to MAX_OUTPUT_TOKENS from config.
    Returns:
        str: The generated content as a string.

    Raises:
        SystemExit: Exits if the GEMINI_API_KEY is not set or if the model returns no text.
    """
    if not API_KEY:
        logging.fatal("GEMINI_API_KEY is not set. Add it to your environment or .env file.")
        sys.exit(1)

    client = genai.Client(api_key=API_KEY)

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=PROMPT)],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        system_instruction=[types.Part.from_text(text=INSTRUCTIONS)],
    )

    logging.info(
        "Generating content with model='%s', temperature=%s, max_output_tokens=%s",
        model,
        temperature,
        max_output_tokens,
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    if response.text:
        logging.info("Response from AI generated successfully.")
        return response.text

    logging.fatal("No response text received from AI. Exiting.")
    sys.exit(1)
