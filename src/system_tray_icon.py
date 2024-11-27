"""
THis module uses pystray to create a system tray icon and allow the program to keep running in the background
"""

import PIL.Image
import pystray

from custom_logging import general_logger
import global_events
from my_utils.simple_queue import QueueEvents
from my_utils import util


class SystemTrayIcon:

    def __init__(self) -> None:
        general_logger.debug("system_tray.initialize_system_tray: Initializing system tray...")
        # Load the image for the icon
        image = PIL.Image.open(util.resource_path("assets/icon_32px.png"))

        # Set up pystray
        global __pystray_icon_object
        __pystray_icon_object = pystray.Icon(
            "Bump - Web Monitoring Tool",
            image,
            menu=pystray.Menu(
                pystray.MenuItem(
                    "default", self.on_clicked_open_gui, default=True, visible=False
                ),  # default=True means that this is also the action that gets called when LMB the icon
                pystray.MenuItem("Open", self.on_clicked_open_gui),
                pystray.MenuItem("Exit", self.on_clicked_exit),
            ),
        )

        global_events.main_loop_exited.add(self.stop)

        # Run pystray
        __pystray_icon_object.run_detached()

    # Define actions for the RMB menu of the tray icon
    def on_clicked_exit(self, icon, item):
        general_logger.debug(f'system_tray.on_clicked_exit: Clicked "{item}"')
        # global_events.main_thread_event_queue.put("exit")
        global_events.app_exit_requested.trigger()
        global_events.bg_monitoring_queue.put_nowait(QueueEvents.EXIT_APP)
        global_events.main_thread_blocking_queue.put(QueueEvents.EXIT_APP, 1)

    def stop(self):
        general_logger.debug("system_tray.stop: Stopping system tray...")
        # HACK : hide, because "zombie" icons linger in the tray after the program exits otehrwise. Not live threads, just the icon for some reason
        __pystray_icon_object.visible = False
        __pystray_icon_object.stop()

    # Define actions for the RMB menu of the tray icon
    def on_clicked_open_gui(self, icon, item):
        general_logger.debug(f'system_tray.on_clicked_open_gui: Clicked "{item}"')
        # global_events.main_thread_event_queue.put("show_gui")
        if not global_events.gui_winow_opened:
            global_events.main_thread_blocking_queue.put(QueueEvents.OPEN_GUI, 1)
        else:
            general_logger.debug("system_tray.on_clicked_open_gui: Main window already open.")
            pass
