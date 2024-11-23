from datetime import datetime
import re

from playwright.sync_api import sync_playwright
from queries.query import Query
from query_result import QueryResult


class RenderedContentRegexQuery(Query):
    """
    Looks for a string in the actual rendered page (e.g. after JavaScript has run).
    """

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
        super().__init__()
        self.url = url
        self.timeout = timeout
        self.regex_to_find = regex_to_find
        self.multi_line = multi_line
        self.ignore_case = ignore_case
        self.dot_all = dot_all

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
                reason=None,
            )

        return QueryResult(
            start_time=self._start_time,
            end_time=datetime.now(),
            test_passed=self._test_passed_predicate(rendered_content),
            retries=1,
            code_or_status=None,
            message=None,
            reason=None,
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
