# Output trust boundary

`output_trust_boundary_applicability=APPLICABLE`: incident text and provider results cross JSON, browser HTML, SQL, and log sinks.

## Trust boundary matrix

| Source field | Processing chain | Sink | Encoding or validation | Test anchor |
| --- | --- | --- | --- | --- |
| `event_text` HTTP input | size-limited JSON parse → normalized as data → JSON encode | JSON | `json.dumps`; semantic text preserved | `SinkAndConfigurationTests.test_real_wsgi_json_preserves_adversarial_payload` |
| API JSON fields | JSON parse → browser `JSON.stringify` → DOM | HTML | `textContent`, never `innerHTML`; restrictive CSP and `nosniff` | `test_browser_sink_uses_text_content_not_html`; real browser log |
| vector memory metadata | required structured fields → LangChain filter | SQL | structured filter values; fixed collection/columns; mandatory incident/service/severity/time scope | `test_scope_filter_excludes_other_service`; provider adapter review |
| MCP `run_id` | string argument → fixed table allowlist → MCP SQL arguments | SQL | compile-time `ALLOWED_AUDIT_TABLES`; `$1` parameter | `providers.py`; Root independent review required |
| provider error body | bounded HTTP read → exception/return object | log/JSON | production logs emit stable error categories, never body, key, URL query, prompt, or incident text | `test_provider_http_never_fakes_success` |
| idempotency key | server-derived run/action tuple → atomic map in demo; DB unique key in provider schema | action receipt | caller cannot select action or target; allowlisted simulator only | `test_concurrent_idempotency_key_has_one_receipt` |

Machine JSON and display HTML are deliberately separate: the API preserves text semantics; the browser converts JSON to text and assigns `textContent`.

## Adversarial corpus

The machine-readable corpus is [`tests/adversarial-corpus.json`](../../tests/adversarial-corpus.json). It covers scripts/event handlers, Markdown link/table/template tokens, quotes/newlines/backslashes/Unicode, SQL injection, CSV formula text, scope escalation, expired runbooks, duplicate keys, forged checkpoints/receipts, and MCP error bodies. RecallOps does not export CSV or render Markdown; those payloads remain inert JSON/text.

## Controls and limitations

- Only synthetic incidents and an allowlisted synthetic action are supported.
- Approval is mandatory; receipt claim precedes action recovery.
- Secrets are environment-only and never logged. Structured logs contain categories, not request bodies.
- Managed MCP is read-only by application contract and uses fixed tables plus a parameterized run id.
- Provider mode is intentionally not wired into the local demo. Until Root supplies and validates the real repository/store integration, it returns `configuration_required`; this prevents false provider success.
- The current vector adapter relies on the dependency's structured filter compiler. Root must independently review the emitted SQL against the live frozen version before Gate C.

## Security evidence gate

- RED log: [`evidence/red.log`](evidence/red.log)
- GREEN log: [`evidence/green.log`](evidence/green.log)
- Real HTTP sink: [`evidence/real-http.log`](evidence/real-http.log)
- Real browser sink: [`evidence/browser.log`](evidence/browser.log)
- OpenTelemetry/log privacy smoke: [`evidence/otel.log`](evidence/otel.log)
- Source equivalence: [`evidence/source-equivalence.log`](evidence/source-equivalence.log)

Independent adversarial review is intentionally left to Root. Until Root records `APPROVE` with no P0–P2 findings and no unexplained sink, this implementation remains review-ready input rather than Gate-C-authorized output.
