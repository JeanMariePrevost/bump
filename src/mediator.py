from __future__ import annotations
from typing import TYPE_CHECKING
from bottle import Bottle

from my_utils.simple_queue import SimpleQueue
from my_utils.signal import Signal

if TYPE_CHECKING:
    from frontend.gui_window import GuiWindow
    from monitor.monitors_manager import MonitorsManager

"""
A central hub for communication between different parts of the application.
"""

############################################################################################
# Queues
# For inter-thread communication, where "get" blocks until an event is received
# When you need an action to be performed in a specific thread
main_thread_blocking_queue = SimpleQueue()
bg_monitoring_queue = SimpleQueue()

############################################################################################
# Signals
# For unasfe "brodcast" communication, where all observers are called when the signal is sent
# Execution happens in the thread that sends the signal, so won't work for things like pywebview bits that need to run in the main thread
main_loop_exited = Signal()  # E.g. the main loop has exited, application is shutting down, threads need to stop
app_exit_requested = Signal()  # E.g. the user has requested the application to exit, will allow to close opened windows and such

all_monitors_now_up = Signal()  # all monitors are now up, change the tray icon to normal
some_monitors_down = Signal()  # some monitors are now down, change the tray icon to down
some_monitors_have_exceptions = Signal()  # some monitors now have exceptions, change the tray icon to warning
new_monitor_results = Signal(str)  # new results have been received from any monitor, with the monitor's unique name as the argument
monitor_status_changed = Signal(str)  # the status of a monitor has changed, with the monitor's unique name as the argument


############################################################################################
# Shared state / blackboard
# For shared *safe* info to be accessed anywhere
__active_gui: GuiWindow | None = None
__monitors_manager: MonitorsManager | None = None
__http_server: Bottle | None = None


def register_active_gui(window: GuiWindow | None):
    if window.__class__.__name__ != "GuiWindow":
        raise ValueError("Invalid type")
    global __active_gui
    __active_gui = window


def get_active_gui() -> GuiWindow | None:
    return __active_gui


def register_monitors_manager(monitors_manager: MonitorsManager | None):
    if monitors_manager.__class__.__name__ != "MonitorsManager":
        raise ValueError("Invalid type")
    global __monitors_manager
    __monitors_manager = monitors_manager


def get_monitors_manager() -> MonitorsManager | None:
    if __monitors_manager is None:
        raise ValueError("Monitors manager not set")
    return __monitors_manager


def register_http_server(server: Bottle | None):
    if server.__class__.__name__ != "Bottle":
        raise ValueError("Invalid type")
    global __http_server
    __http_server = server


def get_http_server() -> Bottle | None:
    if __http_server is None:
        raise ValueError("HTTP server not set")
    return __http_server


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
