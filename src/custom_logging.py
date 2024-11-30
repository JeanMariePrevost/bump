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


class ColoredFormatter(logging.Formatter):
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
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
            handlers.append(file_handler)

        if self.log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(ColoredFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
            handlers.append(console_handler)

        for handler in handlers:
            logger.addHandler(handler)

        return logger


# Initialize the logger manager
logger_manager = LoggerManager()

# Predefined feeds
general_logger: logging.Logger = logger_manager.get_logger("general")
monitoring_logger: logging.Logger = logger_manager.get_logger("monitoring")


# Example usage
# from logger_manager import general_logger, monitoring_logger

# general_logger.info("This is a general log.")
# monitoring_logger.debug("This is a monitoring-specific debug log.")


def read_log_entries(log_file_path: str, mnumber_of_entries: int, level: str = "INFO"):
    """Reads and returns the last `mnumber_of_entries` log entries from the specified log file with the specified level."""
    log_entries = []

    levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if level not in levels:
        general_logger.error(f"Invalid log level: {level}")
        return log_entries
    levels = levels[levels.index(level) :]  # Get all levels from the specified level to the end

    try:
        with open(log_file_path, "r") as f:
            lines = f.readlines()
            count = 0
            for line in reversed(lines):
                if any(l in line for l in levels):
                    log_entries.append(line)
                    count += 1
                    if count >= mnumber_of_entries:
                        break
    except Exception as e:
        general_logger.error(f"Error while reading log file: {e}")
    return log_entries
    # return log_entries[::-1]  # Reverse to maintain original order?
