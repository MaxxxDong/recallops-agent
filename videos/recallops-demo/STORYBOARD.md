---

## Video direction

- Palette: use `frame.md` roles exactly — midnight canvas, pale ink, layered navy surfaces, and scarce coral voltage only for failure, approval, or the one result that matters.
- Type: display role for claims, body for operator guidance, mono for incident IDs, provenance, idempotency keys, status, and receipts.
- Motion: one paused seek-safe timeline per frame; smooth long-tail settles, VO-paced sequential reveals across the back half, and velocity-matched internal seams. No bounce, repeat, random, wall-clock, CSS animation, lazy breathing, or late camera drift.
- Rhythm: Frames 1–3 establish risk and product; Frames 4–7 move deliberately through state and approval; Frame 8 fails hard; Frame 9 earns the climax; Frames 10–12 slow into architecture, disclosure, and a held close.
- Composition: operational panels remain readable, primary element fills at least 40% of the canvas, and the bottom 17% stays clear for captions.
- Negative list: no fake production outage, fake cloud activity, fake database values, generic robot/brain graphics, neon AI gradients, browser chrome, slideshow front-loading, or screensaver motion.
format: 1920x1080
duration: 150s
message: "RecallOps turns persistent incident memory into safe, exactly-once recovery actions."
arc: PAS with Demo Loop
audience: CockroachDB and AWS hackathon judges, SRE and platform teams
mode: autonomous
music: none
---

## Frame 1 — Recovery should survive the failure

- scene: A recovery timeline fractures, but one incident identity stays pinned.
- voiceover: "An incident can interrupt the recovery process itself. The next attempt should remember exactly where the last one stopped."
- duration: 6.4s
- poster: 4s
- transition_in: cut
- status: animated
- src: compositions/frames/01-survive-failure.html
- type: hook
- persuasion: Pain validation
- beat: tension
- blueprint: compose
- asset_candidates:

Make the interruption visible without depicting a production outage.

Adapt: keep the in-place token-swap signature; the stable incident identity stays fixed while recovery states fracture around it.
Scene 1 (0.0–1.7s): `RECOVERY` arrives in the center over a thin three-step timeline; the left step is calm navy and the incident ID sits pinned above in mono.
Scene 2 (1.7–4.1s): on “interrupt,” the variable token hard-cuts to `FAILED`, the middle rail fractures into offset slices (`chromatic-glitch`), but the incident ID remains motionless and sharp.
Scene 3 (4.1–6.4s): `REMEMBER WHERE IT STOPPED` assembles per phrase (`dynamic-content-sequencing`); the broken rail reconnects to the same ID and holds.

## Frame 2 — Stateless retries duplicate risk

- scene: Three identical retry cards multiply around one synthetic 503 event.
- voiceover: "Without durable memory, retries repeat diagnosis, lose provenance, and can execute the same remediation twice."
- duration: 6.784s
- transition_in: zoom-through
- status: animated
- src: compositions/frames/02-stateless-risk.html
- type: pain_point
- persuasion: Risk agitation
- beat: anxiety
- blueprint: overwhelm-surround
- asset_candidates:

The danger is duplicated action, not raw alert volume.

Adapt: keep the accumulation-and-close-in signature; use duplicate retry artifacts instead of generic app clutter.
Scene 1 (0.0–1.8s): one `503 RETRY` card appears center-left beside an empty action-receipt slot; the camera is locked.
Scene 2 (1.8–4.5s): two more identical retry cards slide in from opposing edges as `DIAGNOSE AGAIN`, `LOSE PROVENANCE`, and `EXECUTE TWICE` reveal on their cues; cards close inward (`center-outward-expansion` reversed) without hiding the center.
Scene 3 (4.5–5.7s): the retry cluster surrounds a coral `DUPLICATE RISK` marker while the empty receipt slot remains visible.
Scene 4 (5.7–6.8s): motion stops on the unsafe state; no ambient float.

## Frame 3 — Meet RecallOps

- scene: Incident, memory and action receipt assemble around the RecallOps wordmark.
- voiceover: "RecallOps is a resumable incident agent. It remembers the evidence, requires approval, and turns one recovery into one durable receipt."
- duration: 8.363s
- transition_in: zoom-through
- status: animated
- src: compositions/frames/03-product-intro.html
- type: product_intro
- persuasion: Category definition
- beat: clarity
- blueprint: logo-assemble-lockup
- asset_candidates:

