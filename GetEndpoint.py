import json
import sys
from pathlib import Path

def safe_name(value):
    # Remove any characters that are not alphanumeric, hyphens, underscores, or periods and replace them with underscores.
    safe_value = "".join(character if character.isalnum() or character in ("-", "_", ".") else "_" for character in value)
    # Substitute characters to "_"
    return safe_value.strip("._") or "entry"


def format_response_content(content):
    if content is None:
        return ""
    if isinstance(content, str):
        try:
            parsed_content = json.loads(content)
        except json.JSONDecodeError:
            return content
        # if json is valid resturn it formatted
        return json.dumps(parsed_content, indent=2, ensure_ascii=False)
    # if content is a dictionary or list, return it formatted
    return json.dumps(content, indent=2, ensure_ascii=False)


# Builds an HTTP request string from the given method, URL, headers, and body.
def build_http_request(method, url, headers, body):
    lines = [f"{method} {url} HTTP/1.1"]
    # Build the headers section of the HTTP request
    if headers:
        for header_name, header_value in headers.items():
            lines.append(f"{header_name}: {header_value}")
    # Return the body section of the HTTP request if it exists
    if body:
        lines.append("")
        lines.append(body)

    return "\n".join(lines)

# Save the output in a folder with the same name as the HAR file, and create two files for each entry: one for the HTTP request and another for the response content.
def save_entry_files(output_dir, index, method, url, headers, body, content):
    entry_name = safe_name(Path(url).name or f"entry_{index}")
    http_file_path = output_dir / f"{index:03d}_{entry_name}.http"
    json_file_path = output_dir / f"{index:03d}_{entry_name}.json"

    http_content = build_http_request(method, url, headers, body)
    response_content = format_response_content(content)

    http_file_path.write_text(http_content, encoding="utf-8")
    json_file_path.write_text(response_content, encoding="utf-8")

    print(f"Saved: {http_file_path}")
    print(f"Saved: {json_file_path}")

# Scan the HAR file for all HTTP requests and responses, and save them in the output directory.
def get_endpoints(path):
    har_file_path = Path(path)

    if not har_file_path.is_file():
        print(f"File not found: {har_file_path}")
        return

    with har_file_path.open("r", encoding="utf-8") as file:
        file_content = json.load(file)

    entries = file_content["log"]["entries"]
    output_dir = har_file_path.parent / har_file_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    for index, entry in enumerate(entries, start=1):
        request = entry.get("request", {})
        response = entry.get("response", {})
        method = request.get("method")
        url = request.get("url")
        headers = {header.get("name", ""): header.get("value", "") for header in request.get("headers", []) if header.get("name")}
        text = request.get("postData", {}).get("text")
        content = response.get("content", {}).get("text")
        save_entry_files(output_dir, index, method, url, headers, text, content)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        get_endpoints(sys.argv[1])
    else:
        print("Usage: python GetEndpoint.py <path-to-har-file>")
# path example: ..\x\y\UnderwriterRequestDetails_DataActionGetPlacementSubmissions_OS_Request.har
