import difflib
import yaml
from my_utils import util
from custom_logging import general_logger
from types import SimpleNamespace

# Defaults, accessed like a regular object, e.g. settings.alerts_use_toast (this isn't a dict)
settings = SimpleNamespace(
    alerts_use_toast=True,
    alerts_use_email=False,
    alerts_use_sms=False,
)


def load_configs():
    """
    Set module-level variables from the app_config.yaml file.
    """

    # Read from /email_config.yaml
    with open(util.resource_path("config/app_config.yaml"), "r") as file:
        config = yaml.safe_load(file)

        global settings

        for key, value in config.items():
            # Check if the key exists in settings
            if hasattr(settings, key):
                if isinstance(value, type(getattr(settings, key))):
                    setattr(settings, key, value)
                else:
                    general_logger.warning(
                        f"app_config.yaml: {key} is not the correct type. Expected {type(getattr(settings, key))}, got {value}:{type(value)}"
                    )
            else:
                __wanr_of_incorrect_key(key)

        # Debug logging that lists ALL module-level variables
        general_logger.debug("App settings loaded:")
        for key, value in vars(settings).items():
            general_logger.debug(f"{key}: {value}")


def __wanr_of_incorrect_key(key: str):
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
