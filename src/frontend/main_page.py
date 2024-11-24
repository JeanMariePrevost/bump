import os
import webview


class MainPage:
    def __init__(self) -> None:
        pass

    def show(self):
        # NOTE: pywebview uses the script's current working directory as the base directory for relative paths. E.g. /src/...
        _window = webview.create_window("BUMP - Dashboard", "frontend/content/main_page.html", text_select=True, width=1200, height=800)

        print(f"Current working directory: {os.getcwd()}")
        webview.start(self.webview_custom_logic_callback, debug=False)

    def webview_custom_logic_callback(self):
        # A separate thread handled by the webview?
        print("Webview custom logic callback")
        pass
