"""Extracts HAR entries into per-entry .http/.json files under processed_hars/,
and can parse those .http files back into a request spec for replay in main.py.
"""

import json
import shutil
import sys
from pathlib import Path


# Sanitizes a string for use as a filename.
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
        # if json is valid return it formatted
        return json.dumps(parsed_content, indent=2, ensure_ascii=False)
    # if content is a dictionary or list, return it formatted
    return json.dumps(content, indent=2, ensure_ascii=False)


# Builds an HTTP request string from the given method, URL, headers, and body.
def build_http_request(method, url, headers, body):
    lines = [f"{method} {url} HTTP/1.1"]
    if headers:
        for header_name, header_value in headers.items():
            lines.append(f"{header_name}: {header_value}")
    if body:
        lines.append("")
        lines.append(body)

    return "\n".join(lines)

# Save the output in a folder with the same name as the HAR file, and create two files for each entry.
def save_entry_files(output_dir, index, method, url, headers, body, content):
    entry_name = safe_name(Path(url).name or f"entry_{index}")
    http_file_path = output_dir / f"{index:03d}_{entry_name}.http"
    json_file_path = output_dir / f"{index:03d}_{entry_name}.json"

    http_content = build_http_request(method, url, headers, body)
    response_content = format_response_content(content)

    http_file_path.write_text(http_content, encoding="utf-8")
    json_file_path.write_text(response_content, encoding="utf-8")

# Resolve the HAR file path based on the script directory and the provided HAR file name.
def resolve_har_path(path):
    har_file_path = Path(path).expanduser()
    if not har_file_path.is_absolute():
        har_file_path = (Path(__file__).resolve().parent / har_file_path).resolve()
    return har_file_path


def resolve_processed_har_path(har_file_path):
    processed_root = har_file_path.parent.parent / "processed_hars"
    processed_root.mkdir(parents=True, exist_ok=True)
    processed_har_file_path = processed_root / har_file_path.name
    return processed_har_file_path


# Returns the processed_hars/<har_stem> folder for a given .har file path.
def resolve_processed_entries_dir(har_file_path):
    return resolve_processed_har_path(har_file_path).parent / har_file_path.stem


# Lists the processed .http entry files for a har, as (entry_index, http_path) sorted by index.
def find_processed_entries(processed_dir):
    if not processed_dir.is_dir():
        return []

    entries = []
    for http_file in processed_dir.glob("*.http"):
        prefix = http_file.stem.split("_", 1)[0]
        if prefix.isdigit():
            entries.append((int(prefix), http_file))

    entries.sort(key=lambda item: item[0])
    return entries


# Parses a saved .http request file back into method, url, headers and body.
def parse_http_file(http_file_path):
    content = http_file_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    request_line = lines[0]
    method, rest = request_line.split(" ", 1)
    url = rest.rsplit(" HTTP/", 1)[0].strip()

    headers = {}
    line_index = 1
    while line_index < len(lines) and lines[line_index].strip() != "":
        line = lines[line_index]
        if ":" in line:
            name, value = line.split(":", 1)
            headers[name.strip()] = value.strip()
        line_index += 1

    body = ""
    if line_index + 1 < len(lines):
        body = "\n".join(lines[line_index + 1:])

    return {
        "method": method.strip(),
        "url": url,
        "headers": headers,
        "body": body,
    }


# Extracts every entry in a single HAR file into indexed .http/.json files, replacing any previous output.
def process_har_file(har_file_path):
    har_file_path = resolve_har_path(har_file_path)
    processed_har_file_path = resolve_processed_har_path(har_file_path)
    if not har_file_path.is_file():
        print(f"File not found: {har_file_path}")
        return False

    with har_file_path.open("r", encoding="utf-8") as file:
        file_content = json.load(file)

    entries = file_content.get("log", {}).get("entries", [])
    output_dir = processed_har_file_path.parent / har_file_path.stem
    if output_dir.exists():
        shutil.rmtree(output_dir)
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

    print(f"Processed {har_file_path.name} -> {output_dir}")
    return True


# Scan the HAR files in a folder (or a single HAR file) and save them in the output directory.
def get_endpoints(path):
    input_path = resolve_har_path(path)

    if input_path.is_dir():
        har_files = sorted(
            {
                candidate.resolve()
                for candidate in input_path.iterdir()
                if candidate.is_file() and candidate.suffix.lower() == ".har"
            },
            key=lambda candidate: candidate.name.lower(),
        )
        if not har_files:
            print(f"No .har files found in {input_path}")
            return False

        all_ok = True
        for har_file in har_files:
            all_ok = process_har_file(har_file) and all_ok

        print(f"--- Extraction completed for {len(har_files)} HAR file(s) ---")
        return all_ok

    return process_har_file(input_path)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        get_endpoints(sys.argv[1])
    else:
        default_path = Path(__file__).resolve().parent / "hars"
        get_endpoints(default_path)
