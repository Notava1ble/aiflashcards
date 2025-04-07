import logging
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


def configure_logger(log_file: str = "aiflashcard.log", debug: bool = False):
    """
    Configure the root logger with file and console handlers.
    This function sets up logging by:
    1. Setting the root logger's level to DEBUG to capture all log messages.
    2. Adding a file handler that writes logs to the specified file in UTF-8 encoding,
        using a formatter that includes the timestamp, log level, and message.
    3. Adding a console handler for outputting log messages below the ERROR level (to stdout)
        with colored formatting. The level for this handler is set to DEBUG if the debug flag is True,
        otherwise it is set to INFO.
    4. Adding a separate console handler for outputting ERROR and higher level log messages (to stderr)
        with colored formatting.
    Parameters:
         log_file (str): The file path for the log file. Defaults to "aiflashcard.log".
         debug (bool): If True, set the console handler level to DEBUG for more verbose output.
                            Otherwise, set it to INFO. Defaults to False.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Ensure all levels are captured

    # File handler
    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler for INFO and below (stdout)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    stdout_formatter = ColoredFormatter("%(levelname)s - %(message)s")
    stdout_handler.setFormatter(stdout_formatter)
    stdout_handler.addFilter(lambda record: record.levelno < logging.ERROR)
    logger.addHandler(stdout_handler)

    # Console handler for ERROR and above (stderr)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_formatter = ColoredFormatter("%(levelname)s - %(message)s")
    stderr_handler.setFormatter(stderr_formatter)
    logger.addHandler(stderr_handler)
