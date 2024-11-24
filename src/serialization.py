# def to_dict_tree(object) -> dict:
#     if isinstance(object, dict):
#         return {key: to_dict_tree(value) for key, value in object.items()}
#     elif isinstance(object, list):
#         return [to_dict_tree(element) for element in object]
#     elif hasattr(object, "__dict__"):
#         return to_dict_tree(object.__dict__)
#     else:
#         return object


# def to_dict(object) -> dict:
#     return object.__dict__


from datetime import datetime
import json


class SerializationError(Exception):
    pass


class Deserializable:
    """Base class for class instances that can be deserialized from a dictionary."""

    @classmethod
    def from_dict(cls, dict_object: dict):
        # Dynamically create an instance of the calling class
        instance = cls()
        for key, value in dict_object.items():
            # Only set attributes that exist in the class
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance


def encode_with_type(obj):
    """
    Function to encode an non-simple object to as a dictionary of its attributes AND its type.
    """
    if hasattr(obj, "__dict__"):
        # If it has a __dict__ attribute, it's a class instance

        # If its class doesn't have a "from_dict" static method, raise an exception as it won't be able to be deserialized
        if not hasattr(obj.__class__, "from_dict"):
            raise SerializationError(f"Class {obj.__class__.__name__} does not have a 'from_dict' static method implemented.")

        return {
            "type": f"{obj.__class__.__module__}.{obj.__class__.__name__}",
            "value": {key: encode_with_type(value) for key, value in obj.__dict__.items()},  # Recursively encode attributes of the object
        }
    elif isinstance(obj, list):
        return [encode_with_type(item) for item in obj]  # Recursively handle lists to identify non-simple objects
    elif isinstance(obj, dict):
        return {key: encode_with_type(value) for key, value in obj.items()}  # Recursively handle dicts to identify non-simple objects
    else:
        # "value" types with custom encoding, then a default behavior
        if isinstance(obj, datetime):
            return {"type": "datetime.datetime", "value": obj.isoformat()}
        else:
            return obj  # Return primitives directly


def to_encoded_json(obj):
    """
    Encodes an object to JSON, but includes the type of the non-simple objects for them to beproperly deserialized.
    """
    return json.dumps(encode_with_type(obj), indent=4)


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
    with open(file_path, "w") as file:
        file.write(to_encoded_json(obj))


def load_from_json_file(file_path) -> object:
    """
    Loads an object from a JSON file that was encoded with the encode_with_type function.
    """
    with open(file_path, "r") as file:
        return from_encoded_json(file.read())
