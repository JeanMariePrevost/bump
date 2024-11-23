from http.client import HTTPResponse

from queries.http_query import HttpQuery


class HttpStatusCodeQuery(HttpQuery):
    """
    Looks for a specific HTTP status code in the response.
    An HttpStatusCodeQuery with code 200 would be equivalent to a default HttpQuery.
    """

    def __init__(self, url: str, timeout: float, expected_status_code: int) -> None:
        super().__init__(url, timeout)
        self.expected_status_code = expected_status_code

    def _test_passed_predicate(self, response: HTTPResponse | Exception) -> bool:
        if hasattr(response, "code"):
            return response.code == self.expected_status_code
        elif hasattr(response, "status"):
            return response.status == self.expected_status_code
        else:
            return False
