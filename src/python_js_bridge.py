import json
import webview


class PythonJSBridge:
    def __init__(self, window):
        self.window = window

    def send_event(self, event_type, data):
        payload = {"data": data}  # Wrap the data in a dictionary
        js_code = f"window.dispatchEvent(new CustomEvent('{event_type}', {{ detail: {json.dumps(payload)} }}));"
        self.window.evaluate_js(js_code)
        print(f"Sent event: {event_type} with data: {data}")
