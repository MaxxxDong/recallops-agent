from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from .core import ConfigurationRequired, RunState

ALLOWED_AUDIT_COLUMNS = {
    "agent_runs": ("run_id", "incident_id", "state", "created_at", "updated_at"),
    "run_checkpoints": ("checkpoint_id", "run_id", "status", "state", "created_at"),
    "action_receipts": ("idempotency_key", "run_id", "receipt", "created_at"),
}


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ConfigurationRequired(f"{name} is required")
    return value


def _cockroach_url(value: str) -> str:
    for scheme in ("postgresql+psycopg://", "postgresql://", "postgres://", "cockroachdb://"):
        if value.startswith(scheme):
            return value.replace(scheme, "cockroachdb+psycopg://", 1)
    return value


class FastEmbedAdapter:
    def __init__(self) -> None:
        from fastembed import TextEmbedding

        self.model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self.model.embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        return await asyncio.to_thread(self.embed_documents, texts)

    async def aembed_query(self, text: str) -> list[float]:
        return await asyncio.to_thread(self.embed_query, text)


class CockroachVectorTool:
    """C-SPANN-backed vector write/search with mandatory incident scope."""

    def __init__(self) -> None:
        connection = _cockroach_url(_required("DATABASE_URL"))
        try:
            from langchain_cockroachdb import CockroachDBEngine, CockroachDBVectorStore
            from langchain_cockroachdb.indexes import DistanceStrategy
        except ImportError as exc:
            raise ConfigurationRequired("install project dependencies") from exc
        engine = CockroachDBEngine.from_connection_string(connection)
        self.store = CockroachDBVectorStore(
            engine,
            FastEmbedAdapter(),
            "memory_chunks",
            distance_strategy=DistanceStrategy.EUCLIDEAN,
        )

    def write(self, text: str, metadata: dict[str, Any], memory_id: str) -> str:
        required = {
            "incident_id",
            "service",
            "severity",
            "observed_at",
            "observed_at_epoch",
            "valid_until",
            "valid_until_epoch",
            "source",
            "version",
        }
        if required - metadata.keys():
            raise ValueError("missing scoped memory metadata")
        return self.store.add_texts([text], [metadata], [memory_id])[0]

    def search(self, query: str, incident_id: str, service: str, severity: str, as_of_epoch: float) -> list[dict[str, Any]]:
        filters = {
            "$and": [
                {"incident_id": {"$eq": incident_id}},
                {"service": {"$eq": service}},
                {"severity": {"$eq": severity}},
                {"observed_at_epoch": {"$lte": as_of_epoch}},
                {"valid_until_epoch": {"$gt": as_of_epoch}},
            ]
        }
        docs = self.store.similarity_search(query, k=5, filter=filters)
        return [
            {
                "text": d.page_content,
                "source": d.metadata["source"],
                "version": d.metadata["version"],
                "observed_at": d.metadata["observed_at"],
                "valid_until": d.metadata["valid_until"],
            }
            for d in docs
        ]


