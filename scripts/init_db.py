from __future__ import annotations

import argparse
import os
from pathlib import Path

import psycopg
from langchain_cockroachdb import CockroachDBEngine, CockroachDBVectorStore
from langchain_cockroachdb.indexes import CSPANNIndex, DistanceStrategy

from recallops.providers import FastEmbedAdapter, _cockroach_url

SYNTHETIC_INCIDENT_ID = "11111111-1111-4111-8111-111111111111"
SYNTHETIC_EVENT_ID = "44444444-4444-4444-8444-444444444444"
SYNTHETIC_MEMORIES = (
    (
        "22222222-2222-4222-8222-222222222222",
        "Reuse an existing action receipt after a retry; never repeat mitigation.",
        "synthetic-runbook/duplicate-requests",
        2,
    ),
    (
        "33333333-3333-4333-8333-333333333333",
        "A saturated synthetic worker pool can raise checkout latency and 503 responses.",
        "synthetic-incident/INC-017",
        1,
    ),
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-synthetic", action="store_true")
    args = parser.parse_args()
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("configuration_required: DATABASE_URL")
    pg_url = url.replace("cockroachdb+psycopg://", "postgresql://", 1)
    statements = Path("schema.sql").read_text().split(";")
    with psycopg.connect(pg_url) as connection, connection.cursor() as cursor:
        for statement in statements:
            if statement.strip():
                cursor.execute(statement)
    engine = CockroachDBEngine.from_connection_string(_cockroach_url(url))
    engine.init_vectorstore_table("memory_chunks", 384)
    store = CockroachDBVectorStore(engine, FastEmbedAdapter(), "memory_chunks", distance_strategy=DistanceStrategy.EUCLIDEAN)
    if args.seed_synthetic:
        with psycopg.connect(pg_url) as connection, connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO incidents (incident_id, service, severity) VALUES (%s, 'checkout', 'SEV-1') "
                "ON CONFLICT (incident_id) DO UPDATE SET service=excluded.service, severity=excluded.severity",
                (SYNTHETIC_INCIDENT_ID,),
            )
            cursor.execute(
                "INSERT INTO incident_events (event_id, incident_id, event_text) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (SYNTHETIC_EVENT_ID, SYNTHETIC_INCIDENT_ID, "Synthetic checkout duplicate 503 latency incident."),
            )
        ids = [memory[0] for memory in SYNTHETIC_MEMORIES]
        store.delete(ids)
        store.add_texts(
            [memory[1] for memory in SYNTHETIC_MEMORIES],
            [
                {
                    "incident_id": SYNTHETIC_INCIDENT_ID,
                    "service": "checkout",
                    "severity": "SEV-1",
                    "observed_at": "2026-01-01T00:00:00+00:00",
                    "observed_at_epoch": 1767225600,
                    "valid_until": "2030-01-01T00:00:00+00:00",
                    "valid_until_epoch": 1893456000,
                    "source": memory[2],
                    "version": memory[3],
                }
                for memory in SYNTHETIC_MEMORIES
            ],
            ids,
        )
    store.apply_vector_index(CSPANNIndex(distance_strategy=DistanceStrategy.EUCLIDEAN, name="memory_chunks_cspann_idx"))
    suffix = f"; synthetic incident {SYNTHETIC_INCIDENT_ID}" if args.seed_synthetic else ""
    print(f"initialized CockroachDB schema and L2 C-SPANN index{suffix}")


if __name__ == "__main__":
    main()
