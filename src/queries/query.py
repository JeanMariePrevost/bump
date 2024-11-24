from queries.query_result import QueryResult


class Query:
    """
    Abstract query that defines the "interface" for all queries and potentially holds common logic.
    """

    @staticmethod
    def assert_keys_exist(dictionary: dict, required_keys: list[str]) -> None:
        """
        Validates if a dictionary contains the required keys.

        E.g. validate_dict(my_dict, ["a", "b"])
        """
        if not isinstance(dictionary, dict):
            raise ValueError(f"Expected a dictionary, got {type(dictionary)}")

        for key in required_keys:
            if key not in dictionary:
                raise ValueError(f"Missing key {key} in dictionary {dictionary}")

    @staticmethod
    def from_dict(dictionary: dict) -> "Query":
        """
        Create a query from a dictionary.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def __init__(self) -> None:
        self._retries = 0

    def execute(self) -> QueryResult:
        """
        Execute the query on the given cursor.
        """

        # TODO: Make async, or make the ENTIRE backend monitoring logic its own service
        raise NotImplementedError("Subclasses must implement this method.")
