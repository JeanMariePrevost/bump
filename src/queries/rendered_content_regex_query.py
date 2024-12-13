from datetime import datetime
import re

from playwright.sync_api import sync_playwright
from common.custom_logging import get_general_logger
from queries.query import Query
from queries.query_result import QueryResult


class RenderedContentRegexQuery(Query):
    """
    Looks for a string in the actual rendered page (e.g. after JavaScript has run).
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

        if not self.timeout or not isinstance(self.timeout, (int, float)) or self.timeout <= 0:
            return False

        if not isinstance(self.multi_line, bool):
            return False

        if not isinstance(self.ignore_case, bool):
            return False

        if not isinstance(self.dot_all, bool):
            return False

        return super().parameters_are_valid()

    def get_rendered_page_content(self, url: str, timeout: int = 30) -> str:
        """
        Gets the fully rendered content of a webpage using Playwright.
        Returns the HTML content as a string.

        NOTE: MAJOR not-understood code block here, this was taken straight from various online snippets and appears to work
        """
        from playwright.async_api import async_playwright
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        async def _get_content():
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                try:
                    page = await browser.new_page()
                    await page.goto(url, timeout=timeout * 1000)
                    await page.wait_for_load_state("networkidle")
                    return await page.content()
                finally:
                    await browser.close()

        if asyncio.get_event_loop().is_running():
            # We're in an event loop, so run in a separate thread
            with ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _get_content())
                return future.result()

        # If no event loop, just run it
        return asyncio.run(_get_content())

    def execute(self) -> QueryResult:
        self._start_time = datetime.now()
        try:
            rendered_content = self.get_rendered_page_content(self.url, self.timeout)
        except Exception as e:
            get_general_logger().error(f"Error getting rendered content: {e}")

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
