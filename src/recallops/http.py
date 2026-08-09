from __future__ import annotations

import json
import logging
import os
from importlib.resources import files
from typing import Any
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from .core import ConfigurationRequired, InjectedFailure, RecallOps
from .telemetry import configure

configure()
logging.basicConfig(format='{"level":"%(levelname)s","message":"%(message)s"}', level=logging.INFO)
LOG = logging.getLogger("recallops")
APP = RecallOps()
PROVIDER_APP = None
MAX_BODY_BYTES = 16_384
PUBLIC_DEMO_EVENT = "Checkout latency rose above 2 seconds and duplicate 503 retries appeared."


class RequestTooLarge(ValueError):
    pass


def current_app() -> RecallOps:
    global PROVIDER_APP
    if os.getenv("RECALLOPS_MODE", "demo") == "demo":
        return APP
    if PROVIDER_APP is None:
        from .providers import CockroachStore

        PROVIDER_APP = RecallOps(CockroachStore())
    return PROVIDER_APP


def response(start_response, status: str, body: bytes, content_type: str = "application/json; charset=utf-8"):
    headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(body))),
        ("Cache-Control", "no-store"),
        ("X-Content-Type-Options", "nosniff"),
        ("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; base-uri 'none'"),
    ]
    start_response(status, headers)
    return [body]


def json_response(start_response, status: str, payload: dict[str, Any]):
    return response(start_response, status, json.dumps(payload, ensure_ascii=False).encode())


def read_json(environ) -> dict[str, Any]:
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid_content_length") from exc
    if length < 0:
        raise ValueError("invalid_content_length")
    if length > MAX_BODY_BYTES:
        raise RequestTooLarge("payload_too_large")
    body = environ["wsgi.input"].read(length)
    if len(body) != length:
        raise ValueError("incomplete_body")
    try:
        value = json.loads(body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("invalid_json") from exc
    if not isinstance(value, dict):
        raise ValueError("object_required")
    return value


def application(environ, start_response):
    path, method = environ.get("PATH_INFO", "/"), environ.get("REQUEST_METHOD", "GET")
    try:
        if path == "/" and method == "GET":
            return response(start_response, "200 OK", files("recallops").joinpath("ui.html").read_bytes(), "text/html; charset=utf-8")
        if path == "/ui.js" and method == "GET":
            return response(start_response, "200 OK", files("recallops").joinpath("ui.js").read_bytes(), "text/javascript; charset=utf-8")
        if path == "/ui.css" and method == "GET":
            return response(start_response, "200 OK", files("recallops").joinpath("ui.css").read_bytes(), "text/css; charset=utf-8")
        if path == "/favicon.ico" and method == "GET":
            return response(start_response, "204 No Content", b"", "image/x-icon")
        if path == "/health" and method == "GET":
            return json_response(start_response, "200 OK", {"ok": True, "mode": os.getenv("RECALLOPS_MODE", "demo")})
        if path == "/api/runs" and method == "POST":
            data = read_json(environ)
            text = str(data.get("event_text", ""))
            if not 1 <= len(text) <= 4000:
                raise ValueError("event_text_length")
            if os.getenv("RECALLOPS_PUBLIC_DEMO") == "1" and text != PUBLIC_DEMO_EVENT:
                raise ValueError("public_demo_uses_fixed_synthetic_incident")
            return json_response(start_response, "201 Created", current_app().start(text))
        match = path.strip("/").split("/")
        if len(match) == 3 and match[:2] == ["api", "runs"] and method == "GET":
            return json_response(start_response, "200 OK", current_app().store.get(match[2]))
        if len(match) == 4 and match[:2] == ["api", "runs"] and method == "POST":
            run_id, action = match[2], match[3]
            if action == "approve":
                return json_response(start_response, "200 OK", current_app().approve(run_id))
            if action in {"execute", "resume"}:
                fail = action == "execute" and parse_qs(environ.get("QUERY_STRING", "")).get("fail_once") == ["1"]
                return json_response(start_response, "200 OK", current_app().execute(run_id, fail))
            if action == "audit":
                from .providers import ManagedMCPMemoryAuditor

                return json_response(start_response, "200 OK", {"run_id": run_id, "mcp_write": False, "results": ManagedMCPMemoryAuditor().audit_run(run_id)})
        return json_response(start_response, "404 Not Found", {"error": "not_found"})
    except ConfigurationRequired as exc:
        LOG.warning("configuration_required")
        return json_response(start_response, "503 Service Unavailable", {"error": "configuration_required", "detail": str(exc)})
    except InjectedFailure:
        LOG.warning("injected_failure")
        return json_response(start_response, "503 Service Unavailable", {"error": "injected_failure", "recoverable": True})
    except RequestTooLarge as exc:
        return json_response(start_response, "413 Payload Too Large", {"error": str(exc)})
    except KeyError as exc:
        return json_response(start_response, "404 Not Found", {"error": exc.args[0] if exc.args else "not_found"})
    except ValueError as exc:
        return json_response(start_response, "400 Bad Request", {"error": str(exc)})
    except Exception:
        if os.getenv("RECALLOPS_MODE", "demo") == "demo":
            raise
        LOG.error("provider_error")
        return json_response(start_response, "502 Bad Gateway", {"error": "provider_error"})


def main() -> None:
    host, port = os.getenv("HOST", "127.0.0.1"), int(os.getenv("PORT", "8080"))
    LOG.info("server_started host=%s port=%s", host, port)
    make_server(host, port, application).serve_forever()


if __name__ == "__main__":
    main()
