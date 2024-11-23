import time
from queries.http_availability_query import HttpStatusCodeQuery
from queries.http_query import HttpQuery


print("Welcome to bump.")
print("Current behavior is to run a series of simple queries to test the monitoring system.")


def run_debug_query(Query, expected_to_pass):
    time.sleep(0.4)  # Just to not bombard the servers
    result = Query.execute()
    if result.test_passed == expected_to_pass:
        print(f"AS EXPECTED: {result}")
    else:
        print(f"NOPE, something's not right: {result}")


run_debug_query(HttpQuery(url="http://www.google.com", timeout=1), True)
run_debug_query(HttpStatusCodeQuery(url="http://www.httpstat.us/200", timeout=1, expected_status_code=200), True)
run_debug_query(HttpStatusCodeQuery(url="http://www.httpstat.us/200", timeout=1, expected_status_code=404), False)
run_debug_query(HttpStatusCodeQuery(url="https://httpstat.us/404", timeout=1, expected_status_code=404), True)
run_debug_query(HttpQuery(url="https://httpstat.us/200", timeout=1), True)
run_debug_query(HttpStatusCodeQuery(url="https://httpstat.us/200", timeout=1, expected_status_code=500), False)
run_debug_query(HttpStatusCodeQuery(url="https://thereissimplynowaythisisanactualurl", timeout=1, expected_status_code=500), False)
run_debug_query(HttpQuery(url="https://httpstat.us/200", timeout=0.0001), False)  # Forced timeout
run_debug_query(HttpStatusCodeQuery(url="https://httpstat.us/200", timeout=0.0001, expected_status_code=200), False)  # Forced timeout
