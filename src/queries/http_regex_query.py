import re
from http.client import HTTPResponse

from queries.http_query import HttpQuery
from queries.query import Query
from queries.query_result import QueryResult


class HttpRegexQuery(HttpQuery):
    """
    Looks for a string in the response body.
    """

    def __init__(
        self,
        url: str = "",
        timeout: float = Query.DEFAULT_TIMEOUT,
        regex_to_find: str = "",
        multi_line: bool = False,
        ignore_case: bool = False,
        dot_all: bool = False,
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

    def apply_query_params_string(self, query_params_as_string: str):
        # Error if null or empty
        if not query_params_as_string:
            raise ValueError("query_params_as_string cannot be null or empty")
        self.regex_to_find = query_params_as_string
        self.update_query_params_string()

    def update_query_params_string(self):
        self.query_params_as_string = self.regex_to_find

    def parameters_are_valid(self) -> bool:
        if not self.regex_to_find:
            return False

        return super().parameters_are_valid()

    def _test_passed_predicate(self, response: HTTPResponse | Exception) -> bool:
        self.flags = 0
        if self.multi_line:
            self.flags |= re.MULTILINE
        if self.ignore_case:
            self.flags |= re.IGNORECASE
        if self.dot_all:
            self.flags |= re.DOTALL

        compiled_pattern = re.compile(self.regex_to_find, self.flags)
        if str(getattr(response, "code", None)) == "200":
            body = response.read().decode("utf-8", errors="ignore")
            return bool(compiled_pattern.search(body))
        else:
            return False

    def _postprocess_query_result(self, query_result: QueryResult) -> QueryResult:
        if query_result.exception_type is None and not query_result.test_passed:
            # Failed because of the rule, not because of an exception
            query_result.reason = "Did not match regex pattern."
        return super()._postprocess_query_result(query_result)
