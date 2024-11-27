from my_utils.simple_queue import SimpleQueue
from my_utils.signal import Signal

# Queues
# For inter-thread communication, where "get" blocks until an event is received
# When you need an action to be performed in a specific thread
main_thread_blocking_queue = SimpleQueue()
bg_monitoring_queue = SimpleQueue()


# Signals
# For unasfe "brodcast" communication, where all observers are called when the signal is sent
# Execution happens in the thread that sends the signal, so won't work for things like pywebview bits that need to run in the main thread
main_loop_exited = Signal()  # E.g. the main loop has exited, application is shutting down, threads need to stop
app_exit_requested = Signal()  # E.g. the user has requested the application to exit, will allow to close opened windows and such


# Shared state / blackboard
# For shared *safe* info to be accessed anywhere
gui_winow_opened = False


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
