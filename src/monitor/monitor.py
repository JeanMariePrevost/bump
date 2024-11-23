import queries
import json

from queries.http_query import HttpQuery


class Monitor:
    @staticmethod
    def create_from_json(json_string: str) -> "Monitor":
        monitor = Monitor()
        # Debug: trying to get the query type from a string
        json_object = json.loads(json_string)
        # monitor.query_type = getattr(queries, json_object["query_type"])

        # Debug: print every attribute of queries
        print(dir(queries))
        return monitor

    def to_json(self):
        self_as_dict = self.__dict__.copy()
        # Turn problematic fields into strings
        self_as_dict["query_type"] = self.query_type.__name__

        return json.dumps(self_as_dict)

    def __init__(self) -> None:
        self.unique_name = "Monitor"
        self.url = "http://www.google.com"
        self.timeout = 1
        self.query_type = HttpQuery
        self.extra_query_params = {"expected_status_code": 200}

    def execute(self):
        return self.query_type(url=self.url, timeout=self.timeout).execute()