class ManagedMCPMemoryAuditor:
    """Read-only MCP auditor. It never claims or performs an MCP write."""

    def __init__(self) -> None:
        self.url = os.getenv("COCKROACH_MCP_URL", "https://cockroachlabs.cloud/mcp")
        self.key = _required("COCKROACH_MCP_API_KEY")
        self.cluster_id = _required("COCKROACH_MCP_CLUSTER_ID")
        self.database = os.getenv("COCKROACH_MCP_DATABASE", "defaultdb")
        self.sql_tool = os.getenv("COCKROACH_MCP_SQL_TOOL", "select_query")
        self.schema_tool = os.getenv("COCKROACH_MCP_SCHEMA_TOOL", "get_table_schema")

    def audit_run(self, run_id: str) -> list[dict[str, Any]]:
        return asyncio.run(self._audit_run(str(uuid.UUID(run_id))))

    async def _audit_run(self, run_id: str) -> list[dict[str, Any]]:
        headers = {"Authorization": f"Bearer {self.key}", "mcp-cluster-id": self.cluster_id}
        async with httpx.AsyncClient(headers=headers, timeout=10) as client:
            async with streamable_http_client(self.url, http_client=client) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    offered = {tool.name: tool for tool in tools.tools}
                    sql_tool = offered.get(self.sql_tool)
                    schema_tool = offered.get(self.schema_tool)
                    if sql_tool is None or schema_tool is None:
                        raise ConfigurationRequired("configured MCP audit tools are not offered")
                    if not {"database", "query"} <= set(sql_tool.inputSchema.get("properties", ())):
                        raise ConfigurationRequired("configured MCP SQL tool has an unsupported schema")
                    if not {"database", "table"} <= set(schema_tool.inputSchema.get("properties", ())):
                        raise ConfigurationRequired("configured MCP schema tool has an unsupported schema")

                    results = [
                        await self._call_tool(
                            session,
                            self.schema_tool,
                            {"database": self.database, "schema": "public", "table": table},
                        )
                        for table in ALLOWED_AUDIT_COLUMNS
                    ]
                    for table, columns in ALLOWED_AUDIT_COLUMNS.items():
                        query = f"SELECT {', '.join(columns)} FROM {table} WHERE run_id = '{run_id}'::UUID LIMIT 100"
                        results.append(
                            await self._call_tool(
                                session,
                                self.sql_tool,
                                {"database": self.database, "query": query},
                            )
                        )
                    return results

    @staticmethod
    async def _call_tool(session: ClientSession, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        result = await session.call_tool(name, arguments)
        if result.isError:
            raise RuntimeError("managed MCP SQL tool returned an error")
        return result.model_dump(mode="json", by_alias=True) if hasattr(result, "model_dump") else {"structuredContent": result.structuredContent, "content": result.content}


class CockroachStore:
    """CockroachDB-backed run/checkpoint/receipt store for provider mode."""

    def __init__(self) -> None:
        self.url = _cockroach_url(_required("DATABASE_URL"))
        configured_incident = os.getenv("RECALLOPS_INCIDENT_ID")
        self.incident_id = str(uuid.UUID(configured_incident)) if configured_incident else None
        self.vector = CockroachVectorTool()
        from langchain_cockroachdb import CockroachDBSaver

        self._saver_context = CockroachDBSaver.from_conn_string(self.pg_url)
        self.graph_checkpointer = self._saver_context.__enter__()
        self.graph_checkpointer.setup()

    @property
    def pg_url(self) -> str:
        return self.url.replace("cockroachdb+psycopg://", "postgresql://", 1)

    def _connect(self):
        try:
            import psycopg
        except ImportError as exc:
            raise ConfigurationRequired("install project dependencies") from exc
        return psycopg.connect(self.pg_url)

    def _transaction(self, operation):
        for attempt in range(3):
            try:
                with self._connect() as connection, connection.cursor() as cursor:
                    return operation(cursor)
            except Exception as exc:
                if getattr(exc, "sqlstate", None) != "40001" or attempt == 2:
                    raise
                time.sleep(0.01 * (2**attempt))

    def create_run(self, event_text: str, service: str, severity: str) -> RunState:
        run_id = str(uuid.uuid4())
        incident_id = self.incident_id or str(uuid.uuid4())
        state: RunState = {"run_id": run_id, "incident_id": incident_id, "event_text": event_text, "service": service, "severity": severity, "approved": False, "fail_once": False}

        def create(cursor):
            if self.incident_id:
                cursor.execute("SELECT service, severity FROM incidents WHERE incident_id=%s", (incident_id,))
                if cursor.fetchone() != (service, severity):
                    raise ValueError("configured incident scope is missing or mismatched")
            else:
                cursor.execute("INSERT INTO incidents (incident_id, service, severity) VALUES (%s, %s, %s)", (incident_id, service, severity))
            cursor.execute("INSERT INTO incident_events (event_id, incident_id, event_text) VALUES (%s, %s, %s)", (str(uuid.uuid4()), incident_id, event_text))
            cursor.execute("INSERT INTO agent_runs (run_id, incident_id, state) VALUES (%s, %s, %s::JSONB)", (run_id, incident_id, json.dumps(state)))

        self._transaction(create)
        return state

    def search(self, query: str, service: str, severity: str, incident_id: str | None = None) -> list[dict[str, Any]]:
        if not incident_id:
            raise ValueError("incident_id is required")
        return self.vector.search(query, incident_id, service, severity, datetime.now(UTC).timestamp())

    def checkpoint(self, state: RunState, status: str) -> None:
        next_state = deepcopy(state)
        next_state["status"] = status

        def write(cursor):
            cursor.execute("SELECT state FROM agent_runs WHERE run_id=%s FOR UPDATE", (state["run_id"],))
            row = cursor.fetchone()
            if row is None:
                raise KeyError("run_not_found")
            if row[0].get("status") == "complete" and status != "complete":
                return
            cursor.execute("UPDATE agent_runs SET state=%s::JSONB, updated_at=now() WHERE run_id=%s", (json.dumps(next_state), state["run_id"]))
            cursor.execute("INSERT INTO run_checkpoints (checkpoint_id, run_id, status, state) VALUES (%s, %s, %s, %s::JSONB)", (str(uuid.uuid4()), state["run_id"], status, json.dumps(next_state)))
            cursor.execute("INSERT INTO audit_events (audit_id, run_id, event_type) VALUES (%s, %s, %s)", (str(uuid.uuid4()), state["run_id"], status))

        self._transaction(write)

    def record_approval(self, run_id: str) -> None:
        self._transaction(lambda cursor: cursor.execute("INSERT INTO approvals (approval_id, run_id, decision) VALUES (%s, %s, 'approved')", (str(uuid.uuid4()), run_id)))

    def claim_action(self, state: RunState) -> dict[str, Any]:
        key = f"{state['run_id']}:restart_synthetic_worker"
        receipt = {"idempotency_key": key, "run_id": state["run_id"], "action": "restart_synthetic_worker", "target": "simulator://checkout/worker-1", "created_at": datetime.now(UTC).isoformat(), "execution_count": 1}

        def claim(cursor):
            cursor.execute("INSERT INTO action_receipts (idempotency_key, run_id, receipt) VALUES (%s, %s, %s::JSONB) ON CONFLICT (idempotency_key) DO NOTHING", (key, state["run_id"], json.dumps(receipt)))
            cursor.execute("SELECT receipt FROM action_receipts WHERE idempotency_key=%s", (key,))
            return cursor.fetchone()[0]

        return self._transaction(claim)

    def get(self, run_id: str) -> dict[str, Any]:
        def read(cursor):
            cursor.execute("SELECT state FROM agent_runs WHERE run_id=%s", (run_id,))
            row = cursor.fetchone()
            if row is None:
                raise KeyError("run_not_found")
            state = deepcopy(row[0])
            cursor.execute("SELECT created_at, event_type FROM audit_events WHERE run_id=%s ORDER BY created_at", (run_id,))
            state["audit"] = [{"at": at.isoformat(), "run_id": run_id, "event": event} for at, event in cursor.fetchall()]
            return state

        return self._transaction(read)
