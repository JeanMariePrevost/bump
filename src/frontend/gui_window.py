import threading
import time
import webview

import mediator
import python_js_bridge
from custom_logging import get_general_logger
from my_utils import util

DEFAULT_WINDOW_WIDTH = 1280
DEFAULT_WINDOW_HEIGHT = 800


class GuiWindow:
    def __init__(self) -> None:
        self.window: webview.Window = None
        mediator.app_exit_requested.add(self.close)
        mediator.main_loop_exited.add(self.close)
        pass

    def show(self):
        if threading.current_thread() is threading.main_thread():
            get_general_logger().debug("GuiWindow.show called from the main thread. Proceeding.")
        else:
            get_general_logger().exception("GuiWindow.show: Calling from a non-main thread. This is not supported.")
            return
        if self.window is not None:
            get_general_logger().debug("GuiWindow.show: Window already open, not opening another one.")
            return

        # NOTE: pywebview uses the script's current working directory as the base directory for relative paths. E.g. /src/...
        self.window: webview.Window = webview.create_window(
            title="BUMP - Dashboard",
            url=mediator.get_http_server(),
            js_api=python_js_bridge.get_js_api(),
            text_select=True,
            width=DEFAULT_WINDOW_WIDTH,
            height=DEFAULT_WINDOW_HEIGHT,
        )

        self.window.events.closed += self.close
        mediator.register_active_gui(self)

        webview.start(icon=util.resource_path("assets/icon_32px.png"), debug=True)

    def close(self):
        if mediator.get_active_gui() == self.window:
            mediator.register_active_gui(None)
        if self.window is not None:
            self.window.events.closed -= self.close
            self.window.destroy()
        self.window = None
        print("GuiWindow.close: Window closed.")

    def is_open(self) -> bool:
        return self.window is not None
