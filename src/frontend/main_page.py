import os
import time
import webview

from python_js_bridge import PythonJSBridge


class MainPage:
    def __init__(self) -> None:
        self._window = None
        pass

    def show(self):
        # NOTE: pywebview uses the script's current working directory as the base directory for relative paths. E.g. /src/...
        self._window = webview.create_window("BUMP - Dashboard", "frontend/content/main_page.html", text_select=True, width=1200, height=800)

        print(f"Current working directory: {os.getcwd()}")
        webview.start(self.webview_custom_logic_callback, debug=True)

    def webview_custom_logic_callback(self):
        # A separate thread handled by the webview?
        print("Webview custom logic callback")
        time.sleep(2)
        # Dispatch dummy event to test communication
        bridge = PythonJSBridge(self._window)
        bridge.send_event("test_event", "Hello from the backend!")
        pass
