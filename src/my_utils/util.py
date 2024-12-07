import os
import sys
import pathvalidate
from importlib import import_module
from urllib.parse import urlparse
from custom_logging import general_logger


def resource_path(relative_path):
    """
    Resolves absolute path to resource, required for PyInstaller compatibility.
    :param relative_path: The relative path to the resource, from the root directory
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


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_query_class_from_string(fully_qualified_query_class_name: str) -> type | None:
    """
    Returns the class object for a query class based on the class name, or None if the class does not exist or isn't a query.
    :param fully_qualified_query_class_name: The fully qualified class name for the query class
    :return: The class object for the query class or None if it doesn't exist or isn't a query
    """
    # Confirm package
    if not fully_qualified_query_class_name.startswith("queries."):
        general_logger.error(f"Query class name {fully_qualified_query_class_name} not in queries package")
        return None

    # Try to resolve the class object
    try:
        # Split the class name into module and class name
        module_name, class_name = fully_qualified_query_class_name.rsplit(".", 1)

        # Import the module
        module = import_module(module_name)

        # Get the class object
        return getattr(module, class_name, None)
    except ImportError as e:
        general_logger.error(f"Error importing module {module_name}: {e}")
    except AttributeError:
        general_logger.error(f"Class {class_name} not found in module {module_name}")

    return None
