from datetime import datetime
import json
import queries


class Monitor:

    @staticmethod
    def from_dict(dict_object: dict) -> "Monitor":
        monitor = Monitor()
        for key in dict_object:
            if hasattr(monitor, key):
                setattr(monitor, key, dict_object[key])

        return monitor

    def __init__(self) -> None:
        self.unique_name = "Monitor"
        self.query = None

    def execute(self):
        if not self.query:
            raise ValueError("Monitor has no query to execute")
        return self.query.execute()
