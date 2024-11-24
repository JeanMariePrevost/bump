from serialization import Deserializable


class Monitor(Deserializable):

    def __init__(self) -> None:
        self.unique_name = "Monitor"
        self.query = None

    def execute(self):
        if not hasattr(self, "query") or self.query is None:
            raise ValueError("Monitor has no query to execute")
        return self.query.execute()
