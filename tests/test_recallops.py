from __future__ import annotations

import asyncio
import io
import json
import os
import threading
import unittest
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from importlib.resources import files
from pathlib import Path
from unittest.mock import patch

from recallops.core import ConfigurationRequired, DemoStore, InjectedFailure, RecallOps
from recallops.http import PUBLIC_DEMO_EVENT, application
from recallops.lambda_handler import handler
from recallops.providers import CockroachStore, CockroachVectorTool, FastEmbedAdapter, ManagedMCPMemoryAuditor, _cockroach_url


def wsgi(method: str, path: str, payload: dict | None = None, query: str = "", raw: bytes | None = None, content_length: str | None = None):
    raw = json.dumps(payload or {}).encode() if raw is None else raw
    captured = {}

    def start(status, headers):
        captured.update(status=status, headers=dict(headers))

    body = b"".join(application({"REQUEST_METHOD": method, "PATH_INFO": path, "QUERY_STRING": query, "CONTENT_LENGTH": content_length if content_length is not None else str(len(raw)), "wsgi.input": io.BytesIO(raw)}, start))
    return int(captured["status"].split()[0]), captured["headers"], json.loads(body) if captured["headers"]["Content-Type"].startswith("application/json") else body.decode()


class WorkflowTests(unittest.TestCase):
    def test_failure_resume_and_exactly_once_receipt(self):
        app = RecallOps()
        run = app.start("checkout duplicate 503 latency")
        self.assertEqual(run["status"], "approval_required")
        approved = app.approve(run["run_id"])
        self.assertEqual(approved["status"], "approved")
        self.assertEqual(app.approve(run["run_id"])["status"], "approved")
        with self.assertRaises(InjectedFailure):
            app.execute(run["run_id"], True)
        resumed = app.execute(run["run_id"], False)
        self.assertEqual(resumed["status"], "complete")
        self.assertEqual(resumed["receipt"]["execution_count"], 1)
        self.assertEqual(len(app.store.receipts), 1)
        self.assertEqual(app.store.search_count, 1)
        self.assertEqual([row["event"] for row in resumed["audit"]].count("receipt_committed"), 1)
        audit_count = len(resumed["audit"])
        self.assertEqual(app.execute(run["run_id"], False)["status"], "complete")
        self.assertEqual(len(app.store.get(run["run_id"])["audit"]), audit_count)

    def test_concurrent_idempotency_key_has_one_receipt(self):
        store = DemoStore()
        state = store.create_run("event", "checkout", "SEV-1")
        threads = [threading.Thread(target=store.claim_action, args=(state,)) for _ in range(20)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(len(store.receipts), 1)
        self.assertEqual(next(iter(store.receipts.values()))["execution_count"], 1)

    def test_scope_filter_excludes_other_service(self):
        store = DemoStore()
        self.assertEqual(store.search("duplicate", "billing", "SEV-1"), [])

    def test_scope_filter_excludes_expired_memory(self):
        store = DemoStore()
        store.memories[0]["valid_until"] = "2000-01-01T00:00:00Z"
        results = store.search("duplicate", "checkout", "SEV-1")
        self.assertNotIn("mem-duplicate-v2", {result["id"] for result in results})

    def test_vector_query_contains_time_scope_and_provenance(self):
        class VectorStore:
            def __init__(self):
                self.filter = None

            def similarity_search(self, query, k, filter):
                self.filter = filter
                metadata = {"source": "runbook", "version": 3, "observed_at": "2026-01-01T00:00:00Z", "valid_until": "2030-01-01T00:00:00Z"}
                return [type("Doc", (), {"page_content": "safe", "metadata": metadata})()]

        tool = CockroachVectorTool.__new__(CockroachVectorTool)
        tool.store = VectorStore()
        result = tool.search("latency", "incident", "checkout", "SEV-1", 1786233600)
        self.assertIn({"observed_at_epoch": {"$lte": 1786233600}}, tool.store.filter["$and"])
        self.assertIn({"valid_until_epoch": {"$gt": 1786233600}}, tool.store.filter["$and"])
        self.assertEqual(result[0]["valid_until"], "2030-01-01T00:00:00Z")

    def test_vector_write_requires_expiry(self):
        tool = CockroachVectorTool.__new__(CockroachVectorTool)
        with self.assertRaisesRegex(ValueError, "missing scoped memory metadata"):
            tool.write("unsafe", {"incident_id": "i", "service": "s", "severity": "SEV-1", "observed_at": "2026-01-01T00:00:00Z", "source": "x", "version": 1}, "m")


class SinkAndConfigurationTests(unittest.TestCase):
    def test_real_wsgi_json_preserves_adversarial_payload(self):
        payload = "<img src=x onerror=globalThis.pwned=1> x'; DROP TABLE runs; -- 雪💥"
        status, headers, body = wsgi("POST", "/api/runs", {"event_text": payload})
        self.assertEqual(status, 201)
        self.assertEqual(body["event_text"], payload)
        self.assertIn("nosniff", headers["X-Content-Type-Options"])

    def test_real_wsgi_preserves_full_adversarial_corpus(self):
        corpus = json.loads(Path("tests/adversarial-corpus.json").read_text())
        for case in corpus:
            with self.subTest(payload_id=case["payload_id"]):
                status, _, body = wsgi("POST", "/api/runs", {"event_text": case["payload"]})
                self.assertEqual(status, 201)
                self.assertEqual(body["event_text"], case["payload"])

    def test_browser_sink_uses_text_content_not_html(self):
        source = files("recallops").joinpath("ui.js").read_text()
        self.assertIn("output.textContent", source)
        self.assertNotIn("output.innerHTML", source)

    def test_provider_missing_configuration_is_explicit(self):
        names = ("DATABASE_URL", "COCKROACH_MCP_API_KEY", "COCKROACH_MCP_CLUSTER_ID")
        old = {name: os.environ.pop(name, None) for name in names}
        try:
            with self.assertRaises(ConfigurationRequired):
                CockroachVectorTool()
            with self.assertRaises(ConfigurationRequired):
                ManagedMCPMemoryAuditor()
        finally:
            for name, value in old.items():
                if value is not None:
                    os.environ[name] = value

    def test_provider_http_never_fakes_success(self):
        previous = os.environ.get("RECALLOPS_MODE")
        os.environ["RECALLOPS_MODE"] = "provider"
        try:
            status, _, body = wsgi("POST", "/api/runs", {"event_text": "test"})
            self.assertEqual(status, 503)
            self.assertEqual(body["error"], "configuration_required")
        finally:
            if previous is None:
                os.environ.pop("RECALLOPS_MODE", None)
            else:
                os.environ["RECALLOPS_MODE"] = previous

    def test_http_rejects_oversized_short_and_invalid_lengths(self):
        self.assertEqual(wsgi("POST", "/api/runs", raw=b"{}", content_length="16385")[0], 413)
        self.assertEqual(wsgi("POST", "/api/runs", raw=b"{}", content_length="3")[0], 400)
        self.assertEqual(wsgi("POST", "/api/runs", raw=b"{}", content_length="wat")[0], 400)
        with patch.dict(os.environ, {"RECALLOPS_MODE": "provider"}):
            self.assertEqual(wsgi("POST", "/api/runs", raw=b"{}", content_length="16385")[0], 413)

    def test_http_maps_missing_run_to_404(self):
        self.assertEqual(wsgi("GET", "/api/runs/not-a-run")[0], 404)

    def test_http_ignores_forged_scope_receipt_and_checkpoint(self):
        status, _, body = wsgi("POST", "/api/runs", {"event_text": "safe", "service": "admin", "approved": True, "receipt": {"execution_count": 99}, "status": "complete"})
        self.assertEqual(status, 201)
        self.assertEqual(body["service"], "checkout")
        self.assertFalse(body["approved"])
        self.assertNotIn("receipt", body)
        self.assertEqual(body["status"], "approval_required")

    def test_public_demo_accepts_only_fixed_synthetic_incident(self):
        with patch.dict(os.environ, {"RECALLOPS_PUBLIC_DEMO": "1"}):
            self.assertEqual(wsgi("POST", "/api/runs", {"event_text": PUBLIC_DEMO_EVENT})[0], 201)
            status, _, body = wsgi("POST", "/api/runs", {"event_text": "production://restart-everything"})
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "public_demo_uses_fixed_synthetic_incident")

    def test_lambda_handler_import_and_health(self):
        result = handler({"rawPath": "/health", "requestContext": {"http": {"method": "GET", "path": "/health"}}}, None)
        self.assertEqual(result["statusCode"], 200)

    def test_lambda_handler_rejects_invalid_or_oversized_encoded_body(self):
        event = {"body": "%%%", "isBase64Encoded": True, "requestContext": {"http": {"method": "POST", "path": "/api/runs"}}}
        self.assertEqual(handler(event, None)["statusCode"], 400)
        event["body"] = "x" * 32_769
        event["isBase64Encoded"] = False
        self.assertEqual(handler(event, None)["statusCode"], 413)


