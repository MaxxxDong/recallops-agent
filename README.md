# RecallOps

RecallOps is a resumable incident-memory agent for on-call teams. It combines scoped semantic recall with durable checkpoints, human approval, exactly-once synthetic action receipts, and a read-only CockroachDB Managed MCP audit path. The local demo is deliberately volatile and synthetic; CockroachDB remains the only supported persistent backend.

## Quick start

Requires Python 3.12.

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e .
RECALLOPS_MODE=demo .venv/bin/python -m recallops.http
# open http://127.0.0.1:8080
```

Click **Create incident**, **Approve**, **Execute with one failure**, and **Resume**. The UI shows scoped recall, the durable receipt created before the injected failure, reuse of that receipt after recovery, the handoff, and the audit trail. Demo mode never claims a provider call and stores nothing after the process exits.

Public fixed-scenario demo: https://i5lvohbwb6newxfvc4xxiky6im0sojdz.lambda-url.us-east-1.on.aws/

Provider mode is opt-in. Copy `.env.example`, supply environment variables through your deployment secret mechanism, and set `RECALLOPS_MODE=provider`. Missing configuration returns HTTP `503` with `{"error":"configuration_required"}`; there is no mock-success fallback.

To create the schema, C-SPANN index, and two explicitly synthetic demo memories, run `PYTHONPATH=src python scripts/init_db.py --seed-synthetic`, then set `RECALLOPS_INCIDENT_ID=11111111-1111-4111-8111-111111111111` for the provider walkthrough. Managed MCP auditing uses the currently offered `get_table_schema` and `select_query` tools; it is read-only and rejects non-UUID run ids.

## Project evidence

- [Architecture and state flow](docs/technical-overview.md#architecture)
- [CockroachDB tools and AWS Lambda](docs/technical-overview.md#provider-tools-and-lambda)
- [Demo walkthrough](docs/technical-overview.md#demo)
- [Validation commands and evidence](docs/technical-overview.md#validation)
- [Privacy and threat model](docs/security/trust-boundary.md)
- [Pre-existing work and third-party disclosure](docs/technical-overview.md#pre-existing-work-and-third-party-disclosure)
- [Dependency license inventory](docs/dependency-licenses.md)
- [Submission draft](docs/submission-draft.md)
- [Final demo video](videos/recallops-demo/renders/recallops-final.mp4)

## Scope

All incident data and actions are synthetic. The only executable action is the allowlisted `restart_synthetic_worker` simulator and it always requires approval. RecallOps does not connect to production systems, perform real remediation, or write through Managed MCP. The anonymous AWS judge demo accepts only the fixed synthetic incident, rejects bodies over its limit, contains no CockroachDB credentials, and is separate from provider verification.
