from datetime import datetime
import re

from playwright.sync_api import sync_playwright
from queries.query import Query
from queries.query_result import QueryResult


class RenderedContentRegexQuery(Query):
    """
    Looks for a string in the actual rendered page (e.g. after JavaScript has run).
    """

    def __init__(
        self, url: str = "", timeout: float = 1, regex_to_find: str = "", multi_line: bool = False, ignore_case: bool = False, dot_all: bool = False
    ) -> None:
        """
        :param url: The URL to query
        :param timeout: The timeout in seconds for the query
        :param regex_to_find: The regex pattern to search for
        :param multi_line: Whether to use the multi-line flag
        :param ignore_case: Whether to use the ignore-case flag
        :param dot_all: Whether to use the dot-all flag
        """
        super().__init__()
        self.url = url
        self.timeout = timeout
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

        if not self.url:
            return False

        if not self.timeout:
            return False

        if not isinstance(self.timeout, (int, float)) or self.timeout <= 0:
            return False

        if not isinstance(self.multi_line, bool):
            return False

        if not isinstance(self.ignore_case, bool):
            return False

        if not isinstance(self.dot_all, bool):
            return False

        return super().parameters_are_valid()

    def execute(self) -> QueryResult:
        self._start_time = datetime.now()
        try:
            # Use Playwright to render the page to get the "real" content
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(self.url, timeout=self.timeout * 1000)
                page.wait_for_load_state("networkidle")  # Wait until network requests are idle
                rendered_content = page.content()
                browser.close()
        except Exception as e:
            return QueryResult(
                start_time=self._start_time,
                end_time=datetime.now(),
                test_passed=False,
                retries=1,
                code_or_status=type(e).__name__,
                message=str(e),
                reason=str(e),
            )

        test_passed = self._test_passed_predicate(rendered_content)
        return QueryResult(
            start_time=self._start_time,
            end_time=datetime.now(),
            test_passed=test_passed,
            retries=1,
            code_or_status=None,
            message=None,
            reason="Did not match regex pattern." if not test_passed else None,
        )

    def _test_passed_predicate(self, rendered_content: str) -> bool:
        self.flags = 0
        if self.multi_line:
            self.flags |= re.MULTILINE
        if self.ignore_case:
            self.flags |= re.IGNORECASE
        if self.dot_all:
            self.flags |= re.DOTALL

        compiled_pattern = re.compile(self.regex_to_find, self.flags)
        return bool(compiled_pattern.search(rendered_content))
