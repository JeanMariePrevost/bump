from dataclasses import dataclass
import difflib
from ruamel.yaml import YAML, CommentedMap
from my_utils import util
from custom_logging import general_logger


# Defaults values and the "struct" settings object
# NOTE: Password is entered during setup and stored using keyring (https://pypi.org/project/keyring/)
@dataclass
class Settings:
    general_interval: int = 60
    general_log_level: str = "INFO"
    general_theme: str = "dark"
    alerts_use_toast: bool = True
    alerts_use_email: bool = False
    alerts_use_sms: bool = False
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_target_email: str = ""
    smtp_target_email_for_sms: str = ""


settings = Settings()


def load_configs():
    """
    Set module-level variables from the app_config.yaml file.
    """

    general_logger.debug("Loading app settings from app_config.yaml")

    yaml = YAML()

    try:
        with open(util.resource_path("config/app_config.yaml"), "r") as file:
            loadedConfigsDict = yaml.load(file)
    except FileNotFoundError:
        general_logger.error("app_config.yaml not found. Settings could not be loaded.")
        return
    except Exception as e:
        general_logger.error(f"Error loading app_config.yaml: {e}")
        return

    apply_Settings_dictionary(loadedConfigsDict)

    general_logger.debug("App settings loaded successfully.")


def save_configs():
    """
    Save the current settings to the app_config.yaml file.
    Includes hard-coded comments into the output file.
    """

    # NOTE: THe order of operations AND the order of the properties in the object matter to keep the layout of the yaml file
    # (The *data* is unaffected however, it will only result in a messy yaml file with misplaced comments)

    general_logger.debug("Saving app settings to app_config.yaml")

    yaml = YAML()
    yaml_data = CommentedMap()  # Allows us to add comments to the output file

    # Populate the yaml_data with the current settings
    for key, value in vars(settings).items():
        yaml_data[key] = value

    # Add top-level comments
    yaml_data.yaml_set_start_comment("Configuration settings for the application\nAdjust the alert settings and SMTP server details as needed")

    # Add empty lines between sections
    yaml_data.yaml_set_comment_before_after_key("general_interval", before="\n")
    yaml_data.yaml_set_comment_before_after_key("general_log_level", before="\n")
    yaml_data.yaml_set_comment_before_after_key("general_theme", before="\n")
    yaml_data.yaml_set_comment_before_after_key("alerts_use_toast", before="\n")
    yaml_data.yaml_set_comment_before_after_key("smtp_server", before="\n")

    # Add "internal" comments
    yaml_data.yaml_set_comment_before_after_key("general_interval", before='Integer in seconds that defines the monitoring "ticking rate"')
    yaml_data.yaml_set_comment_before_after_key("general_log_level", before='One of "DEBUG", "INFO", "WARNING", "ERROR"')
    yaml_data.yaml_set_comment_before_after_key("general_theme", before='"light" or "dark"')
    yaml_data.yaml_set_comment_before_after_key("alerts_use_toast", before="Enable/disable alerts per type")
    yaml_data.yaml_set_comment_before_after_key(
        "smtp_server",
        before="SMTP server details, used for sending email and Email-to-SMS alerts\nNote: The password is entered during setup and stored in the OS credentials manager using keyring (https://pypi.org/project/keyring/)",
    )

    # Save the yaml_data to the file
    try:
        with open(util.resource_path("config/app_config.yaml"), "w") as file:
            yaml.dump(yaml_data, file)
    except Exception as e:
        general_logger.error(f"Error saving app_config.yaml: {e}")
        return

    general_logger.debug("App settings saved successfully.")


def __warn_of_incorrect_key(key: str):
    # Get a list of close matches from known settings
    suggestions = difflib.get_close_matches(key, vars(settings).keys(), n=1, cutoff=0.1)
    if suggestions:
        suggestion = suggestions[0]
        general_logger.warning(f"app_config.yaml: {key} is not a known setting. Did you mean '{suggestion}'?")
    else:
        general_logger.warning(f"app_config.yaml: {key} is not a known setting.")


def apply_Settings_dictionary(dictionary: dict):
    """
    Safely apply the settings from a dictionary to the settings object.
    """
    for key, value in dictionary.items():
        if hasattr(settings, key):  # If it's a known setting
            if isinstance(value, type(getattr(settings, key))):  # If it's the right type
                setattr(settings, key, value)  # Set the value
            else:
                # Actual setting, but wrong type, don't load
                general_logger.warning(
                    f"Dictionary: {key} is not the correct type. Expected {type(getattr(settings, key))}, got {value}:{type(value)}"
                )
        else:
            # Not a known setting, don't load
            __warn_of_incorrect_key(key)

    # TODO: Refresh the application's settings based on the new settings, e.g. custom_loggin.set_log_level(settings.general_log_level), main loop interval...
    # NOTE: Currently, the settings are only applied when the application is started, not during runtime.


def apply_settings_dicitonary_from_frontend(configData: dict):
    """
    Prepares and validates input before passing it to apply_Settings_dictionary()
    """
    print(configData)
    # general_interval casts to a positive integer
    try:
        configData["general_interval"] = int(configData["general_interval"])
    except ValueError:
        general_logger.warning("general_interval must be a positive integer.")
        return

    # general_log_level must be one of the following: "DEBUG", "INFO", "WARNING", "ERROR"
    if configData["general_log_level"] not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        general_logger.warning("general_log_level must be one of the following: 'DEBUG', 'INFO', 'WARNING', 'ERROR'")
        return

    # general_theme must be one of the following: "light", "dark"
    if configData["general_theme"] not in ["light", "dark"]:
        general_logger.warning("general_theme must be one of the following: 'light', 'dark'")
        return

    # alerts_use_toast, alerts_use_email, alerts_use_sms must be string that represents a boolean, and be converted to a boolean
    for key in ["alerts_use_toast", "alerts_use_email", "alerts_use_sms"]:
        if configData[key].lower() not in ["true", "false"]:
            general_logger.warning(f"{key} must be a string that represents a boolean.")
            return
        configData[key] = configData[key].lower == "true"

    # smtp_port casts to a positive integer
    try:
        configData["smtp_port"] = int(configData["smtp_port"])
    except ValueError:
        general_logger.warning("smtp_port must be a positive integer.")
        return

    # smtp_server, smtp_username, smtp_target_email, smtp_target_email_for_sms must be strings
    for key in ["smtp_server", "smtp_username", "smtp_target_email", "smtp_target_email_for_sms"]:
        if not isinstance(configData[key], str):
            general_logger.warning(f"{key} must be a string.")
            return

    # Everything seems valid, apply the settings
    apply_Settings_dictionary(configData)


# Testing
if __name__ == "__main__":
    load_configs()
    print(settings)
    print(settings.alerts_use_toast)
