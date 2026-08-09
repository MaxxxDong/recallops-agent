from __future__ import annotations

import re
import threading
import uuid
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, TypedDict


class ConfigurationRequired(RuntimeError):
    pass


class ApprovalRequired(RuntimeError):
    pass


class InjectedFailure(RuntimeError):
    pass


class RunState(TypedDict, total=False):
    run_id: str
    incident_id: str
    event_text: str
    service: str
    severity: str
    approved: bool
    fail_once: bool
    normalized: str
    memories: list[dict[str, Any]]
    hypothesis: str
    status: str
    action: str
    receipt: dict[str, Any]
    verification: str
    handoff: str
    error: str


def now() -> str:
    return datetime.now(UTC).isoformat()


class DemoStore:
    """Volatile synthetic store. It is never presented as CockroachDB."""

    def __init__(self) -> None:
        from langgraph.checkpoint.memory import InMemorySaver

        self._lock = threading.RLock()
        self.graph_checkpointer = InMemorySaver()
        self.runs: dict[str, RunState] = {}
        self.receipts: dict[str, dict[str, Any]] = {}
        self.audit: list[dict[str, str]] = []
        self.search_count = 0
        self.memories = [
            {
                "id": "mem-duplicate-v2",
                "service": "checkout",
                "severity": "SEV-1",
                "version": 2,
                "source": "synthetic-runbook/duplicate-requests",
                "text": "Reuse an existing action receipt after a retry; never repeat mitigation.",
                "observed_at": "2026-01-01T00:00:00Z",
                "valid_until": "2030-01-01T00:00:00Z",
            },
            {
                "id": "mem-pool-v1",
                "service": "checkout",
                "severity": "SEV-1",
                "version": 1,
                "source": "synthetic-incident/INC-017",
                "text": "A saturated synthetic worker pool can raise checkout latency and 503 responses.",
                "observed_at": "2026-01-01T00:00:00Z",
                "valid_until": "2030-01-01T00:00:00Z",
            },
        ]

    def create_run(self, event_text: str, service: str, severity: str) -> RunState:
        run_id = str(uuid.uuid4())
        state: RunState = {
            "run_id": run_id,
            "incident_id": "INC-DEMO-001",
            "event_text": event_text,
            "service": service,
            "severity": severity,
            "approved": False,
            "fail_once": False,
        }
        with self._lock:
            self.runs[run_id] = state
        return deepcopy(state)

    def search(self, query: str, service: str, severity: str, incident_id: str | None = None) -> list[dict[str, Any]]:
        words = set(re.findall(r"[a-z0-9]+", query.lower()))
        as_of = datetime.now(UTC)
        with self._lock:
            self.search_count += 1
        scoped = [
            memory
            for memory in self.memories
            if memory["service"] == service
            and memory["severity"] == severity
            and datetime.fromisoformat(memory["observed_at"].replace("Z", "+00:00")) <= as_of
            < datetime.fromisoformat(memory["valid_until"].replace("Z", "+00:00"))
        ]
        return sorted(scoped, key=lambda m: -len(words & set(re.findall(r"[a-z0-9]+", m["text"].lower()))))[:3]

    def checkpoint(self, state: RunState, status: str) -> None:
        with self._lock:
            state["status"] = status
            self.runs[state["run_id"]] = deepcopy(state)
            self.audit.append({"at": now(), "run_id": state["run_id"], "event": status})

    def record_approval(self, run_id: str) -> None:
        with self._lock:
            if run_id not in self.runs:
                raise KeyError("run_not_found")

    def claim_action(self, state: RunState) -> dict[str, Any]:
        key = f"{state['run_id']}:restart_synthetic_worker"
        with self._lock:
            receipt = self.receipts.setdefault(
                key,
                {
                    "idempotency_key": key,
                    "action": "restart_synthetic_worker",
                    "target": "simulator://checkout/worker-1",
                    "created_at": now(),
                    "execution_count": 1,
                },
            )
            return deepcopy(receipt)

    def get(self, run_id: str) -> dict[str, Any]:
        with self._lock:
            result = deepcopy(self.runs[run_id])
            result["audit"] = [a for a in self.audit if a["run_id"] == run_id]
            return result


