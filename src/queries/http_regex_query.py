import re
from http.client import HTTPResponse

from queries.http_query import HttpQuery


class HttpRegexQuery(HttpQuery):
    """
    Looks for a string in the response body.
    """

    @staticmethod
    def from_dict(dictionary: dict) -> "HttpRegexQuery":
        HttpRegexQuery.assert_keys_exist(dictionary, ["url", "timeout", "regex_to_find"])
        return HttpRegexQuery(
            url=dictionary["url"],
            timeout=dictionary["timeout"],
            regex_to_find=dictionary["regex_to_find"],
            multi_line=dictionary.get("multi_line", False),
            ignore_case=dictionary.get("ignore_case", False),
            dot_all=dictionary.get("dot_all", False),
        )

    def __init__(
        self, url: str, timeout: float, regex_to_find: str, multi_line: bool = False, ignore_case: bool = False, dot_all: bool = False
    ) -> None:
        """
        :param url: The URL to query
        :param timeout: The timeout in seconds for the query
        :param regex_to_find: The regex pattern to search for
        :param multi_line: Whether to use the multi-line flag
        :param ignore_case: Whether to use the ignore-case flag
        :param dot_all: Whether to use the dot-all flag
        """
        super().__init__(url, timeout)
        self.regex_to_find = regex_to_find
        self.multi_line = multi_line
        self.ignore_case = ignore_case
        self.dot_all = dot_all

    def _test_passed_predicate(self, response: HTTPResponse | Exception) -> bool:
        self.flags = 0
        if self.multi_line:
            self.flags |= re.MULTILINE
        if self.ignore_case:
            self.flags |= re.IGNORECASE
        if self.dot_all:
            self.flags |= re.DOTALL

        compiled_pattern = re.compile(self.regex_to_find, self.flags)
        if getattr(response, "code", None) == 200:
            body = response.read().decode("utf-8")
            return bool(compiled_pattern.search(body))
        else:
            return False
