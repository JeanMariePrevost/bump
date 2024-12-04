from http.client import HTTPResponse

from queries.http_query import HttpQuery
from queries.query_result import QueryResult


class HttpStatusCodeQuery(HttpQuery):
    """
    Looks for a specific HTTP status code in the response.
    An HttpStatusCodeQuery with code 200 would be equivalent to a default HttpQuery.
    """

    def __init__(self, url: str = "", timeout: float = 1, expected_status_code: int = "") -> None:
        super().__init__(url, timeout)
        self.expected_status_code = expected_status_code

    def apply_query_params_string(self, query_params_as_string: str):
        # Error if null or empty
        if not query_params_as_string:
            raise ValueError("query_params_as_string cannot be null or empty")
        self.expected_status_code = query_params_as_string
        self.update_query_params_string()

    def update_query_params_string(self):
        self.query_params_as_string = self.expected_status_code

    def _test_passed_predicate(self, response: HTTPResponse | Exception) -> bool:
        if hasattr(response, "code"):
            return response.code == self.expected_status_code
        elif hasattr(response, "status"):
            return response.status == self.expected_status_code
        else:
            return False

    def _postprocess_query_result(self, query_result: QueryResult) -> QueryResult:
        if query_result.exception_type is None and not query_result.test_passed:
            # Failed because of the rule, not because of an exception
            query_result.reason = f"Expected code {self.expected_status_code}, got {query_result.code_or_status}"
        return super()._postprocess_query_result(query_result)
