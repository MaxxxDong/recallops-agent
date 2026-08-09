from __future__ import annotations

import base64
import io
from typing import Any

from .http import application


def handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    request = event.get("requestContext", {}).get("http", {})
    body = event.get("body") or ""
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode()
    status_headers: dict[str, Any] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        status_headers["statusCode"] = int(status.split()[0])
        status_headers["headers"] = dict(headers)

    environ = {
        "REQUEST_METHOD": request.get("method", "GET"),
        "PATH_INFO": request.get("path", event.get("rawPath", "/")),
        "QUERY_STRING": event.get("rawQueryString", ""),
        "CONTENT_LENGTH": str(len(body.encode())),
        "wsgi.input": io.BytesIO(body.encode()),
    }
    payload = b"".join(application(environ, start_response))
    return {**status_headers, "body": payload.decode("utf-8")}
