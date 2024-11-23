from datetime import datetime


class QueryResult:
    """Class to hold the results of a query"""

    def __init__(
        self,
        start_time: datetime,
        end_time: datetime,
        test_passed: bool,
        retries: int,
        code_or_status: int,
        message: str,
        reason: str,
        exception_type: str = None,
    ) -> None:
        self.start_time = start_time.isoformat()
        self.end_time = end_time.isoformat()
        self.test_passed = test_passed
        self.retries = retries
        self.code_or_status = code_or_status
        self.message = message
        self.reason = reason
        self.exception_type = exception_type

    def __str__(self):
        status = "Passed" if self.test_passed else "Failed"
        return f"{status} - Start: {self.start_time}, End: {self.end_time}, Retries: {self.retries}, Code/Status: {self.code_or_status}, Message: {self.message}, Reason: {self.reason}, Exception Type: {self.exception_type}"
