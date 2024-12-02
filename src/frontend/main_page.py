import threading
import time
import webview

import mediator
import python_js_bridge
from custom_logging import general_logger

DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800


class MainPage:
    def __init__(self) -> None:
        self._window: webview.Window = None
        mediator.app_exit_requested.add(self.close)
        mediator.main_loop_exited.add(self.close)
        pass

    def show(self):
        if threading.current_thread() is threading.main_thread():
            general_logger.debug("MainPage.show called from the main thread. Proceeding.")
        else:
            general_logger.exception("MainPage.show: Calling from a non-main thread. This is not supported.")
            return
        if self._window is not None:
            general_logger.debug("MainPage.show: Window already open, not opening another one.")
            return

        # NOTE: pywebview uses the script's current working directory as the base directory for relative paths. E.g. /src/...
        # self._window: webview.Window = webview.create_window(
        #     "BUMP - Dashboard",
        #     "frontend/content/main_page.html",
        #     js_api=python_js_bridge.get_js_api(),
        #     text_select=True,
        #     width=1200,
        #     height=800,
        # )

        self._window: webview.Window = webview.create_window(
            title="BUMP - Dashboard",
            url=mediator.get_http_server(),
            js_api=python_js_bridge.get_js_api(),
            text_select=True,
            width=1200,
            height=800,
        )

        self._window.events.closed += self.close
        mediator.register_active_gui(self)

        webview.start(self.webview_custom_logic_callback, debug=True)

    def close(self):
        if mediator.get_active_gui() == self._window:
            mediator.register_active_gui(None)
        if self._window is not None:
            self._window.events.closed -= self.close
            self._window.destroy()
        self._window = None
        print("MainPage.close: Window closed.")

    def is_open(self) -> bool:
        return self._window is not None

    def webview_custom_logic_callback(self):
        # A separate thread handled by the webview?
        print("Webview custom logic callback")
        time.sleep(2)
        # Dispatch dummy event to test communication
        python_js_bridge.send_event_to_js(self._window, "py_js_test_event", {"data": "Hello from the backend!"})
        pass
