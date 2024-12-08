from datetime import datetime

from http.client import HTTPResponse
import urllib
from urllib.error import HTTPError, URLError
from urllib.request import Request
from queries.query import Query
from queries.query_result import QueryResult


class HttpQuery(Query):
    """
    The base query for http queries.
    This one simply passes if the response code is 200, fails otherwise.
    """

    @classmethod
    def from_dict(cls, dict_object: dict):
        return super().from_dict(dict_object)

    def __init__(self, url: str = "", timeout: float = 1) -> None:
        super().__init__()
        self.url = url
        self.timeout = timeout

    def apply_query_params_string(self, query_params_as_string: str):
        # The basic HttpQuery does not have any parameters to apply
        pass

    def update_query_params_string(self):
        # The basic HttpQuery does not have any parameters to update
        pass

    def parameters_are_valid(self) -> bool:
        if not self.url:
            return False

        if not self.timeout or not isinstance(self.timeout, (int, float)) or self.timeout <= 0:
            return False

        return super().parameters_are_valid()

        # If url cannot be made into a valid URL
        try:
            urllib.parse.urlparse(self.url)
        except ValueError:
            return False

        if self.timeout <= 0:
            return False

    def execute(self) -> QueryResult:
        # Send an HTTP HEAD request to the URL using urllib
        self._start_time = datetime.now()
        try:
            request = Request(self.url)
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return self._postprocess_query_result(self._process_response(response))
        except ValueError as e:
            # URL is invalid?
            return self._postprocess_query_result(self._process_exception(e))
        except HTTPError as e:
            # 404, 500...
            return self._postprocess_query_result(self._process_exception(e))
        except URLError as e:
            # Timeout, URL does not exist or there is a connection issue
            return self._postprocess_query_result(self._process_exception(e))

    def _process_response(self, response: HTTPResponse) -> QueryResult:
        """
        Process the response from the HTTP request and builds the QueryResult.
        """
        # Default http behavior is simply that it exists, i.e status code 200
        return QueryResult(
            start_time=self._start_time,
            end_time=datetime.now(),
            test_passed=self._test_passed_predicate(response),
            retries=1,
            code_or_status=response.code,
            message=response.msg,
            reason=response.reason,
        )

    def _process_exception(self, e: Exception) -> QueryResult:
        """
        Process an exception that occurred during the query and builds the QueryResult.
        """
        return QueryResult(
            start_time=self._start_time,
            end_time=datetime.now(),
            test_passed=self._test_passed_predicate(e),
            retries=1,
            code_or_status=e.status if hasattr(e, "status") else None,
            message=e.msg if hasattr(e, "msg") else str(e),
            reason=e.reason if hasattr(e, "reason") else str(e),
            exception_type=type(e).__name__,
        )

    def _test_passed_predicate(self, response: HTTPResponse | Exception) -> bool:
        if isinstance(response, Exception):
            return False
        return response.code == 200
