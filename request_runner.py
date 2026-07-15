"""Sends HTTP requests to the local backend and waits for it to become reachable.

SSL verification is disabled since the local backend typically runs on a
self-signed development certificate.
"""

import ssl
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _build_ssl_context() -> ssl.SSLContext:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


# Decodes a raw response body using the charset declared in its Content-Type header.
def _decode_response_body(raw_body: bytes, headers: Any) -> str:
    if hasattr(headers, "get_content_charset"):
        charset = headers.get_content_charset("utf-8")
    elif isinstance(headers, dict):
        content_type = headers.get("Content-Type") or headers.get("content-type") or ""
        charset = "utf-8"
        for part in content_type.split(";"):
            if part.strip().lower().startswith("charset="):
                charset = part.split("=", 1)[1].strip().strip('"')
                break
    else:
        charset = "utf-8"

    return raw_body.decode(charset, errors="replace")

# Function to wait for the backend to be available
def wait_for_backend(base_url: str, timeout_seconds: float = 10.0, interval_seconds: float = 0.5) -> bool:
    deadline = time.monotonic() + timeout_seconds
    request = Request(base_url, method="HEAD")
    ssl_context = _build_ssl_context()

    while True:
        try:
            with urlopen(request, timeout=interval_seconds, context=ssl_context) as response:
                return True
        except HTTPError:
            return True
        except URLError:
            if time.monotonic() >= deadline:
                return False
            time.sleep(interval_seconds)

# Function to send an HTTP request based on the request specification and return the response
def send_request(request_spec: dict[str, Any], target_url: str, timeout_seconds: float = 15.0) -> dict[str, Any]:
    headers = {
        name: value
        for name, value in request_spec.get("headers", {}).items()
        if name.lower() not in {"host", "content-length"}
    }

    body = request_spec.get("body", "") or ""
    data = body.encode("utf-8") if body else None
    request = Request(target_url, data=data, headers=headers, method=request_spec.get("method", "GET"))

    ssl_context = _build_ssl_context()

    try:
        with urlopen(request, timeout=timeout_seconds, context=ssl_context) as response:
            raw_body = response.read()
            return {
                "status": response.getcode(),
                "headers": dict(response.getheaders()),
                "body": _decode_response_body(raw_body, response.headers),
            }
    except HTTPError as error:
        raw_body = error.read()
        return {
            "status": error.code,
            "headers": dict(error.headers.items()),
            "body": _decode_response_body(raw_body, error.headers),
        }
