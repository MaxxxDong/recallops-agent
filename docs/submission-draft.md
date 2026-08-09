# RecallOps — submission draft

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
- Deployment boundary: the current Lambda image is a no-secret demo profile with no anonymous Function URL; real provider verification is recorded separately.

## Judge demo

1. Create the synthetic checkout incident.
2. Inspect retrieved memory and provenance.
3. Approve the allowlisted simulator action.
4. Execute with one injected failure.
5. Resume the same run.
6. Retry and verify `execution_count = 1` with the same receipt.

## Links to add at Gate C

- Public repository: pending publication approval
- Functional demo: pending public-access security decision
- Public video under three minutes: `videos/recallops-demo/renders/recallops-final.mp4` (106.27s, 1080p, H.264/AAC, SHA-256 `ffbf310488aba29cc08affdcb8238df7e23871bbd32f326fda26bf748902a64f`)

## Access note

The judging build must remain available without payment through the judging period. Any test credentials or access instructions will be documented here before submission.
