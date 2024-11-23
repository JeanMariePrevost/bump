from datetime import datetime
from urllib import request

import urllib
from queries.query import Query
from query_result import QueryResult


class HttpAvailabilityQuery(Query):
    """
    The most basic query that sends an HTTP HEAD request to a given URL.
    Passes if the response code is 200, fails otherwise.
    """

    def _validate_and_apply_config(self, config: dict) -> None:
        # Confirm we have a URL and timeout in the config
        if "url" not in config:
            raise ValueError("URL not found in config")
        if "timeout" not in config:
            raise ValueError("Timeout not found in config")
        self.url = config["url"]
        self.timeout = config["timeout"]

    def execute(self) -> QueryResult:
        # Send an HTTP HEAD request to the URL using urllib
        start_time = datetime.now()
        try:
            request = urllib.request.Request(self.url, method="HEAD")
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return QueryResult(
                    start_time=start_time,
                    end_time=datetime.now(),
                    test_passed=response.code == 200,
                    tries=1,  # TODO: Implement retries
                    code_or_status=response.code,
                    message=response.msg,
                    reason=response.reason,
                )
        except ValueError as e:
            # URL is invalid
            return QueryResult(
                start_time=start_time,
                end_time=datetime.now(),
                test_passed=False,
                tries=1,
                code_or_status="ValueError",
                message=str(e),
                reason=str(e.reason),
            )
        except urllib.error.HTTPError as e:
            # Unsure what can trigger this
            return QueryResult(
                start_time=start_time,
                end_time=datetime.now(),
                test_passed=False,
                tries=1,
                code_or_status=e.code,
                message=str(e),
                reason=str(e.reason),
            )
        except urllib.error.URLError as e:
            # Timeout, URL does not exist or there is a connection issue
            return QueryResult(
                start_time=start_time,
                end_time=datetime.now(),
                test_passed=False,
                tries=1,
                code_or_status="URLError",
                message=str(e),
                reason=str(e.reason),
            )
