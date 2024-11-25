import json
import webview

from custom_logging import general_logger

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

    # def __init__(self, bridge):
    #     self.bridge = bridge
    #     self.window = bridge.window

    def send_event_to_python(self, event_type, data):
        print(f"Received event: {event_type} with data: {data}")
        pass


def get_js_api():
    global __js_api
    if __js_api is None:
        __js_api = JsApi()
    return __js_api