Introduce the product as a state machine, not a chatbot.

Adapt: keep the parts-assembly signature; assemble the identity from incident, memory, approval, and receipt.
Scene 1 (0.0–2.0s): four labeled rails enter from the frame edges — `INCIDENT`, `MEMORY`, `APPROVAL`, `RECEIPT` — and park around an empty center.
Scene 2 (2.0–4.8s): connectors self-draw from each rail into a compact state-machine glyph (`svg-path-draw`); labels arrive only as the VO names their ideas.
Scene 3 (4.8–6.9s): the glyph flattens into the RecallOps wordmark via depth-scatter assemble (`depth-scatter-assemble`); `RESUMABLE INCIDENT AGENT` appears beneath.
Scene 4 (6.9–8.4s): one coral pulse marks the approval node, then the complete lockup holds still.

## Frame 4 — Create a synthetic incident

- scene: The real workbench receives the synthetic checkout-latency event and creates a run.
- voiceover: "Start with a synthetic checkout incident: latency above two seconds, followed by duplicate five-oh-three retries. RecallOps creates a stable run identity."
- duration: 9.941s
- transition_in: push-slide LEFT
- status: animated
- src: compositions/frames/04-create-incident.html
- type: feature_showcase
- persuasion: Show-don't-tell proof
- beat: curiosity
- blueprint: device-surface-showcase
- asset_candidates: assets/workbench.png — real RecallOps local workbench with the synthetic incident input and four-step recovery controls

Use the actual UI as the main surface.

- focal: assets/workbench.png
- roles: workbench.png = cutout · incident-ID strip = supporting · midnight field = background

Adapt: keep the persistent-window signature; one real captured workbench is the entire demo surface.
Scene 1 (0.0–2.0s): the real RecallOps workbench rises into a wide 70/30 floating window with a faint coral edge and settles via motion-blur streak.
Scene 2 (2.0–5.0s): as the synthetic event is read, the camera targets the textarea (`coordinate-target-zoom`); each fact receives a restrained marker sweep, one at a time.
Scene 3 (5.0–8.0s): `CREATE INCIDENT` receives a custom cursor approach and one click ripple; an incident-ID strip animates out from the button into the right-side evidence panel.
Scene 4 (8.0–9.9s): camera eases back to the full workbench and holds the generated run identity.

## Frame 5 — Retrieve memory with provenance

- scene: A query enters CockroachDB; two relevant memories return with timestamps and sources attached.
- voiceover: "CockroachDB's Distributed Vector Index retrieves relevant incident memory. Every result keeps its source, observation time, and incident identity."
- duration: 9.493s
- transition_in: push-slide LEFT
- status: animated
- src: compositions/frames/05-vector-memory.html
- type: feature_showcase
- persuasion: Feature-to-benefit translation
- beat: control
- blueprint: prompt-type-submit-generate
- asset_candidates:

Name the official CockroachDB capability explicitly.

Adapt: keep query-to-streamed-answer theater; the answer is a provenance-bearing memory set, not generated prose.
Scene 1 (0.0–2.0s): a focused query card types `checkout duplicate 503 latency` with a blinking caret; surrounding workspace remains dim.
Scene 2 (2.0–4.3s): submit compresses once (`press-release-spring`); `DISTRIBUTED VECTOR INDEX` appears as a mono status line while the camera locks.
Scene 3 (4.3–7.6s): two memory cards stream in separately; each reveals source, observation time, and incident identity on the corresponding VO cue.
Scene 4 (7.6–9.5s): the query and two results settle into an asymmetric 40/60 composition; a coral provenance rail connects them and holds.

## Frame 6 — Inspect state through Managed MCP

- scene: Read-only MCP calls orbit one incident state; raw credentials and writes remain outside the frame.
- voiceover: "CockroachDB Managed MCP provides a second, independently auditable view of the same persistent state — read-only in this prototype."
- duration: 8.896s
- transition_in: crossfade
- status: animated
- src: compositions/frames/06-managed-mcp.html
- type: feature_showcase
- persuasion: Independent verification
- beat: trust
- blueprint: comparison-split
- asset_candidates:

Do not imply MCP write support.

