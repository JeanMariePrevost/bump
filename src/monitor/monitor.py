import json
import queries


class Monitor:
    @staticmethod
    def create_from_json(json_string: str) -> "Monitor":
        json_object = json.loads(json_string)
        monitor = Monitor()
        for key in json_object:
            if hasattr(monitor, key):
                setattr(monitor, key, json_object[key])

        # Fix problematic attributes
        query_type = json_object["query"]["query_type"]
        query_data_dict = json_object["query"]
        monitor.query = getattr(queries, query_type).from_dict(query_data_dict)

        return monitor

    def to_json(self):
        self_as_dict = self.__dict__.copy()

        # Fix problematic attributes
        #
        # self_as_dict["query_type"] = self.query_type.__name__
        if self.query:
            self_as_dict["query"] = self.query.__dict__.copy()
            self_as_dict["query"]["query_type"] = self.query.__class__.__name__

        return json.dumps(self_as_dict)

    def __init__(self) -> None:
        self.unique_name = "Monitor"
        self.query = None

    def execute(self):
        if not self.query:
            raise ValueError("Monitor has no query to execute")
        return self.query.execute()
