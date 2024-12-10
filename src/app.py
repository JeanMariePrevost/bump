from frontend.main_page import MainPage
import mediator
from monitor.monitor import Monitor
from monitor.monitors_manager import MonitorsManager
from my_utils import util
from my_utils.simple_queue import QueueEvents
import python_js_bridge
import serialization
from custom_logging import general_logger, set_log_level
from system_tray_icon import SystemTrayIcon
import settings_manager


general_logger.info("Starting application...")

settings_manager.load_configs()
settings_manager.save_configs()

general_logger.debug("Trying to load monitors from file...")
try:
    monitors_manager: MonitorsManager = serialization.load_from_json_file("data/monitors.json")
    general_logger.info("Monitors loaded successfully.")
except FileNotFoundError:
    general_logger.warning("No monitors file found. Creating new empty file at 'data/monitors.json'.")
    monitors_manager = MonitorsManager()
    monitors_manager.save_monitors_configs_to_file()
except Exception as e:
    general_logger.error(f"An error occurred while loading monitors: {e}.")
    # Prompt user through simple tkinter dialog
    import tkinter as tk
    from tkinter import messagebox
    import os

    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Ask the user if they want to overwrite the file and start fresh
    message = (
        f"An error occurred while trying to load the monitors configuration file at 'data/monitors.json'."
        f"\n\nError: {e}"
        f"\n\nOverwrite with a new empty configuration?"
    )

    response = messagebox.askyesno("Error", message, icon=messagebox.ERROR)

    if response:
        message = "'data/monitors.json' will be overwritten.\n\nProceed?"
        response = messagebox.askyesno("Warning", message, icon=messagebox.WARNING)

    if response:
        # User chose to overwrite the file and start fresh
        monitors_manager = MonitorsManager()
        monitors_manager.save_monitors_configs_to_file()
        root.destroy()
    else:
        # Message box informing that the application cannot continue without the monitors file,
        # and that the user can try to fix it by revealing the file in Explorer
        message = (
            f"The application could not load the monitors configuration."
            f"\n\nError message: {e}"
            f"\n\nNo changes were made."
            f"\n\nYou can reload the application to start with a new empty configuration"
            f" or try to fix 'data/monitors.json' manually."
            f"\n\nOpen the config file directory before exiting?"
        )
        response = messagebox.askyesno("Error", message, icon=messagebox.ERROR)

        if response:
            # Open the directory containing the config file in Explorer and exit the application
            config_file_path = util.resource_path("data/monitors.json")
            os.startfile(os.path.dirname(config_file_path))

        root.destroy()
        general_logger.warning("Failed to load monitors. Exiting application.")
        exit()


mediator.register_monitors_manager(monitors_manager)
async_bg_monitoring_thread = monitors_manager.start_background_monitoring_thread()

python_js_bridge.hook_frontend_to_backend_signals()  # Allows the JS frontend to receive specific backend events

# Start custom HTTP server in the background
from bottle_server import BottleServer

BottleServer().start_as_background_thread()


print("We started the background monitoring thread. Now we can do other things in the main thread.")

tray_icon = SystemTrayIcon()

# Right before entiring the main loop, refresh things like the tray icon
monitors_manager.checkIfAllMonitorsAreUpAndValid()

# Apply various settings before entering the main loop
set_log_level(settings_manager.settings.general_log_level)


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
