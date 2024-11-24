import time
from monitor.monitor import Monitor
from queries.http_content_query import HttpContentQuery
from queries.http_headers_query import HttpHeadersQuery
from queries.http_regex_query import HttpRegexQuery
from queries.http_status_code_query import HttpStatusCodeQuery
from queries.http_query import HttpQuery
from queries.rendered_content_regex_query import RenderedContentRegexQuery
from monitor.monitors_manager import MonitorsManager


print("Welcome to bump.")
print("Current behavior is to run a series of simple queries to test the monitoring system.")


def run_debug_query(Query, expected_to_pass):
    time.sleep(0.4)  # Just to not bombard the servers
    result = Query.execute()
    if result.test_passed == expected_to_pass:
        print(f"AS EXPECTED: {result}")
    else:
        print(f"NOPE, something's not right: {result}")


# run_debug_query(HttpQuery(url="http://www.google.com", timeout=1), True)
# run_debug_query(HttpStatusCodeQuery(url="http://www.httpstat.us/200", timeout=1, expected_status_code=200), True)
# run_debug_query(HttpStatusCodeQuery(url="http://www.httpstat.us/200", timeout=1, expected_status_code=404), False)
# run_debug_query(HttpStatusCodeQuery(url="https://httpstat.us/404", timeout=1, expected_status_code=404), True)
# run_debug_query(HttpQuery(url="https://httpstat.us/200", timeout=1), True)
# run_debug_query(HttpStatusCodeQuery(url="https://httpstat.us/200", timeout=1, expected_status_code=500), False)
# run_debug_query(HttpStatusCodeQuery(url="https://thereissimplynowaythisisanactualurl", timeout=1, expected_status_code=500), False)
# run_debug_query(HttpQuery(url="https://httpstat.us/200", timeout=0.0001), False)  # Forced timeout
# run_debug_query(HttpStatusCodeQuery(url="https://httpstat.us/200", timeout=0.0001, expected_status_code=200), False)  # Forced timeout
# run_debug_query(HttpHeadersQuery(url="https://httpstat.us/200", timeout=1, header_key="Content-Type", header_value="text/plain"), True)
# run_debug_query(HttpContentQuery(url="https://github.com/JeanMariePrevost/pyfolio", timeout=1, string_to_find="Easy Portfolio Websites"), True)
# run_debug_query(HttpContentQuery(url="http://www.google.com", timeout=1, string_to_find="No you won't find this one"), False)

# run_debug_query(HttpRegexQuery(url="https://github.com/JeanMariePrevost/pyfolio", timeout=1, regex_to_find="Easy Port.*lio Websites"), True)
# run_debug_query(HttpRegexQuery(url="https://github.com/JeanMariePrevost/pyfolio", timeout=1, regex_to_find="TLDR.*with Python."), False)
# run_debug_query(HttpRegexQuery(url="https://github.com/JeanMariePrevost/pyfolio", timeout=1, regex_to_find="Easy Port.*abcdefg.*lio Websites"), False)

# run_debug_query(RenderedContentRegexQuery(url="https://github.com/JeanMariePrevost/pyfolio", timeout=1, regex_to_find="Easy.*Websites"), True)
# run_debug_query(RenderedContentRegexQuery(url="https://github.com/JeanMariePrevost/pyfolio", timeout=1, regex_to_find="create.simple"), True)
# run_debug_query(RenderedContentRegexQuery(url="https://github.com/JeanMariePrevost/pyfolio", timeout=1, regex_to_find="This tool.*license"), True)


# TEsting serialiation stuff
monitor = Monitor()
monitor.query = HttpQuery(url="http://www.google.com", timeout=1)


monitor2 = Monitor()
monitor2.query = HttpQuery(url="http://www.google.com", timeout=1)


monitors_manager = MonitorsManager()
monitors_manager.add_monitor(monitor)
monitors_manager.add_monitor(monitor2)
# print("saving monitors")
# monitors_manager.save_monitors_to_file()


print("Testing serialization module's functions")
import serialization

print("Testing serialization of a single query")
encoded_query = serialization.to_encoded_json(monitor.query)
print("Testing serialization of a single monitor")
encoded_monitor = serialization.to_encoded_json(monitor)
print(encoded_monitor)
print("Testing serialization of a monitors manager")
encoded_manager_content = serialization.to_encoded_json(monitors_manager.monitors)
print(encoded_manager_content)

deserialized_monitor = serialization.from_encoded_json(encoded_monitor)
print("Deserialized monitor:")
print(deserialized_monitor)
result = deserialized_monitor.execute()
print(f"Result of deserialized monitor: {result}")

deserialized_manager = serialization.from_encoded_json(encoded_manager_content)
deserialized_query_from_serialized_manager = deserialized_manager[0].query

print("Deserialized query from serialized manager:")
print(deserialized_query_from_serialized_manager)
result = deserialized_query_from_serialized_manager.execute()
print(f"Result of deserialized query from serialized manager: {result}")


# Test saving and loading to and from file
serialization.save_as_json_file(monitors_manager.monitors, "data/monitors.json")
loaded_monitors = serialization.load_from_json_file("data/monitors.json")

new_monitors_manager = MonitorsManager()
new_monitors_manager.monitors = loaded_monitors

new_monitors_manager.execute_monitors()
