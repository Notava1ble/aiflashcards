import os
from dotenv import load_dotenv

# Load environment variables from .env early so config picks them up when imported.
load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.2"))
MAX_OUTPUT_TOKENS = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "8192"))

LOG_FILE = os.getenv("APP_LOG_FILE", "aiflashcard.log")
LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "INFO").upper()

NOTES_DIR = os.getenv("NOTES_DIR", "./notes/")
INSTRUCTIONS_PATH = os.getenv("INSTRUCTIONS_PATH", "./src/instructions.txt")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output/")
LOGS_DIR = os.getenv("LOGS_DIR", "./logs")
