import asyncio
import threading
import mediator
from monitor.monitor import Monitor
from my_utils.simple_queue import QueueEvents
from serialization import Deserializable
from custom_logging import general_logger
import serialization

MONITOR_LOOP_INTERVAL_S = 5  # Defines the minimum "resolution" of monitor checks, i.e. even if your monitors are set to go every seconds, they will only be checked if due every MONITOR_LOOP_INTERVAL_S seconds


class MonitorsManager(Deserializable):

    def __init__(self) -> None:
        self.monitors: list[Monitor] = []
        mediator.new_monitor_results.add(lambda _: self.checkIfAllMonitorsAreUpAndValid())

    def add_monitor(self, monitor: Monitor) -> None:
        # Ensure no duplicate names
        for m in self.monitors:
            if m.unique_name == monitor.unique_name:
                raise ValueError(f"Monitor with name {monitor.unique_name} already exists")
        self.monitors.append(monitor)
        self.checkIfAllMonitorsAreUpAndValid()

    def remove_monitor(self, monitor: Monitor) -> None:
        self.monitors.remove(monitor)
        self.checkIfAllMonitorsAreUpAndValid()

    def create_and_add_empty_monitor(self) -> Monitor:
        unique_name = self.get_next_free_monitor_name()
        monitor = Monitor(unique_name=unique_name)
        self.add_monitor(monitor)
        return monitor

    def get_next_free_monitor_name(self) -> str:
        unique_name = "New monitor"
        i = 1
        while self.get_monitor_by_name(unique_name) is not None:
            unique_name = f"New monitor {i}"
            i += 1
        return unique_name

    def get_monitor_by_name(self, name: str) -> Monitor:
        for monitor in self.monitors:
            if monitor.unique_name == name:
                return monitor
        return None

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
        mediator.main_loop_exited.add(self.stop_background_monitoring_thread)

        async def background_monitoring_loop():
            while True:
                self.execute_due_monitors()

                # Wait listening for an event for a time, or continue after the timeout
                event = mediator.bg_monitoring_queue.get(timeout_s=MONITOR_LOOP_INTERVAL_S)
                if event == QueueEvents.EXIT_APP:
                    general_logger.debug("Background monitoring loop exiting")
                    break

        def thread_target():
            asyncio.run(background_monitoring_loop())  # Run the coroutine in this thread's event loop

        thread = threading.Thread(target=thread_target)
        thread.start()
        return thread

    def stop_background_monitoring_thread(self) -> None:
        mediator.bg_monitoring_queue.put(QueueEvents.EXIT_APP)

    def save_monitors_configs_to_file(self) -> None:
        # Prepare monitors for serialization
        for monitor in self.monitors:
            monitor.create_history_file_if_not_exists()  # Ensure the history files exist
            monitor.validate_monitor_configuration()  # Ensure the latest validation status is saved
            monitor.recalculate_stats()  # Ensure the latest stats are saved
        serialization.save_as_json_file(self, "data/monitors.json")

    def checkIfAllMonitorsAreUpAndValid(self):
        # Determine if all monitors are up, some are down, or some have exceptions/issues
        any_down = False
        any_exceptions = False
        for monitor in self.monitors:
            if monitor.paused:
                # Paused monitors don't factor in
                continue
            elif not monitor.last_query_passed:
                any_down = True
            elif not monitor.validate_monitor_configuration():
                any_exceptions = True
                break

        if any_down:
            # Down monitors take precedence over exceptions
            mediator.some_monitors_down.trigger()
        elif any_exceptions:
            mediator.some_monitors_have_exceptions.trigger()
        else:
            mediator.all_monitors_now_up.trigger()
