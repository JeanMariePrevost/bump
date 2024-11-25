from inspect import signature
from typing import Callable, List, Tuple, Type, Union

from custom_logging import general_logger


class Signal:
    """
    Generic type-safe Signal class with dynamically checked payload types and callback signatures.
    You can use "object" type as a wildcard for any type.

    Example usage:
    ```
    test_signal = Signal(object, str)
    test_signal.add(some_callback_int_str)
    test_signal.add(some_callback_str_str)
    test_signal.send(42, "hello")
    ```
    """

    # TODO: Add support for weak references? Either we need explicit "desctruction" of objects, or we need to use weakrefs
    # TODO: Make thread-safe? (threading.Lock)
    # TODO: Add support for async callbacks? For awaits?

    @staticmethod
    def create_wildcard_signal() -> "Signal":
        """
        Create a Signal that accepts any payload types.
        """
        pass

    def __init__(self, *arg_types: Type):
        """
        Initialize the Signal with the expected argument types.
        :param arg_types: A tuple of types that the signal will enforce for payloads.
        """
        self.observers: List[Tuple[int, Callable]] = []
        self.arg_types = arg_types  # Tuple of expected argument types

    def add(self, target_function: Callable, priority: int = 0) -> None:
        """
        Add a function to the list of observers.
        :param target_function: The callback to invoke when the signal is sent.
        :param priority: Priority for callback execution order (higher first).
        """
        self._validate_function_to_be_added(target_function)

        self.observers.append((priority, target_function))
        self.observers.sort(key=lambda x: x[0], reverse=True)

    def add_once(self, target_function: Callable, priority: int = 0) -> None:
        """
        Add a function to the list of observers, but remove it after the first call.
        """

        self._validate_function_to_be_added(target_function)

        def one_time_wrapper(*args, **kwargs):
            target_function(*args, **kwargs)
            self.remove(one_time_wrapper)

        self.add(one_time_wrapper, priority)

    def function_in_list(self, target_function: Callable) -> bool:
        """
        Check if a function is already in the observer list.
        """
        return any(func == target_function for _, func in self.observers)

    def remove(self, target_function: Callable) -> None:
        """
        Remove a specific callback from the observer list.
        """
        self.observers = [(priority, func) for priority, func in self.observers if func != target_function]

    def remove_all(self) -> None:
        """
        Clear all observers.
        """
        self.observers.clear()

    def trigger(self, *args, **kwargs) -> None:
        """
        Trigger the signal, passing the payload to all observers.
        """
        if not self._payload_is_valid_type(args):
            raise TypeError(f"Invalid payload {args}. Expected types: {self.arg_types}")

        for _, target_function in self.observers:
            target_function(*args, **kwargs)

    def _validate_function_to_be_added(self, target_function: Callable):
        """
        Check if a function is valid to be added to the observer list.
        """
        if not callable(target_function):
            raise ValueError("target_function must be a callable function")

        if not self._function_has_valid_signature(target_function):
            raise TypeError(f"Callback {target_function} does not match signal signature {self.arg_types}")

        if self.function_in_list(target_function):
            general_logger.debug(f"Trying to add {target_function} which is already in the signal's list")

    def _payload_is_valid_type(self, args: Tuple) -> bool:
        """
        Validate that the payload matches the expected argument types.
        """
        return len(args) == len(self.arg_types) and all(
            expected is object or isinstance(arg, expected) for arg, expected in zip(args, self.arg_types)  # Handle 'object' explicitly
        )

    def _function_has_valid_signature(self, func: Callable) -> bool:
        """Validate that the callback signature matches the expected argument types."""
        params = list(signature(func).parameters.values())
        return len(params) == len(self.arg_types) and all(
            expected is object or p.annotation in {expected, p.empty} for p, expected in zip(params, self.arg_types)
        )


class UntypedSignal(Signal):
    """
    Signal class that does not enforce payload types and callback signatures.
    Useful for *args and **kwargs scenarios.
    """

    def __init__(self):
        super().__init__(object)

    def _payload_is_valid_type(self, args: Tuple) -> bool:
        return True

    def _function_has_valid_signature(self, func: Callable) -> bool:
        return True
