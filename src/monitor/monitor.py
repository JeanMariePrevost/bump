from datetime import datetime, timedelta
from enum import Enum
import os
import traceback
from queries.query import Query
from queries.query_result import QueryResult
from serialization import Deserializable
from custom_logging import monitoring_logger
import serialization
from custom_logging import general_logger


class Monitor(Deserializable):

    def __init__(self, unique_name: str = "undefined", period_in_seconds: int = 60, query: Query = None) -> None:
        self.unique_name = unique_name
        self.query = query
        self.period_in_seconds = period_in_seconds
        self._next_run_time = datetime.now() + timedelta(seconds=self.period_in_seconds)
        self.last_query_passed = False

    def execute(self):
        if not hasattr(self, "query") or self.query is None:
            monitoring_logger.error(f"Monitor {self.unique_name} has no query to execute")
            raise ValueError("Monitor has no query to execute")
        self._next_run_time = datetime.now() + timedelta(seconds=self.period_in_seconds)
        query_result: QueryResult = self.query.execute()
        monitoring_logger.debug(f"Monitor {self.unique_name} executed with result: {query_result}")

        self.last_query_passed = query_result.test_passed  # Needed by the GUI as it doesn't have direct access to the query results

        self.update_satus_variables(query_result)

        self.append_query_result_to_history(query_result)
        return query_result

    def update_satus_variables(self, query_result: QueryResult):
        # Trigger a status change if the status changed
        if self.current_status != query_result.test_passed:
            # TODO - Signal the change
            monitoring_logger.warning(f"Monitor {self.unique_name} status changed from [{self.current_status}] to [{query_result.test_passed}]")
        self.current_status = query_result.test_passed

    def read_results_from_history(self, count: int) -> list[QueryResult]:
        resultsList = []
        try:
            target_path = f"data/history/{self.unique_name}.jsonl"
            with open(target_path, "r") as f:
                lines = f.readlines()
                if len(lines) > 0:
                    capped_count = min(count, len(lines))  # Avoid reading more entries than we have
                    for line in lines[-capped_count:]:
                        resultsList.append(serialization.from_encoded_jsonl(line))
                    return resultsList
        except Exception as e:
            general_logger.error(f"Error while getting previous query result: {e}")
            traceback.print_exc()
            return []

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
