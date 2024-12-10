import logging
import os
import re

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


def set_log_level(log_level: str):
    """Set the log level for all loggers."""
    log_level = log_level.upper()
    if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        general_logger.error(f"Invalid log level: {log_level}")
        return

    for logger in logger_manager.loggers.values():
        logger.setLevel(log_level)

    general_logger.debug(f"Log level set to: {log_level}")


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
    Expects log_file_path to be the full path, not just relative to the log directory.
    """
    log_entries = []

    accepted_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    if min_level not in accepted_log_levels:
        general_logger.error(f"Invalid log level: {min_level}")
        return log_entries
    accepted_log_levels = accepted_log_levels[accepted_log_levels.index(min_level) :]

    # The pattern that determines when to finish adding lines to the current entry and start a new one
    entry_delimiter_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}")

    try:
        with open(log_file_path, "r") as f:
            lines = f.readlines()

        selected_entries_count = 0
        current_entry = ""
        # For every line in the log file, starting from the end (i.e. most recents)
        for line in reversed(lines):
            if selected_entries_count >= mnumber_of_entries:
                break

            # Append the current line to the current entry
            current_entry = line + current_entry

            if entry_delimiter_pattern.match(line):
                # current_entry ends on this line, add it to the list if it has the right log level and start a new entry
                line_log_level = extract_log_level_from_entry(current_entry)
                if line_log_level in accepted_log_levels:
                    log_entries.append(current_entry)
                    selected_entries_count += 1

                current_entry = ""

    except Exception as e:
        general_logger.error(f"Error while reading log file: {e}")
        return []

    return log_entries
