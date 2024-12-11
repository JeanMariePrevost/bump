# Query Types

Queries define the conditions a monitored resource must meet to be considered "up". Each monitor uses one of the available query types to perform checks. This page provides an overview of the supported query types and their configuration options.

Most query types take in an additional "Condition" argument, described for each below.

---

## Available Query Types

### 1. **HTTP Simple**
- **Description**: Performs a basic HTTP request (similar to a ping) and considers the resource reachable if the server responds.
- **Condition**: None.

---

### 2. **HTTP Status Code**
- **Description**: Verifies that the server responds with a specific HTTP status code.
- **Condition**: The expected code (e.g., `200`, `404`).

---

### 3. **HTTP Content**
- **Description**: Checks for the presence of a specific string in the raw HTTP response body. Case-sensitive.
- **Condition**: The string to search for (e.g., `"Welcome to"`).
- **Example**:
  - Monitor passes if the string `"Welcome to"` is found in the response.

---

### 4. **HTTP Regex**
- **Description**: Similar to HTTP Content but uses a regular expression to match content in the raw HTTP response body.
- **Condition**: The regex pattern to search for (e.g., `"[Ww]elcome back .*!"`).
- **Example**:
  - Monitor passes if the regex matches any part of the response body.

---

### 5. **HTTP Headers**
- **Description**: Checks for the presence and value of a specific HTTP header in the server's response.
- **Condition**: The header and expected value (e.g., `"Content-Type: text/html"`).
- **Example**:
  - Monitor passes if the server returns the header `Content-Type` with the value `text/html`.

---

### 6. **Rendered Page Content Regex**
- **Description**: Fully renders the page as a browser would using [Playwright](https://playwright.dev/), then matches the rendered content against a regular expression.
- **Condition**: The regex pattern to search for (e.g., `"[Ww]elcome back .*!"`).
- **Example**:
  - Monitor passes if the regex matches any part of the fully rendered page.
- **Note** This is a slower and more expensive process.

---

## Choosing the Right Query Type
Select the query type based on the kind of verification needed:
- Use **HTTP Simple** for basic availability.
- Use **HTTP Status Code** to validate server responses.
- Use **HTTP Content** or **HTTP Regex** for specific text in the raw response.
- Use **HTTP Headers** to check server metadata.
- Use **Rendered Page Content Regex** for advanced checks on dynamic, JavaScript-heavy pages.