import time
import webview

import global_events
import python_js_bridge


class MainPage:
    def __init__(self) -> None:
        self._window = None
        global_events.open_gui_requested.add(self.show)
        global_events.app_exit_requested.add(self.close)
        pass

    def show(self):
        # NOTE: pywebview uses the script's current working directory as the base directory for relative paths. E.g. /src/...
        self._window: webview.Window = webview.create_window(
            "BUMP - Dashboard",
            "frontend/content/main_page.html",
            js_api=python_js_bridge.get_js_api(),
            text_select=True,
            width=1200,
            height=800,
        )

        global_events.app_exit_requested.add(self._window.destroy)

        webview.start(self.webview_custom_logic_callback, debug=True)

    def close(self):
        if self._window is not None:
            self._window.destroy()
            self._window = None

    def webview_custom_logic_callback(self):
        # A separate thread handled by the webview?
        print("Webview custom logic callback")
        time.sleep(2)
        # Dispatch dummy event to test communication
        python_js_bridge.send_event_to_js(self._window, "py_js_test_event", {"data": "Hello from the backend!"})
        pass
