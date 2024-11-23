from datetime import datetime


class QueryResult:
    """Class to hold the results of a query"""

    def __init__(self, start_time: datetime, end_time: datetime, test_passed: bool, tries: int, code_or_status: int, message: str, reason: str):
        self.start_time = start_time.isoformat()
        self.end_time = end_time.isoformat()
        self.test_passed = test_passed
        self.tries = tries
        self.code_or_status = code_or_status
        self.message = message
        self.reason = reason
