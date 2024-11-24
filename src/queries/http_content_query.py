from http.client import HTTPResponse

from queries.http_query import HttpQuery


class HttpContentQuery(HttpQuery):
    """
    Looks for a string in the response body.
    """

    @staticmethod
    def from_dict(dictionary: dict) -> "HttpContentQuery":
        HttpContentQuery.assert_keys_exist(dictionary, ["url", "timeout", "string_to_find"])

        return HttpContentQuery(
            url=dictionary["url"],
            timeout=dictionary["timeout"],
            string_to_find=dictionary["string_to_find"],
        )

    def __init__(self, url: str, timeout: float, string_to_find: str) -> None:
        super().__init__(url, timeout)
        self.string_to_find = string_to_find

    def _test_passed_predicate(self, response: HTTPResponse | Exception) -> bool:
        if getattr(response, "code", None) == 200:
            body = response.read().decode("utf-8")
            return self.string_to_find in body
        else:
            return False
