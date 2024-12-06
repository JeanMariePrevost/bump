from frontend.main_page import MainPage
import mediator
from monitor.monitor import Monitor
from monitor.monitors_manager import MonitorsManager
from my_utils.simple_queue import QueueEvents
import serialization
from custom_logging import general_logger
from system_tray_icon import SystemTrayIcon
import settings_manager


general_logger.info("Starting application...")

settings_manager.load_configs()


def create_default_testing_monitors_setup():
    from queries.http_query import HttpQuery
    from queries.http_regex_query import HttpRegexQuery

    temp_query = HttpQuery(url="http://www.google.com", timeout=10)
    monitor = Monitor(unique_name="Google", period_in_seconds=16, query=temp_query)
    temp_query = HttpRegexQuery(url="https://github.com/JeanMariePrevost/p3-project-pew-pew", timeout=10, regex_to_find="proj.*pew")
    monitor2 = Monitor(unique_name="GitHub_pew_pew", period_in_seconds=8, query=temp_query)
    monitors_manager = MonitorsManager.get_instance()
    monitors_manager.add_monitor(monitor)
    monitors_manager.add_monitor(monitor2)
    general_logger.info("Default monitors created successfully.")
    monitors_manager.save_to_file()
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

mediator.register_monitors_manager(monitors_manager)
async_bg_monitoring_thread = monitors_manager.start_background_monitoring_thread()


# Start custom HTTP server in the background
from bottle_server import BottleServer

BottleServer().start_as_background_thread()


print("We started the background monitoring thread. Now we can do other things in the main thread.")

tray_icon = SystemTrayIcon()

# RIght before entiring the main loop, refresh things like the tray icon
monitors_manager.checkIfAllMonitorsAreUpAndValid()


def main_thread_loop():
    general_logger.debug("Main loop started.")
    test_window = MainPage()
    test_window.show()
    # global_events.main_thread_event_queue.put("show_gui")
    while True:
        general_logger.debug("Main loop ticking.")

        general_logger.debug("Main loop listening for next event...")
        event = mediator.main_thread_blocking_queue.get()  # Blocks until an event is received
        general_logger.debug(f"Main loop received event: {event}")

        if event == QueueEvents.EXIT_APP:
            general_logger.info("Exiting application...")
            break
        elif event == QueueEvents.OPEN_GUI:
            test_window = MainPage()
            test_window.show()
            print("Main window was closed.")
        else:
            general_logger.error(f"Unknown event received: {event}")


main_thread_loop()

mediator.main_loop_exited.trigger()

print("Main window was closed. End of script reached.")
