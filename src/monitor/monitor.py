from datetime import datetime, timedelta
from serialization import Deserializable


class Monitor(Deserializable):

    def __init__(self) -> None:
        self.unique_name = "Monitor"
        self.query = None
        self.period_in_seconds = 6
        self.next_run_time = datetime.now() + timedelta(seconds=self.period_in_seconds)

    def execute(self):
        if not hasattr(self, "query") or self.query is None:
            raise ValueError("Monitor has no query to execute")
        self.next_run_time = datetime.now() + timedelta(seconds=self.period_in_seconds)
        return self.query.execute()

    def execute_if_due(self):
        if datetime.now() > self.next_run_time:
            self.next_run_time = datetime.now() + timedelta(seconds=self.period_in_seconds)
            return self.execute()
        else:  # DEBUG
            print(f"Monitor {self.unique_name} not due yet, next run in {self.next_run_time - datetime.now()}")
        return None