Adapt: keep two equal-weight mirrored cards; compare vector retrieval with the read-only Managed MCP audit view.
Scene 1 (0.0–2.2s): `VECTOR RETRIEVAL` enters from left and `MANAGED MCP` from right with mirrored book-open tilts (`split-tilt-cards`).
Scene 2 (2.2–5.0s): the left card reveals relevant memory and provenance; the right card reveals the same run identity and state, sequentially on the VO cues.
Scene 3 (5.0–7.3s): a shared `PERSISTENT COCKROACHDB STATE` spine self-draws between the inner edges; both cards receive `AUDITABLE` badges.
Scene 4 (7.3–8.9s): `READ-ONLY IN THIS PROTOTYPE` lands as the sole coral callout and the comparison holds still.

## Frame 7 — Approval is a real gate

- scene: A locked action card waits; the human approval pulse unlocks only the allowlisted simulator action.
- voiceover: "The proposed action cannot run by itself. A human approves one allowlisted simulator restart before execution becomes available."
- duration: 8.085s
- transition_in: squeeze
- status: animated
- src: compositions/frames/07-approval-gate.html
- type: benefit_highlight
- persuasion: Risk reversal
- beat: confidence
- blueprint: cta-morph-press
- asset_candidates:

Make the approval boundary visually unambiguous.

Adapt: keep the same-center morph and physical press; the CTA is the real approval gate, not a marketing action.
Scene 1 (0.0–1.9s): a locked `RESTART SYNTHETIC WORKER` action card holds dead-center; a human silhouette marker and `APPROVAL REQUIRED` sit above.
Scene 2 (1.9–3.8s): the locked card condenses at the same center into `APPROVE ONCE` (`scale-swap-transition`); the allowlisted target remains visible below.
Scene 3 (3.8–5.9s): a cursor approaches off-center and presses; cursor and button compress together (`physics-press-reaction`) while a single coral ripple confirms the human action.
Scene 4 (5.9–8.1s): the button becomes `APPROVED`; execution unlocks beside it, but does not run. The frame holds.

## Frame 8 — Fail once, on purpose

- scene: The execute step turns red once; memory remains green and the idempotency key stays fixed.
- voiceover: "Now inject one failure during execution. The process stops, but the run state, approval, evidence, and idempotency key remain durable."
- duration: 8.149s
- transition_in: push-slide LEFT
- status: animated
- src: compositions/frames/08-injected-failure.html
- type: feature_showcase
- persuasion: Adversarial proof
- beat: tension + control
- blueprint: agent-progress-theater
- asset_candidates:

This is the central proof beat; hold the failed state long enough to read.

Adapt: keep trigger-to-working-to-receipt theater; invert the payoff into a deliberate one-time failure with durable state still visible.
Scene 1 (0.0–1.8s): `EXECUTE WITH ONE FAILURE` is triggered in a focused run panel; the idempotency key is already pinned above in mono.
Scene 2 (1.8–3.9s): status rows activate in order — load run, verify approval, begin simulator action — with restrained progress checks.
Scene 3 (3.9–6.0s): `INJECTED FAILURE` cuts in coral; the running row fractures, but state, approval, evidence, and key remain green and fixed around it.
Scene 4 (6.0–8.1s): the complete failed-state card holds still for reading; no recovery is shown yet.

## Frame 9 — Resume exactly once

- scene: RESUME reconnects to the same key; one receipt appears while a duplicate counter remains at one.
- voiceover: "Resume the same run. RecallOps reuses the same idempotency key and produces one receipt. Retry again — execution count stays one."
- duration: 8.469s
- transition_in: zoom-through
- status: animated
- src: compositions/frames/09-resume-once.html
- type: benefit_highlight
- persuasion: Show-don't-tell proof
- beat: relief + triumph
- blueprint: dataviz-countup
- asset_candidates:

The count of one is the video's primary outcome metric.

Adapt: keep the count-up-to-hero-metric signature; the metric is a verified execution count, not growth theater.
Scene 1 (0.0–1.9s): `RESUME SAME RUN` enters above the pinned idempotency key; a continuity connector self-draws into the stalled action.
Scene 2 (1.9–4.1s): receipt fields assemble one by one as the action resumes; the camera moves through the connector into a large count ring (`multi-phase-camera`, `coordinate-target-zoom`).
Scene 3 (4.1–6.3s): the center number counts from zero to one while its ring fills (`counting-dynamic-scale`, `stat-bars-and-fills`); `ONE RECEIPT` lands beneath.
Scene 4 (6.3–7.5s): a retry marker pulses once; the number stays one and `EXECUTION COUNT` becomes the hero label.
Scene 5 (7.5–8.5s): all supporting elements dim; the count of one holds in the center without drift.