class ProviderInvariantTests(unittest.TestCase):
    def test_fastembed_adapter_exposes_async_contract(self):
        class Vector:
            def tolist(self):
                return [1.0, 2.0]

        adapter = FastEmbedAdapter.__new__(FastEmbedAdapter)
        adapter.model = type("Model", (), {"embed": lambda self, texts: [Vector() for _ in texts]})()
        self.assertEqual(asyncio.run(adapter.aembed_documents(["a", "b"])), [[1.0, 2.0], [1.0, 2.0]])
        self.assertEqual(asyncio.run(adapter.aembed_query("a")), [1.0, 2.0])

    def test_provider_normalizes_official_postgresql_url_for_async_engine(self):
        self.assertEqual(
            _cockroach_url("postgresql://user@host/defaultdb"),
            "cockroachdb+psycopg://user@host/defaultdb",
        )

    def test_checkpoint_retries_40001_and_complete_never_downgrades(self):
        class SerializationFailure(Exception):
            sqlstate = "40001"

        class FakeDatabase:
            def __init__(self):
                self.state = {"run_id": "run", "status": "running"}
                self.lock = threading.RLock()
                self.fail_once = True

            def connect(self):
                database = self

                class Connection:
                    def __enter__(self):
                        database.lock.acquire()
                        return self

                    def __exit__(self, exc_type, exc, traceback):
                        database.lock.release()

                    def cursor(self):
                        return Cursor()

                class Cursor:
                    rowcount = 1

                    def __enter__(self):
                        return self

                    def __exit__(self, *args):
                        pass

                    def execute(self, query, params):
                        if query.startswith("SELECT state"):
                            self.row = (database.state.copy(),)
                        elif query.startswith("UPDATE agent_runs"):
                            if database.fail_once:
                                database.fail_once = False
                                raise SerializationFailure()
                            database.state = json.loads(params[0])

                    def fetchone(self):
                        return self.row

                return Connection()

        database = FakeDatabase()
        store = CockroachStore.__new__(CockroachStore)
        store._connect = database.connect
        errors = []

        def checkpoint(status):
            try:
                store.checkpoint({"run_id": "run"}, status)
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=checkpoint, args=(status,)) for status in ("complete", "failed_after_receipt")]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])
        self.assertEqual(database.state["status"], "complete")

    def test_mcp_uses_initialized_structured_session_and_fixed_queries(self):
        calls = []

        class SQLTool:
            name = "select_query"
            inputSchema = {"type": "object", "properties": {"cluster_id": {}, "database": {}, "query": {}}}

        class SchemaTool:
            name = "get_table_schema"
            inputSchema = {"type": "object", "properties": {"cluster_id": {}, "database": {}, "schema": {}, "table": {}}}

        class Result:
            isError = False
            structuredContent = {"rows": []}
            content = []

        class Session:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

            async def initialize(self):
                calls.append("initialize")

            async def list_tools(self):
                calls.append("list_tools")
                return type("Tools", (), {"tools": [SQLTool(), SchemaTool()]})()

            async def call_tool(self, name, arguments):
                calls.append({"name": name, **arguments})
                return Result()

        @asynccontextmanager
        async def transport(*args, **kwargs):
            yield object(), object(), lambda: "session"

        auditor = ManagedMCPMemoryAuditor.__new__(ManagedMCPMemoryAuditor)
        auditor.url, auditor.key, auditor.cluster_id = "https://mcp.invalid", "secret", "cluster"
        auditor.database, auditor.sql_tool = "defaultdb", "select_query"
        auditor.schema_tool = "get_table_schema"
        with patch("recallops.providers.streamable_http_client", transport), patch("recallops.providers.ClientSession", lambda *args: Session()):
            results = auditor.audit_run("11111111-1111-4111-8111-111111111111")
        self.assertEqual(calls[:2], ["initialize", "list_tools"])
        self.assertEqual([call["name"] for call in calls[2:5]], ["get_table_schema"] * 3)
        queries = [call["query"] for call in calls[5:]]
        self.assertTrue(all("SELECT *" not in query.upper() for query in queries))
        self.assertTrue(all(call["database"] == "defaultdb" for call in calls[2:]))
        self.assertEqual(len(results), 6)

        with self.assertRaises(ValueError):
            auditor.audit_run("x' OR true --")

    def test_mcp_tool_error_is_not_reported_as_success(self):
        class SQLTool:
            name = "select_query"
            inputSchema = {"type": "object", "properties": {"cluster_id": {}, "database": {}, "query": {}}}

        class SchemaTool:
            name = "get_table_schema"
            inputSchema = {"type": "object", "properties": {"cluster_id": {}, "database": {}, "schema": {}, "table": {}}}

        class Session:
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
            async def initialize(self): pass
            async def list_tools(self): return type("Tools", (), {"tools": [SQLTool(), SchemaTool()]})()
            async def call_tool(self, name, arguments): return type("Result", (), {"isError": True, "structuredContent": None, "content": []})()

        @asynccontextmanager
        async def transport(*args, **kwargs):
            yield object(), object(), lambda: "session"

        auditor = ManagedMCPMemoryAuditor.__new__(ManagedMCPMemoryAuditor)
        auditor.url, auditor.key, auditor.cluster_id = "https://mcp.invalid", "secret", "cluster"
        auditor.database, auditor.sql_tool = "defaultdb", "select_query"
        auditor.schema_tool = "get_table_schema"
        with patch("recallops.providers.streamable_http_client", transport), patch("recallops.providers.ClientSession", lambda *args: Session()):
            with self.assertRaises(RuntimeError):
                auditor.audit_run("11111111-1111-4111-8111-111111111111")


if __name__ == "__main__":
    unittest.main()
