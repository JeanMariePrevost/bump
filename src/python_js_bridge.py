import json
import webview

from custom_logging import general_logger
import custom_logging
import mediator
import serialization

__js_api = None


def send_event_to_js(window: webview.Window, event_type: str, data: dict):
    if window is None:
        general_logger.exception("send_event_to_js: Window is None, cannot send event.")
        return
    js_code = f"window.dispatchEvent(new CustomEvent('{event_type}', {{ detail: {json.dumps(data)} }}));"
    window.evaluate_js(js_code)
    print(f"Sent event: {event_type} with data: {data}")


class JsApi:
    """
    Defines the set of functions that the *JavaScript* side can call on the Python side.
    """

    # NOTE: Send json-compatible dictionaries, simple types, or strings as data
    # use serialization.to_dict_encoded_with_types to create safe dictionaries containing non-simple objects
    # use serialization.to_encoded_json to create safe JSON strings

    def send_event_to_python(self, event_type, data):
        print(f"Received event: {event_type} with data: {data}")
        pass

    def test_request_some_data(self, input_string: str):
        print(f"Received request for data with input: {input_string}")
        result = input_string + " - modified on the Python side"
        return {"data": result}

    def request_all_monitors_data(self):
        print("Received request for monitors data")
        # return mediator.get_monitors_manager().monitors
        return serialization.to_dict_encoded_with_types(mediator.get_monitors_manager().monitors)

    def request_monitor_data(self, unique_name: str):
        print(f"Received request for monitor data: {unique_name}")
        targetMonitor = mediator.get_monitors_manager().get_monitor_by_name(unique_name)
        targetMonitor.recalculate_stats()  # Send the frontend the latest stats for monitor details
        return serialization.to_dict_encoded_with_types(targetMonitor)

    def request_monitor_history(self, unique_name: str, max_number_of_entries: int):
        print(f"Received request for monitor history: {unique_name}")
        targetMonitor = mediator.get_monitors_manager().get_monitor_by_name(unique_name)
        if targetMonitor is None:
            general_logger.error(f"Monitor {unique_name} requested but not found.")
            return {}
        history = targetMonitor.read_results_from_history(max_number_of_entries)
        # encodedJson = serialization.to_dict_encoded_with_types(history)
        return serialization.to_dict_encoded_with_types(history)

    def request_log_entries(self, max_number_of_entries: int, min_level: str = "INFO", include_general: bool = True, include_monitoring: bool = True):
        print(f"Received request for log entries")
        # Parse BOTH log files for entries of a given level or higher
        log_entries = []
        if include_general:
            log_entries += custom_logging.read_log_entries("logs/general.log", max_number_of_entries, min_level)
        if include_monitoring:
            log_entries += custom_logging.read_log_entries("logs/monitoring.log", max_number_of_entries, min_level)

        # Sort alphanumerically descending since they start with a timestamp
        log_entries.sort(reverse=True)

        # Return the last max_number_of_entries
        return log_entries[-max_number_of_entries:]


def get_js_api():
    global __js_api
    if __js_api is None:
        __js_api = JsApi()
    return __js_api
