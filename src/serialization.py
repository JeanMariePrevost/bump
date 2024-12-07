from datetime import datetime
import json
import os


class SerializationError(Exception):
    pass


class Deserializable:
    """Base class for class instances that can be deserialized from a dictionary."""

    @classmethod
    def from_dict(cls, dict_object: dict):
        # TODO : IS THIS DEPRECATED IN FAVOR OF from_encoded_json()?
        # Dynamically create an instance of the calling class
        instance = cls()
        for key, value in dict_object.items():
            # Only set attributes that exist in the class
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance


def to_dict_encoded_with_types(obj, include_internal=True, include_private=False) -> dict:
    """
    Function to encode an non-simple object to a dictionary of its attributes AND its type.
    Allows deserialization to the original object type.
    Args:
        obj: The object to encode.
        include_internal (bool): Whether to include internal attributes ("_xyz").
        include_private (bool): Whether to include private attributes ("__xyz").
    Returns:
        dict: A dictionary representation of the object, including its type information.
    Raises:
        SerializationError: If the object's class does not have a 'from_dict' static method implemented.
    """
    if hasattr(obj, "__dict__"):
        # Handle objects with a __dict__ attribute recursively (they are class instances/complex objects)

        # Check if the class has a 'from_dict' static method implemented so that it can be deserialized
        if not hasattr(obj.__class__, "from_dict"):
            raise SerializationError(f"Class {obj.__class__.__name__} does not have a 'from_dict' static method implemented.")

        # Apply the internal/private inclusion/exclusion parameters
        class_name_prefix = f"_{obj.__class__.__name__}__"  # Prefix for mangled private attributes

        attributes = {
            key: value
            for key, value in obj.__dict__.items()
            # Filtering out name-mangled private attributes
            if (include_private or not key.startswith(class_name_prefix))
            # Filtering out internal attributes
            and (include_internal or not key.startswith("_") or key.startswith(class_name_prefix))
        }

        # Recursively encode the attributes
        encoded_attributes = {}
        for key, value in attributes.items():
            # DEBUG:
            print(f"Encoding {key} of type {type(value)}")

            encoded_attributes[key] = to_dict_encoded_with_types(value, include_internal, include_private)

        return {
            "type": f"{obj.__class__.__module__}.{obj.__class__.__name__}",
            "value": encoded_attributes,
        }
    elif isinstance(obj, list):
        return [
            to_dict_encoded_with_types(item, include_internal, include_private) for item in obj
        ]  # Recursively handle lists to identify non-simple objects
    elif isinstance(obj, dict):
        return {
            key: to_dict_encoded_with_types(value, include_internal, include_private) for key, value in obj.items()
        }  # Recursively handle dicts to identify non-simple objects
    else:
        # "value" types with custom encoding, then a default behavior
        if isinstance(obj, datetime):
            return {"type": "datetime.datetime", "value": obj.isoformat()}
        else:
            return obj  # Return primitives directly


def to_encoded_json(obj):
    """
    Encodes an object to JSON, but includes the type of the non-simple objects for them to be properly deserialized.
    """
    return json.dumps(to_dict_encoded_with_types(obj), indent=4)


def to_encoded_jsonl(obj):
    """
    Like to_encoded_json, but as a single line
    """
    return json.dumps(to_dict_encoded_with_types(obj))


def from_encoded_json(json_string) -> object:
    """
    Deserializes an object from a JSON string that was encoded with the encode_with_type function.
    """

    def decode_with_type(obj):
        if isinstance(obj, dict) and "type" in obj and "value" in obj:
            if obj["type"] == "datetime.datetime":
                return datetime.fromisoformat(obj["value"])
            else:
                class_name = obj["type"].split(".")[-1]
                class_module = ".".join(obj["type"].split(".")[:-1])
                class_ = getattr(__import__(class_module, fromlist=[class_name]), class_name)
                return class_.from_dict({key: decode_with_type(value) for key, value in obj["value"].items()})

        elif isinstance(obj, list):
            return [decode_with_type(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: decode_with_type(value) for key, value in obj.items()}
        else:
            return obj

    return decode_with_type(json.loads(json_string))


def save_as_json_file(obj, file_path) -> None:
    """
    Saves an object to a JSON file, but includes the type of the non-simple objects for them to beproperly deserialized.
    """
    # Create path and file if they don't exist
    file_path = os.path.abspath(file_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w") as file:
        file.write(to_encoded_json(obj))


def load_from_json_file(file_path) -> object:
    """
    Loads an object from a JSON file that was encoded with the encode_with_type function.
    """
    with open(file_path, "r") as file:
        return from_encoded_json(file.read())
