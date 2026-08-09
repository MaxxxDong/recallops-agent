# RecallOps — submission record

## One-line summary

RecallOps is a resumable incident agent that uses CockroachDB as durable memory and AWS Lambda as a bounded execution entry point, so an interrupted recovery can resume without duplicating the approved action.

## Product description

Incident automation becomes risky when the automation itself fails. Stateless retries can repeat diagnosis, lose evidence provenance, or execute the same remediation twice. RecallOps models recovery as a persistent state machine. A synthetic incident creates a stable run identity; CockroachDB's Distributed Vector Index retrieves relevant incident memory with source and observation time; Managed MCP supplies a second, read-only audit view; a human must approve the single allowlisted simulator action; and an idempotency key guarantees that retrying the same recovery produces one durable receipt.

The demo deliberately injects one execution failure, resumes the same run, and verifies that the execution count remains one. It uses synthetic data and a simulator target only. It does not connect to production systems or perform real remediation.

## CockroachDB and AWS usage

- CockroachDB persistent memory: incident state, provenance-bearing memory, approval state, idempotency key, and action receipt.
- CockroachDB capability 1: Distributed Vector Index for relevant-memory retrieval.
- CockroachDB capability 2: Managed MCP for an independently auditable, read-only state view.
- AWS service: Lambda runs the packaged demo entry point.
- Deployment boundary: the public Lambda is a no-secret, fixed-scenario demo profile; real provider verification is recorded separately.

## Judge demo

1. Create the synthetic checkout incident.
2. Inspect retrieved memory and provenance.
3. Approve the allowlisted simulator action.
4. Execute with one injected failure.
5. Resume the same run.
6. Retry and verify `execution_count = 1` with the same receipt.

## Submission links

- Public repository: https://github.com/MaxxxDong/recallops-agent
- Functional demo: https://i5lvohbwb6newxfvc4xxiky6im0sojdz.lambda-url.us-east-1.on.aws/
- Installable fallback: https://github.com/MaxxxDong/recallops-agent (run `recallops` and open `http://127.0.0.1:8080`)
- Public video under three minutes: https://youtu.be/XoBr9iga4zQ (`videos/recallops-demo/renders/recallops-final.mp4`, 106.27s, 1080p, H.264/AAC, SHA-256 `ffbf310488aba29cc08affdcb8238df7e23871bbd32f326fda26bf748902a64f`)
- Devpost submission: https://devpost.com/software/recallops-h5oru8
- Submission status: submitted to CockroachDB × AWS Hackathon — Build with Agentic Memory.

## Access note

The judging build requires no credentials. AWS rejected reserved concurrency `1` under the account's concurrency floor, so the public Lambda instead minimizes exposure through a 256 MB / 30 second configuration, fixed synthetic input, bounded request bodies, and simulator-only actions. AWS usage is still possible and is not a hard-zero-cost guarantee.
