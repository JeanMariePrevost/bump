from datetime import datetime
from common.serialization import Deserializable


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
        self.start_time = start_time if start_time else datetime.now()
        self.end_time = end_time if end_time else datetime.now()
        self.test_passed = bool(test_passed) if test_passed is not None else None
        self.retries = int(retries) if retries else None
        self.code_or_status = int(code_or_status) if code_or_status else None
        self.message = str(message) if message else None
        self.reason = str(reason) if reason else None
        self.exception_type = str(exception_type) if exception_type else None

    def __str__(self):
        status = "Passed" if self.test_passed else "Failed"
        return f"{status} - Start: {self.start_time}, End: {self.end_time}, Retries: {self.retries}, Code/Status: {self.code_or_status}, Message: {self.message}, Reason: {self.reason}, Exception Type: {self.exception_type}"

    def calcualte_latency(self) -> float:
        return (self.end_time - self.start_time).total_seconds()