## Frame 10 — CockroachDB memory, AWS execution

- scene: A three-layer architecture assembles: browser, RecallOps state machine, CockroachDB and AWS Lambda.
- voiceover: "The architecture is deliberately narrow. CockroachDB persists incident memory and action receipts. AWS Lambda runs the packaged demo entry point. RecallOps owns the recovery state machine."
- duration: 11.947s
- transition_in: zoom-through
- status: animated
- src: compositions/frames/10-architecture.html
- type: feature_showcase
- persuasion: Technical clarity
- beat: confidence
- blueprint: constellation-hub
- asset_candidates:

Label Distributed Vector Index, Managed MCP and Lambda without logo ornament.

Adapt: keep the hub-and-satellites topology; use capability labels and data-flow arrows, not partner-logo spectacle.
Scene 1 (0.0–2.8s): `RECALLOPS STATE MACHINE` forms at center; a thin ring and three connector paths draw outward.
Scene 2 (2.8–5.9s): `COCKROACHDB MEMORY` arrives left with `DISTRIBUTED VECTOR INDEX` and `MANAGED MCP` stacked beneath, revealed on their spoken cues.
Scene 3 (5.9–8.6s): `AWS LAMBDA` arrives right as `PACKAGED DEMO ENTRY POINT`; the browser workbench appears top as a third node.
Scene 4 (8.6–10.7s): directional arrows animate once around the hub, then stop; responsibility labels lock to each node.
Scene 5 (10.7–11.9s): camera pulls back slightly to the complete three-layer architecture and holds.

## Frame 11 — Proof without hidden credentials

- scene: Two proof lanes appear: provider verification and deployed no-secret demo profile.
- voiceover: "Provider verification proves the real CockroachDB paths separately. The deployed Lambda image carries no database secrets and exposes no anonymous function URL."
- duration: 10.432s
- transition_in: crossfade
- status: animated
- src: compositions/frames/11-security-boundary.html
- type: social_proof
- persuasion: Trust through bounded claims
- beat: trust
- blueprint: comparison-split
- asset_candidates:

This disclosure prevents the video from implying a public live database connection.

Adapt: keep paired evidence lanes; one proves provider integration, the other proves the deployed image's bounded security profile.
Scene 1 (0.0–2.6s): `PROVIDER VERIFICATION` and `DEPLOYED LAMBDA DEMO` enter as equal mirrored cards (`split-tilt-cards`).
Scene 2 (2.6–5.6s): the left card reveals `REAL COCKROACHDB PATHS` and two small capability receipts; the right reveals `NO DATABASE SECRETS` and a clean environment ledger.
Scene 3 (5.6–8.3s): `NO ANONYMOUS FUNCTION URL` arrives as the sole coral boundary on the right; a `SEPARATE PROOF` spine appears between both lanes.
Scene 4 (8.3–10.4s): both cards flatten into one audit sheet and hold, with no suggestion of a public live provider connection.

## Frame 12 — Durable memory, bounded action

- scene: MEMORY, APPROVAL and ONE RECEIPT collapse into the final RecallOps lockup.
- voiceover: "RecallOps: durable incident memory, human approval, and exactly-once recovery — demonstrated safely with synthetic data and a simulator action."
- duration: 9.28s
- transition_in: zoom-through
- status: animated
- src: compositions/frames/12-outro.html
- type: cta
- persuasion: Value synthesis
- beat: inevitability
- blueprint: logo-assemble-lockup
- asset_candidates:

End on the verified capability and safety scope.

Adapt: keep parts-assembly-to-lockup; the final identity is built from the three verified safeguards.
Scene 1 (0.0–2.6s): `DURABLE MEMORY`, `HUMAN APPROVAL`, and `ONE RECEIPT` arrive from three directions in mono rails, one per spoken cue.
Scene 2 (2.6–5.4s): rails converge into the RecallOps state glyph via depth-scatter assemble; the coral approval node pulses once while memory and receipt remain pale ink.
Scene 3 (5.4–7.6s): `SYNTHETIC DATA · SIMULATOR ACTION` reveals beneath as a quiet boundary line; the RecallOps wordmark completes above.
Scene 4 (7.6–9.3s): the lockup holds completely still to the final cut.
