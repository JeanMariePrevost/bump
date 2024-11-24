import time
from monitor.monitor import Monitor
from monitor.monitors_manager import MonitorsManager
import serialization
from custom_logging import general_logger


general_logger.info("Starting application...")


def create_default_testing_monitors_setup():
    from queries.http_query import HttpQuery
    from queries.http_regex_query import HttpRegexQuery

    temp_query = HttpQuery(url="http://www.google.com", timeout=10)
    monitor = Monitor(unique_name="Google", period_in_seconds=16, query=temp_query)
    temp_query = HttpRegexQuery(url="https://github.com/JeanMariePrevost/p3-project-pew-pew", timeout=10, regex_to_find="proj.*pew")
    monitor2 = Monitor(unique_name="GitHub_pew_pew", period_in_seconds=8, query=temp_query)
    monitors_manager = MonitorsManager()
    monitors_manager.add_monitor(monitor)
    monitors_manager.add_monitor(monitor2)
    general_logger.info("Default monitors created successfully.")
    serialization.save_as_json_file(monitors_manager, "data/monitors.json")
    general_logger.info("Default monitors configuration file created.")


general_logger.debug("Trying to load monitors from file...")
try:
    monitors_manager: MonitorsManager = serialization.load_from_json_file("data/monitors.json")
    general_logger.info("Monitors loaded successfully.")
except FileNotFoundError:
    general_logger.warning("data/monitors.json not found. Creating default monitors setup.")
    create_default_testing_monitors_setup()
    monitors_manager: MonitorsManager = serialization.load_from_json_file("data/monitors.json")
except Exception as e:
    general_logger.error(f"An error occurred while loading monitors: {e}. Creating new monitors manager.")
    create_default_testing_monitors_setup()
    monitors_manager: MonitorsManager = serialization.load_from_json_file("data/monitors.json")


general_logger.info("Starting monitor loop.")
while True:
    monitors_manager.execute_due_monitors()
    time.sleep(2)
