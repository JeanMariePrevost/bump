from queue import Queue
from my_utils.signal import Signal

# Queue for sending stuff that NEEDS to be handled in the main thread, e.g. showing pywebview windows
__main_thread_event_queue = Queue()


main_loop_exited = Signal()  # E.g. the main loop has exited, application is shutting down, threads need to stop


def request_to_show_gui():
    __main_thread_event_queue.put("show_gui")


def request_to_exit_app():
    __main_thread_event_queue.put("exit")


# Signals to probably add:
# Monitor state changed
# errors?

# Other potential events:
# Monitor added
# Monitor removed
# Monitor modified
# Monitor executed / new results in


# Signals to WEAK MAYBE CONSIDER adding:
# Monitor due state changed
# Monitor execution failed
