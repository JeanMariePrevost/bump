import os
import tkinter as tk
from tkinter import messagebox

import common.custom_logging as custom_logging
import common.mediator as mediator
import common.python_js_bridge as python_js_bridge
import sys

from frontend.bottle_server import BottleServer
from common.custom_logging import get_general_logger, set_log_level
from frontend.gui_window import GuiWindow
from monitor.monitors_manager import MonitorsManager
from common import util
from common.simple_queue import QueueEvents
import common.serialization as serialization
from common.system_tray_icon import SystemTrayIcon
import common.settings_manager as settings_manager


def define_cwd():
    """
    Set the working directory to the project root directory.
    Required for the application to work identically when run as a script, in an IDE, or as a bundled app.
    """
    current_script_path = os.path.abspath(__file__)  # Get the absolute path of the current script
    project_root_directory = os.path.dirname(os.path.dirname(current_script_path))  # Determine the root directory (parent of 'src')
    os.chdir(project_root_directory)  # Set the working directory to the project root
    print(f"Working directory set to: {os.getcwd()}")  # Debug: Print the current working directory


def load_monitors_configuration():
    """
    Load the monitors configuration from the 'data/monitors.json' file.
    Handles cases like file not found or errors during loading.
    """

    get_general_logger().debug("Trying to load monitors from file...")
    try:
        monitors_manager = serialization.load_from_json_file("data/monitors.json")
        get_general_logger().info("Monitors loaded successfully.")
    except FileNotFoundError:
        get_general_logger().warning("No monitors file found. Creating new empty file at 'data/monitors.json'.")
        monitors_manager = MonitorsManager()
        monitors_manager.save_monitors_configs_to_file()
    except Exception as e:
        # Failed to load the monitors configuration file.
        # Prompt the user about overwriting the faulty config with a new empty one.
        get_general_logger().error(f"An error occurred while loading monitors: {e}.")

        root = tk.Tk()
        root.withdraw()
        message = (
            f"An error occurred while trying to load the monitors configuration file at 'data/monitors.json'."
            f"\n\nError: {e}"
            f"\n\nOverwrite with a new empty configuration?"
        )
        user_wish_to_overwrite = messagebox.askyesno(title="Error", message=message, icon=messagebox.ERROR)
        user_wish_to_overwrite = messagebox.askyesno("Error", message, icon=messagebox.ERROR)

        if user_wish_to_overwrite:
            message = "'data/monitors.json' will be overwritten.\n\nProceed?"
            user_confirmed = messagebox.askyesno("Warning", message, icon=messagebox.WARNING)

        if user_wish_to_overwrite and user_confirmed:
            # User chose to overwrite the file and start fresh
            monitors_manager = MonitorsManager()
            monitors_manager.save_monitors_configs_to_file()
            root.destroy()
        else:
            # Could not load and user refused to start fresh, cannot proceed
            message = (
                f"The application could not load the monitors configuration."
                f"\n\nError message: {e}"
                f"\n\nNo changes were made."
                f"\n\nYou can reload the application to start with a new empty configuration"
                f" or try to fix 'data/monitors.json' manually."
                f"\n\nOpen the config file directory before exiting?"
            )
            reveal_config_file = messagebox.askyesno("Error", message, icon=messagebox.ERROR)

            if reveal_config_file:
                # Open the directory containing the config file in Explorer
                config_file_path = util.resolve_relative_path("data/monitors.json")
                os.startfile(os.path.dirname(config_file_path))

            root.destroy()
            get_general_logger().warning("Failed to load monitors. Exiting application.")
            sys.exit()

    # Reaching this point means the monitors were loaded successfully or a new empty configuration was created
    mediator.register_monitors_manager(monitors_manager)


def main_thread_loop():
    get_general_logger().debug("Main loop started.")
    test_window = GuiWindow()
    test_window.show()
    # global_events.main_thread_event_queue.put("show_gui")
    while True:
        get_general_logger().debug("Main loop ticking.")

        get_general_logger().debug("Main loop listening for next event...")
        event = mediator.main_thread_blocking_queue.get()  # Blocks until an event is received
        get_general_logger().debug(f"Main loop received event: {event}")

        if event == QueueEvents.EXIT_APP:
            get_general_logger().info("Exiting application...")
            break
        elif event == QueueEvents.OPEN_GUI:
            test_window = GuiWindow()
            test_window.show()
            print("Main window was closed.")
        else:
            get_general_logger().error(f"Unknown event received: {event}")


if __name__ == "__main__":
    # NOTE: Order of operations is important in multiple places here
    # (e.g. defining the working directory before loading settings, loading settings before setting log level, etc.)

    define_cwd()  # Has to be called before any code that relies on relative paths
    custom_logging.initialize()
    settings_manager.load_configs()
    set_log_level(settings_manager.settings.general_log_level)
    get_general_logger().info("Application starting...")

    load_monitors_configuration()
    python_js_bridge.hook_frontend_to_backend_signals()  # Allows the JS frontend to receive specific backend events
    bottle_server = BottleServer()
    bottle_server.start_as_background_thread()  # Start custom HTTP server for the pywebview GUI
    async_bg_monitoring_thread = mediator.get_monitors_manager().start_background_monitoring_thread()
    tray_icon = SystemTrayIcon()  # Create the tray icon

    # Once all background services are set up,
    # check monitors validity and status to immediately refresh things like the tray icon
    mediator.get_monitors_manager().checkIfAllMonitorsAreUpAndValid()

    # Start the main thread loop
    main_thread_loop()

    # Main loop exited, stop all background services and exit the application
    mediator.main_loop_exited.trigger()

    print("Main window was closed. End of script reached.")

    sys.exit()
