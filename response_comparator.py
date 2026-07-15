"""Compares a HAR-recorded (expected) HTTP response against the actual local-backend response.

Status, headers (minus volatile ones) and body are compared independently;
compare_response() combines them into a single ready_for_testing verdict.
"""

import difflib
import json
from typing import Any


# Headers that vary between environments/requests and would cause false-positive diffs.
IGNORED_HEADERS = {
    "date",
    "server",
    "content-length",
    "transfer-encoding",
    "x-request-id",
    "x-correlation-id",
    "connection",
    "set-cookie",
}


def normalize_header_name(name: str) -> str:
    return name.strip().lower()


def filter_relevant_headers(headers: dict[str, str]) -> dict[str, str]:
    return {
        normalize_header_name(name): value.strip()
        for name, value in headers.items()
        if normalize_header_name(name) not in IGNORED_HEADERS
    }


def parse_json(value: str) -> Any:
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None


def pretty_json(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True)


def build_text_diff(expected: str, actual: str) -> str:
    expected_lines = expected.splitlines(keepends=True)
    actual_lines = actual.splitlines(keepends=True)
    return "".join(difflib.unified_diff(expected_lines, actual_lines, fromfile="expected", tofile="actual"))


# Function to compare the expected and actual responses
def compare_response(expected: dict[str, Any], actual: dict[str, Any]) -> dict[str, Any]:
    expected_headers = filter_relevant_headers(expected.get("headers", {}))
    actual_headers = filter_relevant_headers(actual.get("headers", {}))

    header_diffs = []
    all_header_keys = sorted(set(expected_headers) | set(actual_headers))
    for name in all_header_keys:
        expected_value = expected_headers.get(name)
        actual_value = actual_headers.get(name)
        if expected_value != actual_value:
            header_diffs.append(f"Header {name}: expected={expected_value!r} actual={actual_value!r}")

    expected_body = expected.get("body", "") or ""
    actual_body = actual.get("body", "") or ""

    expected_json = parse_json(expected_body)
    actual_json = parse_json(actual_body)
    body_diff = ""
    body_match = False

    if expected_json is not None and actual_json is not None:
        body_match = expected_json == actual_json
        if not body_match:
            body_diff = build_text_diff(pretty_json(expected_json), pretty_json(actual_json))
    else:
        if expected_body == actual_body:
            body_match = True
        else:
            normalized_expected = expected_body.replace("\r\n", "\n").strip()
            normalized_actual = actual_body.replace("\r\n", "\n").strip()
            body_match = normalized_expected == normalized_actual
            if not body_match:
                body_diff = build_text_diff(normalized_expected, normalized_actual)

    status_match = expected.get("status") == actual.get("status")
    full_match = status_match and not header_diffs and body_match

    return {
        "status_match": status_match,
        "header_match": not header_diffs,
        "body_match": body_match,
        "header_diffs": header_diffs,
        "body_diff": body_diff,
        "ready_for_testing": full_match,
    }
