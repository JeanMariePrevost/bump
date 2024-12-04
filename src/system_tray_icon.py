"""
THis module uses pystray to create a system tray icon and allow the program to keep running in the background
"""

import PIL.Image
import pystray

from custom_logging import general_logger
import mediator
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

        mediator.all_monitors_now_up.add(self.changeIconToNormal)
        mediator.some_monitors_down.add(self.changeIconToDown)
        mediator.some_monitors_have_exceptions.add(self.changeIconToWarning)

        mediator.main_loop_exited.add(self.stop)

        # Run pystray
        __pystray_icon_object.run_detached()

    def changeIconToWarning(self):
        image = PIL.Image.open(util.resource_path("assets/icon_warning_32px.png"))
        __pystray_icon_object.icon = image

    def changeIconToNormal(self):
        image = PIL.Image.open(util.resource_path("assets/icon_32px.png"))
        __pystray_icon_object.icon = image

    def changeIconToDown(self):
        image = PIL.Image.open(util.resource_path("assets/icon_down_32px.png"))
        __pystray_icon_object.icon = image

    # Define actions for the RMB menu of the tray icon
    def on_clicked_exit(self, icon, item):
        general_logger.debug(f'system_tray.on_clicked_exit: Clicked "{item}"')
        # global_events.main_thread_event_queue.put("exit")
        mediator.app_exit_requested.trigger()
        mediator.bg_monitoring_queue.put_nowait(QueueEvents.EXIT_APP)
        mediator.main_thread_blocking_queue.put(QueueEvents.EXIT_APP, 1)

    def stop(self):
        general_logger.debug("system_tray.stop: Stopping system tray...")
        # HACK : hide, because "zombie" icons linger in the tray after the program exits otehrwise. Not live threads, just the icon for some reason
        __pystray_icon_object.visible = False
        __pystray_icon_object.stop()

    # Define actions for the RMB menu of the tray icon
    def on_clicked_open_gui(self, icon, item):
        general_logger.debug(f'system_tray.on_clicked_open_gui: Clicked "{item}"')
        # global_events.main_thread_event_queue.put("show_gui")
        if not mediator.get_active_gui().is_open():
            mediator.main_thread_blocking_queue.put(QueueEvents.OPEN_GUI, 1)
        else:
            general_logger.debug("system_tray.on_clicked_open_gui: Main window already open.")
            pass
