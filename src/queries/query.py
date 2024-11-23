from queries.query_result import QueryResult


class Query:
    """
    Abstract query that defines the "interface" for all queries and potentially holds common logic.
    """

    def __init__(self) -> None:
        self._retries = 0

    def execute(self) -> QueryResult:
        """
        Execute the query on the given cursor.
        """

        # TODO: Make async, or make the ENTIRE backend monitoring logic its own service
        raise NotImplementedError("Subclasses must implement this method.")
