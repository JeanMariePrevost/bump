import asyncio
import threading
import global_events
from monitor.monitor import Monitor
from serialization import Deserializable
from custom_logging import general_logger


class MonitorsManager(Deserializable):

    def __init__(self) -> None:
        self.monitors: list[Monitor] = []
        self.__bg_monitoring_running = False

    def add_monitor(self, monitor: Monitor) -> None:
        # Assert no duplicate names
        for m in self.monitors:
            if m.unique_name == monitor.unique_name:
                raise ValueError(f"Monitor with name {monitor.unique_name} already exists")
        self.monitors.append(monitor)

    def remove_monitor(self, monitor: Monitor) -> None:
        self.monitors.remove(monitor)

    def force_execute_monitors(self) -> None:
        """Executes all monitors and prints the result."""

        for monitor in self.monitors:
            general_logger.debug(f"Executing monitor {monitor.unique_name}")
            general_logger.debug(monitor.execute())

    def execute_due_monitors(self) -> None:
        """Executes all monitors that are due and prints the result."""

        for monitor in self.monitors:
            monitor.execute_if_due()

    def start_background_monitoring_thread(self) -> threading.Thread:
        """Starts a background thread that continuously executes due monitors."""

        self.__bg_monitoring_running = True
        global_events.test_stop_bg_thread_signal.add(self.stop_background_monitoring_thread)

        async def background_monitoring_loop():
            while self.__bg_monitoring_running:
                general_logger.debug("Background monitoring loop ticking")
                self.execute_due_monitors()
                await asyncio.sleep(3)

        def thread_target():
            asyncio.run(background_monitoring_loop())  # Run the coroutine in this thread's event loop

        thread = threading.Thread(target=thread_target)
        thread.start()
        return thread

    def stop_background_monitoring_thread(self) -> None:
        self.__bg_monitoring_running = False
