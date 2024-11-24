import json
from monitor.monitor import Monitor
import os

MONITORS_JSON_FILE = "data/monitors.json"


class MonitorsManager:
    def __init__(self) -> None:
        self.monitors = []

    def add_monitor(self, monitor: Monitor) -> None:
        self.monitors.append(monitor)

    def remove_monitor(self, monitor: Monitor) -> None:
        self.monitors.remove(monitor)

    def load_monitors_from_file(self) -> None:
        """
        Reads monitor objects from a JSON file and deserializes and re-create them.
        Replaces all existing monitors.
        """

        with open(MONITORS_JSON_FILE, "r") as file:
            self.monitors = [Monitor.from_dict(monitor) for monitor in json.load(file)]

    def execute_monitors(self) -> None:
        """
        Executes all monitors and prints the result.
        """

        for monitor in self.monitors:
            print(f"Executing monitor {monitor.unique_name}")
            print(monitor.execute())
