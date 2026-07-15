# HAR Runner Testing Suite

This tool automates backend integration testing by replaying HTTP Archive (`.har`) requests against a local .NET Aspire environment. It extracts the original request from a HAR file, executes it locally, and compares the actual backend response against the expected output, generating a detailed report.

## Execution Flow

1. **Start the tool**: Run `python main.py` in your terminal.
2. **First-time Setup**: On your very first run, the script will prompt you for two configuration values (which will be saved for future executions):
   - The **PPL Core Platform** folder path.
   - The **local backend base URL** (e.g., `http://localhost:5046`).
3. **Select HAR File**: Enter the name of the `.har` file you want to process. *(On subsequent runs, the tool will skip step 2 and only ask for this file).*
4. **Execution**: The script will automatically check if the local backend is online (waiting for it if necessary).
5. **Report Generation**: It will execute the request, compare the local response against the original `.har` data, and save the final report in the `reports/` folder.

## Expected Results

- **`Ready for Testing`**: Output when the status code, relevant headers, and response body match the HAR file exactly.
- **`Code Review Needed`**: Output when there are relevant structural or data discrepancies between the original HAR response and the local execution.
