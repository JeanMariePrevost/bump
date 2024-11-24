from datetime import datetime
from serialization import Deserializable


class QueryResult(Deserializable):
    """Class to hold the results of a query"""

    def __init__(
        self,
        start_time: datetime = None,
        end_time: datetime = None,
        test_passed: bool = None,
        retries: int = None,
        code_or_status: int = None,
        message: str = None,
        reason: str = None,
        exception_type: str = None,
    ) -> None:
        self.start_time = start_time
        self.end_time = end_time
        self.test_passed = test_passed
        self.retries = retries
        self.code_or_status = code_or_status
        self.message = message
        self.reason = reason
        self.exception_type = exception_type

    def __str__(self):
        status = "Passed" if self.test_passed else "Failed"
        return f"{status} - Start: {self.start_time}, End: {self.end_time}, Retries: {self.retries}, Code/Status: {self.code_or_status}, Message: {self.message}, Reason: {self.reason}, Exception Type: {self.exception_type}"
