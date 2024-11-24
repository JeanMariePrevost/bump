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


############################################################################
#### ASYNC Scratch pad
############################################################################
# import asyncio
# import threading
# import time

# shared_counter = 0
# shared_stop_bg_tasks = False


# # Define the asynchronous loop (runs in the background thread)
# async def async_loop():
#     while True:
#         if shared_stop_bg_tasks:
#             print("Background loop stopping")
#             break
#         print("Background loop ticking")
#         global shared_counter
#         shared_counter += 1
#         await asyncio.sleep(2)


# # Define the synchronous main loop (runs in the main thread)
# def main_loop(bg_thread: threading.Thread):
#     while True:
#         print(f"Main loop ticking, shared_counter={shared_counter}")
#         if shared_counter > 5:
#             print("Aaaand we're done!")
#             # Kill the background thread
#             global shared_stop_bg_tasks
#             shared_stop_bg_tasks = True
#             bg_thread.join()
#             print("Background thread joined. At this point, we are back to a single-threaded application.")
#             break
#         time.sleep(1)

#     print("Main loop exiting")
#     print("Application done.")


# # Function to start the asyncio event loop in a thread
# def run_async_loop_in_thread():
#     asyncio.run(async_loop())


# # Main entry point
# if __name__ == "__main__":
#     # Start the asyncio loop in a background thread
#     async_thread = threading.Thread(target=run_async_loop_in_thread, daemon=True)
#     async_thread.start()

#     # Run the main thread loop
#     main_loop(async_thread)
############################################################################
#### /ASYNC Scratch pad
############################################################################


def mock_gui_loop():
    duration = 4
    for i in range(duration):
        print(f"Mock gui loop will stop in {duration - i} seconds")
        time.sleep(1)
    print("Mock gui loop stopping.")


async_bg_monitoring_thread = monitors_manager.start_background_monitoring_thread()

print("We started the background monitoring thread. Now we can do other things in the main thread.")

mock_gui_loop()

print("Main thread exited the mock GUI loop.")
print("At this point, the background monitoring thread is preventing the application from exiting.")
monitors_manager.stop_bg_tasks = True
async_bg_monitoring_thread.join()
print("Background monitoring thread joined. Application exiting.")
