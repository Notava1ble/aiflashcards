import logging
import os
import sys


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors based on log level."""

    COLORS = {
        logging.DEBUG: "\033[90m",  # Gray
        logging.INFO: "\033[94m",  # Blue
        logging.WARNING: "\033[93m",  # Yellow
        logging.ERROR: "\033[91m",  # Red
        logging.CRITICAL: "\033[1;91m",  # Bold Red
    }
    RESET = "\033[0m"

    def format(self, record):
        log_color = self.COLORS.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{log_color}{message}{self.RESET}"


def configure_logger(log_file: str = "aiflashcard.log", log_level: str = "INFO"):
    """Configure root logger with file and colored console handlers.

    Sets up a file handler that records DEBUG and above to `log_file`, and two console handlers:
    one (stdout) for messages below ERROR with colored output at the configured level, and one
    (stderr) for ERROR and above. The root logger level is set to DEBUG to allow the file handler
    to capture full history while console verbosity is controlled by `log_level`.

    Parameters:
        log_file (str): The file path for the log file. Defaults to "aiflashcard.log".
        log_level (str): The console log level name (e.g. "INFO", "DEBUG"). Defaults to "INFO".
    """
    logger = logging.getLogger()

    # Prevent duplicate logs when main() is called multiple times (tests, notebooks).
    logger.handlers.clear()

    resolved_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(logging.DEBUG)

    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    # File handler (full debug history)
    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler for INFO/WARN/DEBUG (stdout)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(resolved_level)
    stdout_handler.setFormatter(ColoredFormatter("%(levelname)s - %(message)s"))
    stdout_handler.addFilter(lambda record: record.levelno < logging.ERROR)
    logger.addHandler(stdout_handler)

    # Console handler for ERROR+ (stderr)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(ColoredFormatter("%(levelname)s - %(message)s"))
    logger.addHandler(stderr_handler)
