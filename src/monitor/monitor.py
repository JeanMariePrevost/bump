from datetime import datetime, timedelta
from queries.query import Query
from serialization import Deserializable


class Monitor(Deserializable):

    def __init__(self, unique_name: str = "undefined", period_in_seconds: int = 60, query: Query = None) -> None:
        self.unique_name = unique_name
        self.query = query
        self.period_in_seconds = period_in_seconds
        self._next_run_time = datetime.now() + timedelta(seconds=self.period_in_seconds)

    def execute(self):
        if not hasattr(self, "query") or self.query is None:
            raise ValueError("Monitor has no query to execute")
        self._next_run_time = datetime.now() + timedelta(seconds=self.period_in_seconds)
        return self.query.execute()

    def execute_if_due(self):
        if datetime.now() > self._next_run_time:
            return self.execute()
        else:  # DEBUG
            print(f"Monitor {self.unique_name} not due yet, next run in {self._next_run_time - datetime.now()}")
        return None
