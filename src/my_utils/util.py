from datetime import datetime
import os
import sys
import zipfile
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


def export_app_config_and_logs_to_zip():
    """
    Exports the whole ./config/, ./data/ and ./logs/ directories to a zip file.
    """

    # Define the folders to export
    folders = [
        resource_path("config"),
        resource_path("data"),
        resource_path("logs"),
    ]

    # Ensure source paths already exist
    for folder in folders:
        if not os.path.exists(folder):
            general_logger.error(f"Export failed: {folder} does not exist")
            return

    # Ensure target path exists
    os.makedirs("exports", exist_ok=True)

    # Create the zip file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = timestamp + "_BUMP_EXPORT.zip"
    subdirectory = "exports"
    output_path = resource_path(subdirectory + "/" + filename)
    general_logger.debug(f"Exporting app data and logs to {output_path}")
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for folder in folders:
            for root, _, files in os.walk(folder):
                for file in files:
                    # Get the full file path
                    full_path = os.path.join(root, file)
                    # Add file to the zip, preserving folder structure
                    arcname = os.path.relpath(full_path, os.path.dirname(folder))
                    zipf.write(full_path, arcname)

    general_logger.debug("Export complete")

    # Reveal the file in the file explorer
    full_directory = resource_path(subdirectory)
    print(f"Exported to {full_directory}")
    os.startfile(full_directory)