class RecallOps:
    def __init__(self, store: Any | None = None) -> None:
        self.store = store or DemoStore()

    def _graph(self):
        try:
            from langgraph.graph import END, START, StateGraph
        except ImportError as exc:
            raise ConfigurationRequired("install project dependencies") from exc

        graph = StateGraph(RunState)
        graph.add_node("normalize", self._normalize)
        graph.add_node("retrieve", self._retrieve)
        graph.add_node("hypothesize", self._hypothesize)
        graph.add_node("approval", self._approval)
        graph.add_node("simulator", self._simulator)
        graph.add_node("verify", self._verify)
        graph.add_node("handoff", self._handoff)
        graph.add_edge(START, "normalize")
        graph.add_edge("normalize", "retrieve")
        graph.add_edge("retrieve", "hypothesize")
        graph.add_edge("hypothesize", "approval")
        graph.add_edge("approval", "simulator")
        graph.add_edge("simulator", "verify")
        graph.add_edge("verify", "handoff")
        graph.add_edge("handoff", END)
        return graph.compile(checkpointer=self.store.graph_checkpointer)

    @staticmethod
    def _config(run_id: str) -> dict[str, dict[str, str]]:
        return {"configurable": {"thread_id": run_id}}

    def _invoke(self, state: RunState) -> RunState:
        result = self._graph().invoke(state, config=self._config(state["run_id"]))
        return {key: value for key, value in result.items() if not key.startswith("__")}

    def _resume(self, run_id: str, value: Any) -> RunState:
        from langgraph.types import Command

        result = self._graph().invoke(Command(resume=value), config=self._config(run_id))
        return {key: item for key, item in result.items() if not key.startswith("__")}

    @staticmethod
    def _normalize(state: RunState) -> dict[str, str]:
        return {"normalized": " ".join(state["event_text"].split())[:4000], "status": "normalized"}

    def _retrieve(self, state: RunState) -> dict[str, Any]:
        return {"memories": self.store.search(state["normalized"], state["service"], state["severity"], state["incident_id"]), "status": "retrieved"}

    @staticmethod
    def _hypothesize(state: RunState) -> dict[str, str]:
        return {"hypothesis": "Synthetic checkout worker saturation is consistent with the scoped evidence.", "status": "approval_required"}

    @staticmethod
    def _approval(state: RunState) -> dict[str, Any]:
        from langgraph.types import interrupt

        approved = interrupt({"kind": "approval", "run_id": state["run_id"]})
        if approved is not True:
            raise ApprovalRequired("human approval is required")
        return {"approved": True, "status": "approved"}

    def _simulator(self, state: RunState) -> dict[str, Any]:
        if not state["approved"]:
            raise ApprovalRequired("human approval is required")
        from langgraph.types import interrupt

        fail_once = bool(interrupt({"kind": "execute", "run_id": state["run_id"]}))
        already_failed = self.store.get(state["run_id"])["status"] == "failed_after_receipt"
        receipt = self.store.claim_action(state)
        if not already_failed:
            self.store.checkpoint({**state, "receipt": receipt}, "receipt_committed")
        if fail_once and not already_failed:
            raise InjectedFailure("injected failure after durable receipt")
        return {"action": "restart_synthetic_worker", "receipt": receipt, "status": "executed"}

    @staticmethod
    def _verify(state: RunState) -> dict[str, str]:
        return {"verification": "Simulator latency recovered; no second action was executed.", "status": "verified"}

    @staticmethod
    def _handoff(state: RunState) -> dict[str, str]:
        return {"handoff": "Checkout recovered after approved synthetic worker restart. Receipt is reusable on retry.", "status": "complete"}

    def start(self, event_text: str, service: str = "checkout", severity: str = "SEV-1") -> dict[str, Any]:
        from opentelemetry import trace

        with trace.get_tracer("recallops").start_as_current_span("agent.start") as span:
            state = self.store.create_run(event_text, service, severity)
            span.set_attribute("recallops.run_id", state["run_id"])
            result = self._invoke(state)
            self.store.checkpoint(result, result["status"])
            return self.store.get(result["run_id"])

    def approve(self, run_id: str) -> dict[str, Any]:
        current = self.store.get(run_id)
        if current["status"] != "approval_required":
            return current
        result = self._resume(run_id, True)
        self.store.record_approval(run_id)
        self.store.checkpoint(result, result["status"])
        return self.store.get(run_id)

    def execute(self, run_id: str, fail_once: bool) -> dict[str, Any]:
        from opentelemetry import trace

        with trace.get_tracer("recallops").start_as_current_span("agent.execute") as span:
            span.set_attribute("recallops.run_id", run_id)
            span.set_attribute("recallops.inject_failure", fail_once)
            current = self.store.get(run_id)
            if current["status"] == "complete":
                return current
            if current["status"] not in {"approved", "failed_after_receipt"}:
                raise ValueError("run is not ready to execute")
            try:
                result = self._resume(run_id, fail_once)
            except InjectedFailure:
                failed = self.store.get(run_id)
                failed.pop("audit", None)
                failed["error"] = "injected_failure"
                self.store.checkpoint(failed, "failed_after_receipt")
                raise
            result.pop("error", None)
            self.store.checkpoint(result, result["status"])
            return self.store.get(run_id)
