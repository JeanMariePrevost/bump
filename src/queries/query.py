from queries.query_result import QueryResult
from serialization import Deserializable


class Query(Deserializable):
    """
    Abstract query that defines the "interface" for all queries and potentially holds common logic.
    """

    def __init__(self) -> None:
        self.query_params_as_string = ""  # Used for the frontend, as it configures queries through a single text field

    def apply_query_params_string(self, query_params_as_string: str):
        """
        Apply the query parameters from a string.
        Used when applying setings from the frontend.
        Each subclass implements its own logic for parsing the string.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def update_query_params_string(self):
        """
        Update the query parameters string to be read by the frontend.
        Each subclass implements its own logic for translating its configuration to a string.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def execute(self) -> QueryResult:
        """
        Execute the query on the given cursor.
        """

        # TODO: Make async, or make the ENTIRE backend monitoring logic its own service
        raise NotImplementedError("Subclasses must implement this method.")

    def _postprocess_query_result(self, query_result: QueryResult) -> QueryResult:
        """
        Hook to allow for post-processing of the query result.
        E.g. to add rule failure information, like "if respons eif fine but test failed, set the reason to 'Did not contain the string'"
        """
        return query_result
