from datetime import datetime, timedelta
from enum import Enum
import os
import traceback
import mediator
from my_utils.util import get_query_class_from_string, is_valid_filename, is_valid_url
from queries.query import Query
from queries.query_result import QueryResult
from serialization import Deserializable
from custom_logging import monitoring_logger
import serialization
from custom_logging import general_logger

AVG_STATS_TIMESPAN_DAYS = 7


class Monitor(Deserializable):

    def __init__(self, unique_name: str = "undefined", period_in_seconds: int = 60, query: Query = None) -> None:
        self.unique_name = unique_name
        self.query = query
        self.period_in_seconds = period_in_seconds
        self.retries = 0
        self.retries_interval_in_seconds = 1
        self._next_run_time = datetime.now() + timedelta(seconds=self.period_in_seconds)
        self.last_query_passed = False
        self.time_at_last_status_change = datetime.now()
        self.stats_avg_uptime = 0
        self.stats_avg_latency = 0

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
            target_path = self.get_history_file_path()
            with open(target_path, "r") as f:
                lines = f.readlines()
                if len(lines) > 0:
                    capped_count = min(count, len(lines))  # Avoid reading more entries than we have
                    for line in lines[-capped_count:]:
                        resultsList.append(serialization.from_encoded_json(line))
                    return resultsList
        except Exception as e:
            general_logger.error(f"Error while getting previous query result: {e}")
            traceback.print_exc()
            return []

    def read_results_from_history_days(self, days_to_read: int) -> list[QueryResult]:
        resultsList = []
        try:
            target_path = self.get_history_file_path()
            with open(target_path, "r") as f:
                lines = f.readlines()
                if len(lines) > 0:
                    for line in lines:
                        result: QueryResult = serialization.from_encoded_json(line)
                        if datetime.now() - result.end_time < timedelta(days=days_to_read):
                            resultsList.append(result)
                    return resultsList
        except Exception as e:
            general_logger.error(f"Error while getting previous query result: {e}")
            traceback.print_exc()
            return []
        return resultsList

    def execute_if_due(self):
        if datetime.now() > self._next_run_time:
            return self.execute()
        else:  # DEBUG
            general_logger.debug(f"Monitor {self.unique_name} not due yet, next run in {self._next_run_time - datetime.now()}")
        return None

    def append_query_result_to_history(self, query_result):
        try:
            target_path = self.get_history_file_path()
            self.create_history_file_if_not_exists()
            encoded_query_result = serialization.to_encoded_jsonl(query_result)
            with open(target_path, "a") as f:
                f.write(encoded_query_result + "\n")

        except Exception as e:
            general_logger.error(f"Error while appending query result to history: {e}")

    def create_history_file_if_not_exists(self):
        target_path = self.get_history_file_path()
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        if not os.path.exists(target_path):
            general_logger.debug(f"Monitor {self.unique_name} did not have a history file, creating one now.")
            with open(target_path, "w") as f:
                f.write("")  # Create an empty file

    def recalculate_stats(self):
        results = self.read_results_from_history_days(AVG_STATS_TIMESPAN_DAYS)
        if len(results) > 0:
            uptime_sum = 0
            latency_sum = 0
            for result in results:
                uptime_sum += result.test_passed
                latency_sum += result.calcualte_latency()
            self.stats_avg_uptime = uptime_sum / len(results)
            self.stats_avg_latency = latency_sum / len(results)
            self.time_at_last_status_change = results[0].end_time  # Default to oldest result at first
            for result in results:
                if result.test_passed != self.last_query_passed:
                    self.time_at_last_status_change = result.end_time  # Update to the most recent status change if any
                    break
        else:
            self.stats_avg_uptime = 0
            self.stats_avg_latency = 0
            self.time_at_last_status_change = datetime.now()

    def get_history_file_path(self):
        return f"data/history/{self.unique_name}.jsonl"

    def validate_and_apply_config_from_frontend(self, config: dict) -> None:
        """
        Applies the configuration received from the frontend if valid, otherwise raises an exception
        :param config: The object received from the frontend
        """

        # from python_js_bridge import VALID_QUERY_TYPES

        # VALIDATION
        # Original name must be an existing monitor name
        if "original_name" not in config or type(config["original_name"]) is not str:
            raise ValueError("original_name is missing or invalid")
        targetMonitor = mediator.get_monitors_manager().get_monitor_by_name(config["original_name"])
        if targetMonitor is None:
            raise ValueError("original_name does not match any existing monitor")

        # unique_name must be a non-null, non-empty string that is also a valid filename and unique
        if "unique_name" not in config or type(config["unique_name"]) is not str or len(config["unique_name"]) == 0:
            raise ValueError("unique_name is missing or invalid")
        if not is_valid_filename(config["unique_name"]):
            raise ValueError("unique_name is not a valid filename")

        # query_url must be a non-null, non-empty string, and a valid URL
        if "query_url" not in config or type(config["query_url"]) is not str or len(config["query_url"]) == 0:
            raise ValueError("query_url is missing or invalid")
        if not is_valid_url(config["query_url"]):
            raise ValueError("query_url is not a valid URL")

        # query_type must be a non-null, non-empty string that is also a valid query type
        if "query_type" not in config or type(config["query_type"]) is not str:
            raise ValueError("query_type is missing or invalid")
        # Test whether config["query_type"] is an existing fully qualified class name in the queries package
        queryType = get_query_class_from_string(f"{config['query_type']}")
        if queryType is None:
            raise ValueError("query_type not a known query type")

        # Testing query_params_string requires creating a query object temporarily and passing the string to it
        validation_query: Query = queryType()
        try:
            validation_query.apply_query_params_string(config["query_params_string"])
        except Exception as e:
            raise ValueError(f"query_params_string is invalid: {str(e)}")

        # period_in_seconds must be a positive integer
        if "period_in_seconds" not in config or int(config["period_in_seconds"]) <= 0:
            raise ValueError("period_in_seconds is missing or invalid")

        # retries must be a positive integer
        if "retries" not in config or int(config["retries"]) < 0:
            raise ValueError("retries is missing or invalid")

        # retries_interval_in_seconds must be a positive integer
        if "retries_interval_in_seconds" not in config or int(config["retries_interval_in_seconds"]) < 0:
            raise ValueError("retries_interval_in_seconds is missing or invalid")

        # APPLICATION
        # Apply the new configuration
        targetMonitor.unique_name = config["unique_name"]
        targetMonitor.query = get_query_class_from_string(f"{config['query_type']}")()
        targetMonitor.query.apply_query_params_string(config["query_params_string"])
        targetMonitor.query.url = config["query_url"]
        targetMonitor.period_in_seconds = int(config["period_in_seconds"])
        targetMonitor.retries = int(config["retries"])
        targetMonitor.retries_interval_in_seconds = int(config["retries_interval_in_seconds"])
        # targetMonitor.last_query_passed = False
        # targetMonitor.time_at_last_status_change = datetime.now()
        # targetMonitor.stats_avg_uptime = 0
        # targetMonitor.stats_avg_latency = 0
        targetMonitor._next_run_time = datetime.now() + timedelta(seconds=self.period_in_seconds)

        # Special considerations for monitor renames
        try:
            if targetMonitor.unique_name != config["original_name"]:
                # Rename the history file if it exists
                old_history_path = f"data/history/{config['original_name']}.jsonl"
                if os.path.exists(old_history_path):
                    os.rename(old_history_path, f"data/history/{targetMonitor.unique_name}.jsonl")
        except Exception as e:
            general_logger.error(f"Error while renaming monitor history file: {e}")
            traceback.print_exc()
