import json
from monitor.monitor import Monitor
from serialization import Deserializable


class MonitorsManager(Deserializable):

    def __init__(self) -> None:
        self.monitors = []

    def add_monitor(self, monitor: Monitor) -> None:
        self.monitors.append(monitor)

    def remove_monitor(self, monitor: Monitor) -> None:
        self.monitors.remove(monitor)

    def force_execute_monitors(self) -> None:
        """Executes all monitors and prints the result."""

        for monitor in self.monitors:
            print(f"Executing monitor {monitor.unique_name}")
            print(monitor.execute())

    def execute_due_monitors(self) -> None:
        """Executes all monitors that are due and prints the result."""

        for monitor in self.monitors:
            print(f"Executing monitor {monitor.unique_name} is due")
            print(monitor.execute_if_due())
