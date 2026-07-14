import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


def load_har(har_path: Path) -> dict[str, Any]:
    with har_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def list_entries(har: dict[str, Any]) -> list[dict[str, Any]]:
    return har.get("log", {}).get("entries", [])


def parse_url(url: str) -> tuple[str, str, str]:
    parsed = urlsplit(url)
    path = parsed.path or "/"
    query = parsed.query or ""
    host = parsed.netloc
    return path, query, host


# Replaces everything before "screenservices" in the original URL with the local backend base URL.
def transform_to_local_url(original_url: str, local_base_url: str) -> str:
    marker = "screenservices"
    marker_index = original_url.find(marker)
    if marker_index == -1:
        raise ValueError(f"URL does not contain '{marker}': {original_url}")

    suffix = original_url[marker_index:]
    return f"{local_base_url.rstrip('/')}/{suffix}"


def extract_request(entry: dict[str, Any]) -> dict[str, Any]:
    request = entry.get("request", {})
    url = request.get("url", "")
    method = request.get("method", "GET")
    path, query, host = parse_url(url)
    headers = {
        header.get("name", ""): header.get("value", "")
        for header in request.get("headers", [])
        if header.get("name")
    }
    body = request.get("postData", {}).get("text", "") or ""

    response = entry.get("response", {})
    response_headers = {
        header.get("name", ""): header.get("value", "")
        for header in response.get("headers", [])
        if header.get("name")
    }
    content = response.get("content", {}).get("text", "") or ""
    mime_type = response.get("content", {}).get("mimeType", "") or response_headers.get("Content-Type", "")

    return {
        "request": {
            "method": method,
            "path": path,
            "query": query,
            "headers": headers,
            "body": body,
            "original_url": url,
            "host": host,
        },
        "expected_response": {
            "status": response.get("status", 0),
            "headers": response_headers,
            "body": content,
            "mime_type": mime_type,
        },
    }


def describe_entry(entry: dict[str, Any], index: int) -> str:
    request = entry.get("request", {})
    response = entry.get("response", {})
    url = request.get("url", "")
    method = request.get("method", "GET")
    status = response.get("status", "?")
    return f"{index}. {method} {url} -> {status}"

# Function to choose an entry from the HAR file
def choose_entry(har: dict[str, Any], preferred_index: int | None = None) -> tuple[dict[str, Any], int]:
    entries = list_entries(har)
    if not entries:
        raise ValueError("HAR file contains no entries.")

    if preferred_index is not None:
        if preferred_index < 1 or preferred_index > len(entries):
            raise IndexError(f"Entry index {preferred_index} is out of range.")
        return entries[preferred_index - 1], preferred_index

    print("Found the following HAR entries:")
    for index, entry in enumerate(entries, start=1):
        print(describe_entry(entry, index))

    while True:
        selection = input("Select entry number to execute: ").strip()
        if not selection:
            continue
        if not selection.isdigit():
            print("Please enter a valid entry number.")
            continue

        entry_index = int(selection)
        if 1 <= entry_index <= len(entries):
            return entries[entry_index - 1], entry_index

        print(f"Please choose a number between 1 and {len(entries)}.")
