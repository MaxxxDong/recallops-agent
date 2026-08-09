---
workflow: product-launch-video
flow: automation
storyboard: no
message: "RecallOps turns persistent incident memory into safe, exactly-once recovery actions"
destination: devpost-submission
aspect: 1920x1080
language: en
audience: CockroachDB and AWS hackathon judges
length: 150s
angle: evidence-led resilience demonstration
narration: yes
vo_mode: restructured
---

## Intent

Demonstrate the complete agentic-memory loop: retrieve scoped incident memory, expose its provenance, pause for human approval, survive an injected failure, and resume without duplicating the action receipt. CockroachDB is the persistent memory core and AWS Lambda is the execution environment.

## Assets

- `../../src/recallops/ui.html` — the real product UI to capture and feature.
- `../../docs/security/evidence/real-provider.log` — real CockroachDB, C-SPANN, and Managed MCP evidence.
- `../../docs/security/evidence/aws-lambda.log` — real ARM64 Lambda and exactly-once recovery evidence.
- `../../docs/technical-overview.md` — authoritative architecture and boundary explanation.

## Customizations

- Show the real UI, memory provenance, approval interrupt, failure injection, and final one-receipt state.
- Include one compact architecture scene mapping LangGraph, CockroachDB vector/transactional state, Managed MCP, and AWS Lambda.

## Notes

- English, 16:9, approximately 150 seconds and strictly under the official 3-minute limit.
- Explicitly identify Distributed Vector Indexing and Managed MCP as the two CockroachDB tools, and Lambda as the AWS service.
- The deployed Lambda evidence profile is a no-secret demo; the provider proof is separate and must not be misrepresented as a public credential-bearing deployment.
- No third-party copyrighted music or trademarks beyond factual platform names required to explain integration.
- This is an autonomous build; provide a contact sheet before final render.
