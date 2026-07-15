# HAR Runner Testing Suite

This tool automates backend integration testing by replaying HTTP Archive (`.har`) requests against a local .NET Aspire environment. It extracts the original request from a HAR file, executes it locally, and compares the actual backend response against the expected output, generating a report.

## Architecture

- **`main.py`**: Orchestrates the core execution flow. Reads configurations and Git branches, loads the HAR file, prompts for manual entry selection, triggers the local request, compares results, and saves the final report.
- **`har_extractor.py`**: Parses the `.har` file to extract the HTTP method, path, query parameters, headers, and body. It also provides the interface for manual entry selection.
- **`request_runner.py`**: Constructs the local .NET Aspire URL. It preserves the original path, query string, request body, and HTTP method, sending the exact request to the local backend. Includes optional wait-for-backend support.
- **`response_comparator.py`**: Compares HTTP status codes, relevant headers, and response bodies. It intelligently ignores volatile headers (like `Date`, `Server`, `Content-Length`, and correlation IDs) and performs structural JSON comparisons where possible, generating a readable diff for any discrepancies.
- **`reporter.py`**: Constructs and persists the final comparison report. Documents the Git branch, HAR file used, targeted endpoint, expected vs. actual status, and the generated diff.
- **`config.py`**: Manages the persistence of local configurations, including the PPL Core Platform project path.

## Execution Flow
Afther executing 
1. Place your target `.har` file into the `Compare/hars/` directory.
2. Run `python main.py` from within the `Compare/` directory.
3. Input the name of the `.har` file when prompted.
4. Select the specific request entry you want to test.
5. The tool will extract the endpoint and save the expected response in the `processed_hars/` folder for better visualization.
6. Provide the local .NET Aspire URL (e.g., `http://localhost:5046`), or allow the script to use the saved backend endpoint from `config.json`.
7. The runner waits for the backend to be ready, executes the request, compares the responses, and saves the output report in `Compare/reports/`.

## Expected Results

- **`Ready for Testing`**: Output when the status code, relevant headers, and response body match the HAR file exactly.
- **`Code Review Needed`**: Output when there are relevant structural or data discrepancies between the original HAR response and the local execution.

## Important Notes

- The `.har` file acts as the strict primary source of truth for the baseline request.
- Only the host URL is replaced (pointing to the local Aspire environment). The request path, query strings, and payload body remain strictly unaltered to ensure an accurate 1:1 test.
