import difflib
from ruamel.yaml import YAML, CommentedMap
from my_utils import util
from custom_logging import general_logger
from types import SimpleNamespace

# Defaults values
# NOTE: accessed like a regular object, e.g. settings.alerts_use_toast (i.e. this isn't a dict)
# NOTE: Password is entered during setup and stored using keyring (https://pypi.org/project/keyring/)
settings = SimpleNamespace(
    alerts_use_toast=True,
    alerts_use_email=False,
    alerts_use_sms=False,
    smtp_server="",
    smtp_port=587,
    smtp_username="",
    smtp_target_email="",
    smtp_target_email_for_sms="",
)


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

    for key, value in loadedConfigsDict.items():
        if hasattr(settings, key):  # If it's a known setting
            if isinstance(value, type(getattr(settings, key))):  # If it's the right type
                setattr(settings, key, value)  # Set the value
            else:
                # Actual setting, but wrong type, don't load
                general_logger.warning(
                    f"app_config.yaml: {key} is not the correct type. Expected {type(getattr(settings, key))}, got {value}:{type(value)}"
                )
        else:
            # Not a known setting, don't load
            __warn_of_incorrect_key(key)

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
    yaml_data.yaml_set_comment_before_after_key("alerts_use_toast", before="\n")
    yaml_data.yaml_set_comment_before_after_key("smtp_server", before="\n")

    # Add "internal" comments
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


# Testing
if __name__ == "__main__":
    load_configs()
    print(settings)
    print(settings.alerts_use_toast)
