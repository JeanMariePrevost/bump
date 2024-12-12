import ctypes
import sys
import threading
from bottle import Bottle, static_file
from common.custom_logging import get_general_logger
import common.mediator as mediator


class BottleServer:
    def __init__(self):
        get_general_logger().info("bottle_server.py: Setting up Bottle server routes.")

        self.server: Bottle = Bottle()
        self.thread = None

        def adjust_path(target_path) -> str:
            """Returns the adjusted path whether the application is executed in a PyInstaller bundle or not."""
            if hasattr(sys, "_MEIPASS"):
                # In bundled app, the "src" dir is located inside the PyInstaller's "_internal" dir, so prefix it
                return "_internal/" + target_path
            else:
                # Running in normal Python environment, no changes
                return target_path

        @self.server.route("/assets/<path:path>")
        def serve_asset(path):
            """Serves static files from the assets folder."""
            get_general_logger().debug(f"bottle_server.py: Serving asset: {path}")
            return static_file(path, root=adjust_path("assets"))

        @self.server.route("/<path:path>")
        def serve_content(path):
            """Serves static files from the frontend content folder, where the html, css, js files are."""
            get_general_logger().debug(f"bottle_server.py: Serving content: {path}")
            if "." not in path:
                # Default to serving html files if no extension is provided
                path += ".html"
            return static_file(path, root=adjust_path("src/frontend/content"))

        @self.server.route("/")
        def serve_default():
            """Required by pywebview to define an entry point when passing a server instead of a url to create_window."""
            get_general_logger().debug(f"bottle_server.py: Serving default page.")
            return static_file("main_page.html", root=adjust_path("src/frontend/content/"))

        @self.server.route("/metadata.json")
        def serve_metadata():
            """Special case to serve the metadata.json file for the frontend."""
            get_general_logger().debug(f"bottle_server.py: Serving metadata.json.")
            return static_file("metadata.json", root=adjust_path(""))

        get_general_logger().info("bottle_server.py: Bottle server routes set up.")

    def __run(self):
        self.server.run(host="localhost", port=8081, debug=True)

    def start_as_background_thread(self):
        get_general_logger().info("bottle_server.py: Starting Bottle server as a background thread.")

        self.thread = threading.Thread(target=self.__run)
        self.thread.start()
        mediator.register_http_server(self.server)

        mediator.app_exit_requested.add(self.stop)

        return self.thread

    def stop(self):
        # Taken straight from https://stackoverflow.com/questions/43399652/cant-quit-python-script-with-ctrl-c-if-a-thread-ran-webbrowser-open
        stop = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.thread.ident), ctypes.py_object(KeyboardInterrupt))
        self.thread.join()

        self.server.close()
        get_general_logger().info("bottle_server.py: Bottle server stopped.")
