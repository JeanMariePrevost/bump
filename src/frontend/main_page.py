import threading
import time
import webview

import global_events
import python_js_bridge
from custom_logging import general_logger


class MainPage:
    def __init__(self) -> None:
        self._window: webview.Window = None
        global_events.app_exit_requested.add(self.close)
        global_events.main_loop_exited.add(self.close)
        pass

    def show(self):
        if threading.current_thread() is threading.main_thread():
            print("Running on the main thread. A-OK.")
        else:
            general_logger.exception("MainPage.show: Calling from a non-main thread. This is not supported.")
            return
        general_logger.debug("MainPage.show called.")
        if self._window is not None:
            general_logger.debug("MainPage.show: Window already open, not opening another one.")
            return

        # NOTE: pywebview uses the script's current working directory as the base directory for relative paths. E.g. /src/...
        self._window: webview.Window = webview.create_window(
            "BUMP - Dashboard",
            "frontend/content/main_page.html",
            js_api=python_js_bridge.get_js_api(),
            text_select=True,
            width=1200,
            height=800,
        )

        self._window.events.closed += self.close
        global_events.gui_winow_opened = True

        webview.start(self.webview_custom_logic_callback, debug=True)

    def close(self):
        if self._window is not None:
            self._window.events.closed -= self.close
            self._window.destroy()
        self._window = None
        global_events.gui_winow_opened = False
        print("MainPage.close: Window closed.")

    def webview_custom_logic_callback(self):
        # A separate thread handled by the webview?
        print("Webview custom logic callback")
        time.sleep(2)
        # Dispatch dummy event to test communication
        python_js_bridge.send_event_to_js(self._window, "py_js_test_event", {"data": "Hello from the backend!"})
        pass
