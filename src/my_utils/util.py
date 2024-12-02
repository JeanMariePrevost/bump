import os
import sys
import pathvalidate


def resource_path(relative_path):
    """
    Resolves absolute path to resource, required for PyInstaller compatibility.
    :param relative_path: The relative path to the resource
    :return: The absolute path to the resource
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def is_valid_filename(filename: str) -> bool:
    """
    Checks if the given string is a valid filename based on Windows filesystem rules.
    :param filename: The string to check
    :return: True if the string is a valid filename, False otherwise
    """
    try:
        pathvalidate.validate_filename(filename)
    except pathvalidate.ValidationError:
        return False
    return True
