# RecallOps technical overview

## Architecture

One Python 3.12 application serves both local HTTP and the Lambda Function URL event shape. Both enter `recallops.http.application`; `lambda_handler.handler` only translates the Lambda event to WSGI, so business logic is not duplicated.

The LangGraph flow is `normalize → retrieve → hypothesize → approval interrupt → execution interrupt → allowlisted simulator → verify → handoff`. Approval and execution use LangGraph `Command(resume=...)` with the same `thread_id`; they do not submit state to `START` again. The simulator writes/claims the action receipt before the injected failure. A retry resumes the pending simulator task, reuses the same idempotency key and receipt, verifies recovery, and creates the handoff.

Demo mode is a volatile, process-local synthetic fixture for a credential-free walkthrough. It is visibly labeled and is not a persistence provider. Provider deployments support CockroachDB as the only durable store for incidents, events, memories, runs, checkpoints, approvals, receipts, and audit records.

Set `RECALLOPS_OTEL_CONSOLE=1` to emit OpenTelemetry spans locally. Span attributes contain only run ids, node/action categories, and failure-fixture state; incident text and credentials are excluded. JSON application logs likewise use stable categories rather than request bodies.

## Provider tools and Lambda

### Tool 1: C-SPANN vector memory

`CockroachVectorTool` uses `langchain-cockroachdb==0.2.1`, `FastEmbed==0.8.0`, and `BAAI/bge-small-en-v1.5`. It explicitly selects `DistanceStrategy.EUCLIDEAN`, matching the probed 0.2.1 C-SPANN L2 index behavior. Writes require incident, service, severity, observed time, expiry time, source, and version metadata. Human-readable ISO timestamps are retained as provenance; numeric epoch companions are used for range filtering because the frozen vector-store version casts JSON range operands to numeric. Searches require structured incident/service/severity/as-of scope, exclude expired evidence, and return source, version, `observed_at`, and `valid_until`. No hybrid-search claim is made.

Initialize an authorized target explicitly with `PYTHONPATH=src python scripts/init_db.py`; add `--seed-synthetic` to install the two repeatable demo memories and fixed synthetic incident. It fails with `configuration_required` when `DATABASE_URL` is absent. This command is never run by the local demo or default tests.

### Tool 2: Managed MCP Memory Auditor

`ManagedMCPMemoryAuditor` uses the official Python MCP SDK Streamable HTTP transport and `ClientSession`, initializes the session, and validates structured `tools/list`. The current managed service blocks `information_schema`, so the auditor uses the offered read-only `get_table_schema` tool for each allowlisted table and `select_query` for explicit columns from `agent_runs`, `run_checkpoints`, and `action_receipts`. A run id must parse as a UUID before it is inserted into the fixed query template. It rejects MCP tool errors and never calls a write tool. Tool names default to the verified `get_table_schema` and `select_query` values but remain explicit environment settings.

### AWS Lambda

The ARM64 Docker recipe uses the AWS Python 3.12 Lambda base image and the same WSGI business entry point as local HTTP. It installs the frozen `requirements-lambda-demo.txt` profile and fixes `RECALLOPS_MODE=demo`, so the preview image contains no database or MCP secret. The verified image digest is recorded in `docs/security/evidence/aws-lambda.log`; the existing Lambda keeps an `AWS_IAM` Function URL. A future provider deployment requires a separately approved secret mechanism and cost review.

## Demo

1. Start the local app in `RECALLOPS_MODE=demo`.
2. Create the synthetic checkout incident. The graph normalizes it, retrieves service/severity-scoped memories, and displays each memory source/version.
3. Approve the proposed synthetic restart.
4. Execute with one injected failure. The API returns `503 injected_failure` after a receipt is committed.
5. Resume. The same idempotency key returns the original receipt (`execution_count=1`), then verification and handoff complete.
6. Inspect the audit array for `approval_required`, `approved`, `receipt_committed`, `failed_after_receipt`, and `complete`.

## Validation

From the repository root with dependencies installed:

```bash
PYTHONPATH=src python -m unittest tests.test_recallops -v
PYTHONPATH=src python -m compileall -q src tests
PYTHONPATH=src python -c "from recallops.lambda_handler import handler; assert handler({'rawPath':'/health','requestContext':{'http':{'method':'GET','path':'/health'}}},None)['statusCode']==200"
```

Security RED deliberately runs only the vulnerable test fixture and must exit nonzero; GREEN runs the production suite and must exit zero:

```bash
PYTHONPATH=src python -m unittest tests.test_security_red -v  # expected exit 1
PYTHONPATH=src python -m unittest tests.test_recallops -v     # expected exit 0
```

Auditable outputs are under `docs/security/evidence/`. Browser artifacts are under `output/playwright/` and intentionally ignored because they are run-local corroboration; the textual browser verdict is versioned.

Real provider verification is opt-in and reads only environment variables. The 2026-08-09 synthetic run exercised C-SPANN recall, LangGraph checkpoint/resume, exactly-once receipt, six Managed MCP read batches, ECR, and a four-step Lambda demo flow. See `real-provider.log` and `aws-lambda.log`; no production data, action, anonymous URL, or cloud-stored credential was used.

## Pre-existing work and third-party disclosure

RecallOps was created during the competition submission period. No product code, UI, domain schema, prompts, or data were copied from earlier entries. Design patterns were studied from the author's earlier RegImpact (transactional audit/checkpoint), ThinkTrace EDU (scoped versioned evidence), and ChangeGuard (deterministic receipts and adversarial fixtures) projects.

Runtime dependencies are third-party open source: LangChain CockroachDB (Apache-2.0), LangGraph (MIT), OpenTelemetry Python (Apache-2.0), FastEmbed (repository Apache-2.0; wheel classifier caveat documented), and BGE small English v1.5 model (MIT). See the [license inventory](dependency-licenses.md).
