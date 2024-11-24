from monitor.monitor import Monitor
from serialization import Deserializable
from custom_logging import general_logger


class MonitorsManager(Deserializable):

    def __init__(self) -> None:
        self.monitors: list[Monitor] = []

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
