import time
from queries.http_content_query import HttpContentQuery
from queries.http_headers_query import HttpHeadersQuery
from queries.http_regex_query import HttpRegexQuery
from queries.http_status_code_query import HttpStatusCodeQuery
from queries.http_query import HttpQuery
from queries.rendered_content_regex_query import RenderedContentRegexQuery


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
