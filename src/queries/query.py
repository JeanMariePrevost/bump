from query_result import QueryResult


class Query:
    """
    Abstract query that defines the "interface" for all queries and potentially holds common logic.
    """

    def __init__(self, config: dict) -> None:
        # Parse and validate the monitor configuration
        self._validate_and_apply_config(config)

    def _validate_and_apply_config(self, config: dict) -> None:
        """
        Validate and apply the configuration for the query.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def execute(self) -> QueryResult:
        """
        Execute the query on the given cursor.
        """

        # TODO: Make async, or make the ENTIRE backend monitoring logic its own service
        raise NotImplementedError("Subclasses must implement this method.")
