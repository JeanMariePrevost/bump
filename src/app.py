from queries.http_availability_query import HttpAvailabilityQuery


print("Welcome to bump.")
# ask user for a url to test for availability
url = input("Please enter a URL to test for availability: ")
# ask user for a timeout value in seconds
timeout = input("Please enter a timeout value in seconds: ")
# Create and run the query
query = HttpAvailabilityQuery({"url": url, "timeout": float(timeout)})
print("Running query...")
result = query.execute()
print("Query complete.")

# Print every member variable of the result

print(f"Start time: {result.start_time}")
print(f"End time: {result.end_time}")
print(f"Test passed: {result.test_passed}")
print(f"Tries: {result.tries}")
print(f"Result code or status: {result.result_code_or_status}")
print(f"Result message: {result.result_message}")
