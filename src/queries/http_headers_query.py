from http.client import HTTPResponse

from queries.http_query import HttpQuery
from queries.query import Query
from queries.query_result import QueryResult


class HttpHeadersQuery(HttpQuery):
    """
    Looks for a specific key:value pair in the response headers.
    """

    def __init__(self, url: str = "", timeout: float = Query.DEFAULT_TIMEOUT, header_key: str = "", header_value: str = "") -> None:
        super().__init__(url, timeout)
        self.header_key = header_key
        self.header_value = header_value

    def apply_query_params_string(self, query_params_as_string: str):
        # Error if null or empty, or doesn't match /.+:.+/
        if not query_params_as_string:
            raise ValueError("query_params_as_string cannot be null or empty")
        if not ":" in query_params_as_string:
            raise ValueError("query_params_as_string must be in the format 'key:value'")
        self.header_key, self.header_value = query_params_as_string.split(":")
        self.update_query_params_string()

    def update_query_params_string(self):
        self.query_params_as_string = f"{self.header_key}:{self.header_value}"

    def parameters_are_valid(self) -> bool:
        if not self.header_key or not self.header_value:
            return False

        return super().parameters_are_valid()

    def _test_passed_predicate(self, response: HTTPResponse | Exception) -> bool:
        if hasattr(response, "headers"):
            return response.headers.get(self.header_key) == self.header_value
        else:
            return False

    def _postprocess_query_result(self, query_result: QueryResult) -> QueryResult:
        if query_result.exception_type is None and not query_result.test_passed:
            # Failed because of the rule, not because of an exception
            query_result.reason = "Did not contain specified header."
        return super()._postprocess_query_result(query_result)
