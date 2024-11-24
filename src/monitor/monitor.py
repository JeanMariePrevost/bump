from datetime import datetime, timedelta
import json
import traceback
from queries.query import Query
from queries.query_result import QueryResult
from serialization import Deserializable
import os
from custom_logging import general_logger, monitoring_logger
import serialization


class Monitor(Deserializable):

    def __init__(self, unique_name: str = "undefined", period_in_seconds: int = 60, query: Query = None) -> None:
        self.unique_name = unique_name
        self.query = query
        self.period_in_seconds = period_in_seconds
        self._next_run_time = datetime.now() + timedelta(seconds=self.period_in_seconds)

    def execute(self):
        if not hasattr(self, "query") or self.query is None:
            monitoring_logger.error(f"Monitor {self.unique_name} has no query to execute")
            raise ValueError("Monitor has no query to execute")
        self._next_run_time = datetime.now() + timedelta(seconds=self.period_in_seconds)
        query_result: QueryResult = self.query.execute()
        monitoring_logger.debug(f"Monitor {self.unique_name} executed with result: {query_result}")

        self.check_if_status_changed(query_result)

        self.append_query_result_to_history(query_result)
        return query_result

    def check_if_status_changed(self, query_result: QueryResult) -> bool:
        previous_result = self.get_previous_query_result()
        if previous_result is not None and query_result.test_passed != previous_result.test_passed:
            monitoring_logger.warning(f"Monitor {self.unique_name} status changed from {previous_result.test_passed} to {query_result.test_passed}")
            return True
        return False

    def get_previous_query_result(self) -> QueryResult:
        try:
            target_path = f"data/history/{self.unique_name}.jsonl"
            with open(target_path, "r") as f:
                lines = f.readlines()
                if len(lines) > 0:
                    return serialization.from_encoded_json(lines[-1])
        except Exception as e:
            general_logger.error(f"Error while getting previous query result: {e}")
            traceback.print_exc()
            return None

    def execute_if_due(self):
        if datetime.now() > self._next_run_time:
            return self.execute()
        else:  # DEBUG
            general_logger.debug(f"Monitor {self.unique_name} not due yet, next run in {self._next_run_time - datetime.now()}")
        return None

    def append_query_result_to_history(self, query_result):
        try:
            target_path = f"data/history/{self.unique_name}.jsonl"
            # create the whole path if it doesn't exist
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            encoded_query_result = serialization.to_encoded_jsonl(query_result)
            with open(target_path, "a") as f:
                f.write(encoded_query_result + "\n")

        except Exception as e:
            general_logger.error(f"Error while appending query result to history: {e}")
