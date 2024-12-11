import json
import webview

import credentials_manager
from custom_logging import general_logger, read_entries_from_log_file
from my_utils.simple_queue import QueueEvents
import my_utils.util
import mediator
from monitor.monitor import Monitor
from queries.query import Query
import serialization
from my_utils.util import is_valid_filename, is_valid_url, get_query_class_from_string
import settings_manager

__js_api = None

VALID_QUERY_TYPES = ["http_simple", "http_content", "http_headers", "http_status_code", "http_regex", "rendered_content_regex"]


def send_event_to_js(window: webview.Window, event_type: str, data: dict):
    """
    Executes JavaScript code in the frontend to send an event to the Python backend.
    Can be listened to in the frontend by simply adding an event listener to the global "window" object.

    Example:

        window.addEventListener("my_event_type_name", (event) => {
            // No parsing needed, the event.detail is already a JS object
            console.log("Received payload: ", event.detail);
        });
    """
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

    def request_all_monitors_data(self):
        print("Received request for monitors data")
        # return mediator.get_monitors_manager().monitors
        return serialization.to_dict_encoded_with_types(mediator.get_monitors_manager().monitors)

    def request_monitor_data(self, unique_name: str) -> dict:
        print(f"Received request for monitor data: {unique_name}")
        targetMonitor = mediator.get_monitors_manager().get_monitor_by_name(unique_name)
        if targetMonitor is None:
            raise ValueError(f"No monitor found with name {unique_name}")
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

    def request_delete_monitor(self, unique_name: str):
        print(f"Received request to delete monitor: {unique_name}")
        monitors_manager = mediator.get_monitors_manager()
        targetMonitor = monitors_manager.get_monitor_by_name(unique_name)
        if targetMonitor is None:
            return f"Monitor with name {unique_name} not found"
        monitors_manager.remove_monitor(targetMonitor)
        targetMonitor.delete_history_file()
        monitors_manager.save_monitors_configs_to_file()
        return "true"

    def request_monitor_execution(self, unique_name: str):
        print(f"Received request to execute monitor: {unique_name}")
        targetMonitor = mediator.get_monitors_manager().get_monitor_by_name(unique_name)
        if targetMonitor is None:
            return f"Monitor with name {unique_name} not found"
        targetMonitor.execute()
        return "true"

    def request_log_entries(self, max_number_of_entries: int, min_level: str = "INFO", include_general: bool = True, include_monitoring: bool = True):
        """
        Reads from general and/or monitors logs and returns the last `max_number_of_entries` entries of at least `min_level`.
        """
        print(f"Received request for log entries")

        # Get log entries from the general log and all monitors logs
        log_entries = []
        if include_general:
            # Add log entries from the general log
            general_log_path = my_utils.util.resource_path("logs/general.log")
            log_entries += read_entries_from_log_file(general_log_path, max_number_of_entries, min_level)
        if include_monitoring:
            # Add log entries for all monitors in the manager
            for monitor in mediator.get_monitors_manager().monitors:
                log_entries += monitor.read_monitor_log_entries(max_number_of_entries, min_level)

        # Sort alphanumerically descending since they start with a timestamp
        log_entries.sort(reverse=True)

        # Return the first (i.e. most recent) max_number_of_entries
        return log_entries[:max_number_of_entries]

    def set_monitor_pause_state(self, unique_name: str, new_paused_value: bool) -> str:
        """
        Call to set the pause state of a monitor.
        :param unique_name: The unique name of the monitor
        :param is_paused: The new pause state
        :return: "true" if successful, or an error message if not
        """
        general_logger.debug(f'Received request to set monitor pause state: "{unique_name}" to {new_paused_value}')
        targetMonitor = mediator.get_monitors_manager().get_monitor_by_name(unique_name)
        if targetMonitor is None:
            return f"Monitor with name {unique_name} not found"
        targetMonitor.paused = new_paused_value
        targetMonitor.log_monitor_event("Monintor paused." if new_paused_value else "Monitor unpaused.")
        mediator.get_monitors_manager().save_monitors_configs_to_file()
        return "true"

    def submit_monitor_config(self, monitor_config: dict) -> str:
        """
        Call to apply a monitor configuration received from the frontend.
        Input is validated by the monitor itself then applied.
        The frontend is then responsible for reflecting the new backend state.

        :param monitor_config: The configuration object received from the frontend
        :return: "true" if successful, or an error message if not
        """
        general_logger.debug(f"Received monitor config submission: {monitor_config}")

        try:
            targetMonitor: Monitor = mediator.get_monitors_manager().get_monitor_by_name(monitor_config["original_name"])
            if targetMonitor is None:
                return f"Monitor with name {monitor_config['original_name']} not found"
            targetMonitor.validate_and_apply_config_from_frontend(monitor_config)
            general_logger.debug("Monitor config applied successfully.")
            general_logger.debug(f"Monitor after applying config: {targetMonitor}")
            # Save the new config to disk
            mediator.get_monitors_manager().save_monitors_configs_to_file()
        except Exception as e:
            general_logger.exception(f"Error while applying monitor config: {e}")
            return str(e)

        return "true"

    def create_new_empty_monitor(self) -> dict:
        """
        Create and returns a new empty monitor with a unique name.
        :return: The unique name of the newly created monitor
        """
        general_logger.debug("Received request to create a new empty monitor.")
        monitors_manager = mediator.get_monitors_manager()
        new_monitor = monitors_manager.create_and_add_empty_monitor()
        monitors_manager.save_monitors_configs_to_file()
        newMonitorData = self.request_monitor_data(new_monitor.unique_name)
        return newMonitorData

    def create_new_duplicate_monitor(self, original_name: str) -> dict:
        """
        Create and returns a new monitor that is a duplicate of the monitor with the given name.
        :param original_name: The name of the monitor to duplicate
        :return: The unique name of the newly created monitor
        """
        general_logger.debug(f"Received request to duplicate monitor: {original_name}")
        monitors_manager = mediator.get_monitors_manager()
        original_monitor = monitors_manager.get_monitor_by_name(original_name)
        if original_monitor is None:
            return f"Trying to duplicate monitor {original_name} but it does not exist."
        original_as_dict = serialization.to_encoded_json(original_monitor)
        new_monitor = serialization.from_encoded_json(original_as_dict)
        new_monitor.unique_name = monitors_manager.get_next_free_monitor_name()
        monitors_manager.add_monitor(new_monitor)
        monitors_manager.save_monitors_configs_to_file()
        newMonitorData = self.request_monitor_data(new_monitor.unique_name)
        return newMonitorData

    def request_app_settings(self) -> object:
        general_logger.debug("Received request for app settings.")
        return vars(settings_manager.settings)

    def submit_app_settings(self, new_settings: dict) -> str:
        """
        Call to apply a new app settings configuration received from the frontend.
        Input is validated by the settings manager itself then applied.
        :param new_settings: The configuration object received from the frontend
        :return: "true" if successful, or an error message if not
        """
        general_logger.debug(f"Received app settings submission: {new_settings}")

        try:
            settings_manager.apply_settings_dicitonary_from_frontend(new_settings)
            general_logger.debug("App settings applied successfully.")
        except Exception as e:
            general_logger.exception(f"Error while applying app settings: {e}")
            return str(e)

        return "true"

    def request_enter_new_smtp_password(self) -> str:
        """
        Request the user to enter a new password for the SMTP server.
        :return: "true" if successful, or an error message if not
        """
        general_logger.debug("Received request to enter a new SMTP password.")
        try:
            title = "Enter SMTP Password"
            message = (
                f"SMTP password change requested.\n\nPlease enter a new password, which will be stored through the OS credentials/keyring service."
            )
            credentials_manager.prompt_for_and_save_password(settings_manager.settings.smtp_username, title, message)
        except Exception as e:
            general_logger.exception(f"Error while entering new SMTP password: {e}")
            return str(e)
        return "true"

    def request_delete_smtp_password(self) -> str:
        """
        Request to delete the stored password for the SMTP server.
        :return: "true" if successful, or an error message if not
        """
        general_logger.debug("Received request to delete the SMTP password.")
        try:
            credentials_manager.delete_password_from_keyring(settings_manager.settings.smtp_username)
        except Exception as e:
            general_logger.exception(f"Error while deleting SMTP password: {e}")
            return str(e)
        return "true"

    def request_smtp_password_exists(self) -> bool:
        """
        Request to check if a password exists for the SMTP server.
        :return: True if a password exists, False otherwise
        """
        general_logger.debug("Received request to check if an SMTP password exists.")
        exists = credentials_manager.password_exists(settings_manager.settings.smtp_username)
        print(f"SMTP password exists: {exists}")
        return exists

    def request_complete_export(self) -> str:
        """
        Request to export the whole application configuration and logs to a zip file.
        :return: "true" if successful, or an error message if not
        """
        general_logger.debug("Received request to complete export.")
        try:
            my_utils.util.export_app_config_and_logs_to_zip()
        except Exception as e:
            general_logger.exception(f"Error while exporting app config and logs: {e}")
            return str(e)
        return "true"

    def request_complete_import(self) -> str:
        """
        Request to import the whole application configuration and logs from a zip file.
        :return: "true" if successful, or an error message if not
        """
        general_logger.debug("Received request to complete import.")
        try:
            # TODO - File picker, then safe import
            # my_utils.util.import_app_config_and_logs_from_zip()
            general_logger.error("Import not implemented yet.")
        except Exception as e:
            general_logger.exception(f"Error while importing app config and logs: {e}")
            return str(e)
        return "true"


def get_js_api():
    global __js_api
    if __js_api is None:
        __js_api = JsApi()
    return __js_api


def hook_frontend_to_backend_signals() -> None:
    """
    Hooks up signals from the backend to be forwarded to the frontend.
    """

    def send_new_results_event(monitor_name: str):
        current_gui = mediator.get_active_gui()
        if current_gui is None:
            # No active GUI to send events to
            return

        try:
            current_window = current_gui.window
        except AttributeError:
            general_logger.exception("hook_frontend_to_backend_signals: Could not get current window.")
            return

        if current_window:
            send_event_to_js(current_window, "new_monitor_results_in_backend", {"monitorUniqueName": monitor_name})

    mediator.new_monitor_results.add(send_new_results_event)
