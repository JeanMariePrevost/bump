import logging
import os

from colorama import Fore, Back, Style, init


init(autoreset=True)

# Color definitions for logs
LEVEL_COLORS = {
    logging.DEBUG: Fore.BLUE,
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Back.RED + Fore.WHITE,
    logging.CRITICAL: Back.RED + Fore.WHITE + Style.BRIGHT,
}


class DynamicFormatter(logging.Formatter):
    """Custom formatter to dynamically change the log format based on the log level."""

    FORMATS = {
        logging.INFO: "%(asctime)s -> %(message)s",
        # TODO - Simplify the format for other levels in production too?
        "default": "%(asctime)s [%(levelname)s] (%(module)s.%(funcName)s:ln%(lineno)d) -> %(message)s",
    }

    def format(self, record):
        # Choose the format based on the log level
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS["default"])
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class ColoredFormatter(DynamicFormatter):
    """Custom formatter to add colors to the entire log string."""

    def format(self, record):
        log_color = LEVEL_COLORS.get(record.levelno, "")
        reset_color = Style.RESET_ALL
        log_line = super().format(record)
        return f"{log_color}{log_line}{reset_color}"


class LoggerManager:
    def __init__(self, log_dir="logs", log_to_file=True, log_to_console=True, log_level=logging.DEBUG):
        self.loggers = {}
        self.log_dir = log_dir
        self.log_to_file = log_to_file
        self.log_to_console = log_to_console
        self.log_level = log_level

        os.makedirs(self.log_dir, exist_ok=True)  # Ensure log directory exists

    def get_logger(self, name):
        """Retrieve or create a logger with the given name."""
        if name not in self.loggers:
            self.loggers[name] = self._setup_logger(name)
        return self.loggers[name]

    def _setup_logger(self, name):
        """Configure a logger with specific handlers and formatters."""
        logger = logging.getLogger(name)
        logger.setLevel(self.log_level)
        logger.propagate = False

        handlers = []

        if self.log_to_file:
            # Separate log file for each logger
            log_file = os.path.join(self.log_dir, f"{name}.log")

            # Ensure the directory exists
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(DynamicFormatter())
            handlers.append(file_handler)

        if self.log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(ColoredFormatter("%(asctime)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s"))
            handlers.append(console_handler)

        for handler in handlers:
            logger.addHandler(handler)

        return logger


# Initialize the logger manager
logger_manager = LoggerManager()

# Predefined feeds
general_logger: logging.Logger = logger_manager.get_logger("general")
monitoring_logger: logging.Logger = logger_manager.get_logger("monitoring")


def get_custom_logger(name: str) -> logging.Logger:
    """
    Get a custom logger with the specified name.
    The name is also used to create a log file with the same name/path.
    Example:
    custom_logger = get_custom_logger("monitors/monitor1")
    Will create a log file at "{logger_manager.log_dir}/monitors/monitor1.log"
    """
    from my_utils import util

    # Ensure the path exists
    # relative_path = logger_manager.log_dir + "/" + name
    # full_path = util.resource_path(relative_path)
    # os.makedirs(full_path, exist_ok=True)
    return logger_manager.get_logger(name)


def extract_log_level_from_entry(log_entry: str) -> str:
    """Extracts the log level from a log entry."""
    levels_patterns = ["[DEBUG]", "[INFO]", "[WARNING]", "[ERROR]", "[CRITICAL]"]
    level_if_unknown = "INFO"
    for level in levels_patterns:
        if level in log_entry:
            return level[1:-1]  # Remove brackets
    return level_if_unknown


def read_entries_from_log_file(log_file_path: str, mnumber_of_entries: int, min_level: str = "INFO"):
    """
    Reads and returns the last `mnumber_of_entries` log entries from the specified log file with the specified level.
    Expects log_file_path to be the ful path, not just relative to the log directory.
    """
    log_entries = []

    levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    if min_level not in levels:
        general_logger.error(f"Invalid log level: {min_level}")
        return log_entries
    levels = levels[levels.index(min_level) :]  # Get all levels from the specified level to the end

    try:
        with open(log_file_path, "r") as f:
            lines = f.readlines()
            count = 0
            for line in reversed(lines):
                line_log_level = extract_log_level_from_entry(line)
                if line_log_level in levels:
                    log_entries.append(line)
                    count += 1
                    if count >= mnumber_of_entries:
                        break
    except Exception as e:
        general_logger.error(f"Error while reading log file: {e}")
    return log_entries
