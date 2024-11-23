from http.client import HTTPResponse

from queries.http_query import HttpQuery


class HttpHeadersQuery(HttpQuery):
    """
    Looks for a specific key:value pair in the response headers.
    """

    def __init__(self, url: str, timeout: float, header_key: str, header_value: str) -> None:
        super().__init__(url, timeout)
        self.header_key = header_key
        self.header_value = header_value

    def _test_passed_predicate(self, response: HTTPResponse | Exception) -> bool:
        # Debug, print the headers
        if hasattr(response, "headers"):
            print(response.headers)

        if hasattr(response, "headers"):
            return response.headers.get(self.header_key) == self.header_value
        else:
            return False
