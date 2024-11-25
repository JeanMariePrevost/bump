import os
import sys


def resource_path(relative_path):
    """
    Resolves absolute path to resource, required for PyInstaller compatibility.
    :param relative_path: The relative path to the resource
    :return: The absolute path to the resource
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
