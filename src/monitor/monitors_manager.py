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

    def save_monitors_to_file(self) -> None:
        """
        Serializes monitor objects and write them to a JSON file.
        """

        # Create path if it doesn't exist
        os.makedirs(os.path.dirname(MONITORS_JSON_FILE), exist_ok=True)

        with open(MONITORS_JSON_FILE, "w") as file:
            for monitor in self.monitors:
                monitor_as_json = monitor.to_json()
                file.write(monitor_as_json)

    def load_monitors_from_file(self) -> None:
        """
        Reads monitor objects from a JSON file and deserializes and re-create them.
        Replaces all existing monitors.
        """

        with open(MONITORS_JSON_FILE, "r") as file:
            self.monitors = [Monitor.from_dict(monitor) for monitor in json.load(file)]
