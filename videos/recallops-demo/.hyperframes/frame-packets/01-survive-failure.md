# Frame packet: 01-survive-failure

## Project inputs

- Project: /Users/max/Desktop/CodexWS/Auto/recallops-agent/videos/recallops-demo
- Design tokens: /Users/max/Desktop/CodexWS/Auto/recallops-agent/videos/recallops-demo/frame.md
- RULES_DIR: /Users/max/.mirasim/skills/hyperframes-animation/rules

## Assigned storyboard block

## Frame 1 — Recovery should survive the failure

- scene: A recovery timeline fractures, but one incident identity stays pinned.
- voiceover: "An incident can interrupt the recovery process itself. The next attempt should remember exactly where the last one stopped."
- duration: 6.4s
- poster: 4s
- transition_in: cut
- status: outline
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

## Selected motion rule: chromatic-glitch

---
name: chromatic-glitch
description: RGB-split / slice glitch that snaps sharp — offset color copies jitter on a deterministic hash of quantized timeline time (never Math.random), or horizontal slices displace and converge; a brief vibration, then a clean resolve. Entrance or emphasis punctuation; finite, seek-safe.
metadata:
  tags: glitch, rgb-split, chromatic, slice, jitter, stutter, text, snap, distortion
---

# Chromatic Glitch

Digital interference as punctuation: for a fraction of a second the element **breaks** — offset color copies shudder behind it, or horizontal slices displace sideways — then it **snaps sharp** and holds clean. The payoff is the resolve; the glitch exists to make the clean state land harder. Two forms: an **RGB-split jitter** (warm + cool ghost copies vibrating behind the base) and a **slice displacement** (horizontal bands that arrive offset and converge).

Boundaries: [motion-blur-streak.md](motion-blur-streak.md) is velocity blur tied to **travel** — its element is going somewhere fast. A glitching element is **in place**; the disturbance is temporal, not directional. [hacker-flip-3d.md](hacker-flip-3d.md) substitutes **glyphs** (a decode); here the glyphs are fixed and only displaced copies of them move.

## How It Works

The subject is stacked: the **base copy on top** (full legibility at every frame), ghost copies behind. All motion comes from one finite **amplitude-envelope** tween read by an `onUpdate`:

1. **Quantized time** — `const step = Math.floor(tl.time() / JITTER_STEP)`. The stutter comes from offsets that hold for `JITTER_STEP` and then jump. Smoothly interpolated offsets read as wobble, not glitch — **the quantization IS the digital texture**.
2. **Deterministic hash** — offsets are a pure function of `(step, layerIndex)`:

   ```js
   const glitchHash = (n) => {
     const x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
     return x - Math.floor(x); // 0..1, pure — a scrub to any t recomputes the same frame
   };
   ```

3. **Amplitude envelope** — a proxy tween carries `amp: 1 → 0` over `GLITCH_DUR`. Per-frame offset = `amp × (glitchHash(step * 13 + layer * 7) * 2 − 1) × MAX_SPLIT`. When the envelope hits zero the copies sit at exactly 0 — the snap-sharp is built into the math, and a final `tl.set` clamps the rest state so the hold is bit-exact.

The **slice form** swaps color copies for `SLICE_COUNT` full copies, each clipped to a horizontal band via `clip-path: inset()`; per-band `x` (and optional `scaleX` stretch) start at hash-derived offsets and converge to 0 under a stepped ease.

## Recipe

```html
<!-- inside a standard scene clip (hyperframes-core) -->
<!-- Form A: RGB-split — ghosts behind, base on top. Copies metric-identical (one grid cell, same font stack); aria-hidden on every non-base copy. -->
<div class="glitch-stack" id="glitch-stack">
  <span class="glitch-copy warm" aria-hidden="true">{glitchText}</span>
  <span class="glitch-copy cool" aria-hidden="true">{glitchText}</span>
  <span class="glitch-base">{glitchText}</span>
</div>
```

```css
.glitch-stack {
  display: grid; /* all copies share one cell — pixel-identical boxes */
}
.glitch-base,
.glitch-copy {
  grid-area: 1 / 1;
}
.glitch-base {
  z-index: 2; /* grid items take z-index without position */
  color: {textColor};
}
.glitch-copy {
  z-index: 1;
  opacity: 0; /* raised only while the envelope is live */
  will-change: transform; /* updates every frame while live */
  mix-blend-mode: screen; /* additive on dark bg; drop to normal (and lower opacity) on light */
}
.glitch-copy.warm {
  color: {warmSplit}; /* classic: red/orange */
}
.glitch-copy.cool {
  color: {coolSplit}; /* classic: cyan/blue */
}
```

```js
// Form A: RGB-split jitter — envelope snaps to full amplitude, decays to zero.
// All per-frame state derives from tl.time() + the envelope: pure, replays on seek.
const copies = gsap.utils.toArray("#glitch-stack .glitch-copy");
const amp = { a: 0 };
tl.set(amp, { a: 1 }, GLITCH_START);
tl.set(copies, { opacity: SPLIT_OPACITY }, GLITCH_START);
tl.to(
  amp,
  {
    a: 0,
    duration: GLITCH_DUR,
    ease: "power3.in", // most of the violence up front, dying fast
    onUpdate: () => {
      const step = Math.floor(tl.time() / JITTER_STEP); // quantized — the stutter
      copies.forEach((el, layer) => {
        const jx = (glitchHash(step * 13 + layer * 7) * 2 - 1) * MAX_SPLIT * amp.a;
        const jy = (glitchHash(step * 29 + layer * 11) * 2 - 1) * MAX_SPLIT * 0.35 * amp.a;
        gsap.set(el, { x: jx, y: jy });
      });
    },
  },
  GLITCH_START,
);
// The clean resolve: clamp ghosts to exact rest — never rely on the decay
// landing on zero. A ghost left 1px off reads as a bug every frame after.
tl.set(copies, { x: 0, y: 0, opacity: 0 }, GLITCH_START + GLITCH_DUR);

// Form B: slice displacement — N band copies of the same content converge.
const slices = gsap.utils.toArray("#slice-stack .slice");
const bandH = 100 / slices.length;
slices.forEach((el, i) => {
  gsap.set(el, { clipPath: `inset(${i * bandH}% 0 ${100 - (i + 1) * bandH}% 0)` });
  const dir = glitchHash(i * 3 + 1) > 0.5 ? 1 : -1;
  tl.fromTo(
    el,
    {
      x: dir * (SLICE_OFFSET_MIN + glitchHash(i * 5 + 2) * (SLICE_OFFSET_MAX - SLICE_OFFSET_MIN)),
      scaleX: 1 + glitchHash(i * 7 + 3) * SLICE_STRETCH,
      opacity: 1,
    },
    { x: 0, scaleX: 1, duration: SLICE_RESOLVE_DUR, ease: "steps(SLICE_STEPS)" },
    SLICE_START + glitchHash(i * 11 + 4) * SLICE_JITTER_LAG,
  );
});
```

## Variations

- **Glitch-stretch entrance** — the element ENTERS glitching: layer `fromTo(stack, { scaleX: STRETCH_FROM, opacity: 0 }, { scaleX: 1, opacity: 1, duration: GLITCH_DUR, ease: "power4.out" })` (`STRETCH_FROM` 1.3–1.8) on the whole stack while the envelope runs. Stretch, split, and envelope all die at the same frame — the word is simply _there_, sharp.
- **Emphasis burst on a held word** — a spasm, not an arrival: 2–3 short envelopes (`GLITCH_DUR` ~0.12–0.2s each) separated by clean gaps of ~0.2–0.4s, each its own `set(amp)/to(amp)/set(rest)` triplet. The clean frames between bursts make it read as energy instead of a rendering fault.
- **Slice reveal** — Form B as the arrival itself: bands start opaque but displaced, converge under the stepped ease. Drop the color copies for the monochrome version — the restrained enterprise read of this rule.
- **Card / non-text glitch** — the stacked-copy machinery is content-agnostic (logo lockup, small card). Keep `MAX_SPLIT` proportional (~1% of element width) — oversized splits read as broken layout, not interference.

## Values

| token                                        | range                                  | notes                                                                                         |
| -------------------------------------------- | -------------------------------------- | --------------------------------------------------------------------------------------------- |
| MAX_SPLIT                                    | 4–14px at headline sizes (~0.06–0.1em) | vertical ~35% of horizontal; base must stay legible at peak                                   |
| JITTER_STEP                                  | 1/30–1/12 s                            | shorter = frantic buzz, longer = VHS stutter; **≥ one render frame** or quantization vanishes |
| GLITCH_DUR                                   | 0.25–0.6s entrance; 0.12–0.2s burst    | ≥ ~1s stops reading as an event and starts reading as a broken render                         |
| SPLIT_OPACITY                                | 0.5–0.9 (screen on dark)               | 0.35–0.6 unblended on light — screen on white is invisible                                    |
| SLICE_COUNT                                  | 4–10                                   | more = finer tear, diminishing past ~10                                                       |
| SLICE_OFFSET_MIN / MAX                       | 12–60px                                | derive per-band values from `glitchHash(i)`, never uniform — equal offsets read mechanical    |
| SLICE_STRETCH                                | 0–0.5                                  | 0 pure displacement; ~0.3 stretched-scanline read                                             |
| SLICE_RESOLVE_DUR / SLICE_STEPS / JITTER_LAG | 0.2–0.4s / 3–6 / ≤0.08s per band       | the stepped ease keeps the settle digital                                                     |
| {warmSplit} / {coolSplit}                    | —                                      | classic red/cyan; any opposing warm+cool brand pair survives                                  |

## Critical Constraints

- **Quantize time — the stutter IS the effect.** Offsets hold for `JITTER_STEP` then jump; if the glitch looks like jelly, you interpolated. `JITTER_STEP` ≥ one render frame or the quantization silently disappears.
- **Pure functions of (quantized time, index)** — every per-frame value comes from `glitchHash`; the hash inputs use `tl.time()`, nothing else.
- **Clamp the rest state** — `tl.set({ x: 0, y: 0, opacity: 0 })` on the ghosts at envelope end; never rely on the decay landing exactly on zero.
- **Base on top, always legible** — ghosts vibrate _behind_ the base; a glitch that destroys legibility for more than ~2 frames is a tear-down, not an accent.
- **Brief, then clean** — the clean hold after the snap is the actual beat; `GLITCH_DUR` well under half the element's screen time. Emphasis bursts are separate finite triplets.
- **No CSS `@keyframes` glitch loops** — the classic CSS glitch snippet runs on the wall clock and desyncs from seek; every displacement goes through the timeline's `onUpdate`.
- **Match the register** — RGB-split is a loud consumer/tech gesture; the monochrome slice variant is the only form that belongs in a restrained enterprise composition.

## See also

`kinetic-beat-slam` (one beat lands with the glitch-stretch entrance) · `spring-pop-entrance` (pop clean, burst on the stress beat) · `gradient-text-sweep` (gradient carries the hold after the resolve) · `discrete-text-sequence` (state swap masked at max amplitude) · `motion-blur-streak` (the traveling sibling — if it's moving fast, blur it there).

## Selected motion rule: dynamic-content-sequencing

---
name: dynamic-content-sequencing
description: Auto-calculate timeline start/end times from content length + per-item duration config — longer content gets more screen time without hardcoded numbers.
metadata:
  tags: timeline, sequencing, dynamic, duration, content-aware, utility
---

# Dynamic Content Sequencing

A utility pattern (not a motion rule in itself) for scenes that show a SEQUENCE of items (cards, phrases, stats): each item's duration is computed from its content length + per-item config, and the sequencer assigns absolute start/end times automatically — no hardcoded offsets per item. Distinct from [discrete-text-sequence](discrete-text-sequence.md) (one text element changing states) — this rule swaps between distinct content blocks.

## How It Works

A content array of `{ eyebrow, title, body, speedFactor, hold }` entries is reduced once at build time into a flat `TIMELINE` of `{ …entry, start, end }` — duration per entry is `BASE_DURATION + body.length × SEC_PER_CHAR + hold`, so longer text earns more reading time. A single linear driver's `onUpdate` reverse-searches the active entry and swaps the DOM **only on transitions** (a `lastTitle` guard — per-frame `textContent` writes flicker in render); an optional progress bar fills 0→100% across the whole run.

## Recipe

```html
<!-- inside a standard scene clip (hyperframes-core) -->
<div class="display">
  <div class="eyebrow" id="eyebrow"></div>
  <div class="title" id="title"></div>
  <div class="body" id="body"></div>
  <div class="progress-bar"><div class="progress-fill" id="progress-fill"></div></div>
</div>
```

```css
.body {
  min-height: 160px; /* reserve space — content height varies; without this, layout jumps */
}
.progress-fill {
  height: 100%;
  width: 0%;
}
```

```js
// N entries, each with its own pacing (optionally a speedFactor multiplier);
// the final entry uses a larger hold (closing beat).
const CONTENT = [
  { eyebrow: "{eyebrow1}", title: "{title1}", body: "{body1}", hold: HOLD_MID },
  // …
  { eyebrow: "{eyebrowN}", title: "{titleN}", body: "{bodyN}", hold: HOLD_FINAL },
];

// Pre-compute absolute start/end ONCE — never in onUpdate.
let cumulative = 0;
const TIMELINE = CONTENT.map((entry) => {
  const dur = BASE_DURATION + entry.body.length * SEC_PER_CHAR + entry.hold;
  const start = cumulative;
  cumulative += dur;
  return { ...entry, start, end: cumulative };
});

function entryAt(time) {
  for (let i = TIMELINE.length - 1; i >= 0; i--) {
    if (time >= TIMELINE[i].start) return TIMELINE[i];
  }
  return TIMELINE[0];
}

const eyebrowEl = document.getElementById("eyebrow");
const titleEl = document.getElementById("title");
const bodyEl = document.getElementById("body");
const progressEl = document.getElementById("progress-fill");

const TOTAL_DURATION = cumulative + TAIL_PAD;
const driver = { t: 0 };
let lastTitle = "";

tl.to(
  driver,
  {
    t: TOTAL_DURATION,
    duration: TOTAL_DURATION,
    ease: "none",
    onUpdate: () => {
      const entry = entryAt(driver.t);
      // Swap content only on transitions — no per-frame DOM thrash
      if (entry.title !== lastTitle) {
        eyebrowEl.textContent = entry.eyebrow;
        titleEl.textContent = entry.title;
        bodyEl.textContent = entry.body;
        lastTitle = entry.title;
      }
      progressEl.style.width = `${(driver.t / TOTAL_DURATION) * 100}%`;
    },
  },
  0,
);
```

## Variations

- **Crossfade between items** — return BOTH adjacent entries during an overlap window (`time ≥ e.start − overlap && time ≤ e.end + overlap`, overlap ≈ 0.3s) and render them with opacities computed from distance to the boundary.
- **Per-item motion variation** — map an `entry.style` key to an existing rule per chapter (e.g. `3d-text-depth-layers` → `hacker-flip-3d` → `counting-dynamic-scale`); the sequencer only orchestrates timing.
- **Auto-extend composition duration** — you can set `data-duration` from the computed `TOTAL_DURATION` in script, but HF reads `data-duration` at composition load and setting it after init may not take effect — author the duration manually from a rough total.

### Accelerating cadence (geometric hold decay)

For rhetorical escalation — "everyone says…", a roll-call, a praise flurry — the beat grid itself accelerates: early entries hold ~1s (read speed), then windows shrink geometrically into a ~0.15–0.3s flurry, braking on an emphasis state before the resolve. The acceleration is pre-computed into the same flat `TIMELINE` — still content-driven, still deterministic, no speed-up tween anywhere:

```js
// Geometric decay on the hold, clamped at a flurry floor; the brake state holds longest.
const HOLDS = CONTENT.map((entry, i) => Math.max(FLURRY_FLOOR, HOLD_START * Math.pow(DECAY, i)));
HOLDS[CONTENT.length - 1] = HOLD_FINAL;

let cumulative = 0;
const TIMELINE = CONTENT.map((entry, i) => {
  // Past ~0.5s states are glanced as motion texture, not read —
  // drop the per-char term or you never reach flurry speed.
  const readable = HOLDS[i] >= READ_THRESHOLD;
  const dur = HOLDS[i] + (readable ? entry.body.length * SEC_PER_CHAR : 0);
  const start = cumulative;
  cumulative += dur;
  return { ...entry, start, end: cumulative };
});
```

Worked example — **praise-chip flurry**: ~16 short quotes hard-cut through a chip beside a pinned wordmark. First 3 states at `HOLD_START = 1.0` (each reads fully); `DECAY = 0.8` shrinks every following window until `FLURRY_FLOOR = 0.2` catches it (≈12 states over ~2.5s — a churn of acclaim, individually glanced); the longest phrase takes `HOLD_FINAL ≈ 1.6` as the brake before the closing lockup.

Values: `HOLD_START` 0.8–1.2s; `DECAY` 0.75–0.88 (higher = longer runway before the flurry bites); `FLURRY_FLOOR` 0.15–0.3s (below ~0.15s swaps strobe); `READ_THRESHOLD` ~0.5s; brake ≥ 4× the floor or the stop doesn't register as a beat. The 3–6 entry guidance relaxes here — 12–18 states are legal precisely because flurry states aren't individually read. The hard-cut discipline (`lastTitle` guard, instant swaps) is what lets 0.2s states render clean.

## Values

| token         | range                 | notes                                                                                                                 |
| ------------- | --------------------- | --------------------------------------------------------------------------------------------------------------------- |
| BASE_DURATION | 0.6–1.5s              | minimum per entry regardless of length — even one-word entries get read time                                          |
| SEC_PER_CHAR  | 0.03–0.06 s/char      | ≈17–33 chars/sec; uniform across the sequence so the pace reads as one engine; lean high for wide-character languages |
| HOLD_MID      | 0.5–1.0s              | dwell on a non-final entry; `< HOLD_FINAL`                                                                            |
| HOLD_FINAL    | 1.0–2.0s              | climax dwell — must exceed HOLD_MID by a clear margin so the close reads as a beat                                    |
| SPEED_FACTOR  | 0.5–2.0 (default 1.0) | per-entry only; if every entry shares a factor, fold it into SEC_PER_CHAR                                             |
| TAIL_PAD      | 0.0–1.0s              | quiet beat after the last entry; prefer 0 when the next composition owns the breath                                   |
| CONTENT N     | 3–6 entries           | <3 isn't a sequence; >6 drags (accelerating cadence relaxes this — see above)                                         |

Reference: `../../examples/messaging-multi-phrase.html`.

## Critical Constraints

- **Pre-compute the TIMELINE once at build** — never recompute in `onUpdate`; the reverse search over the flat array is the whole per-frame cost.
- **DOM swap only on entry transition** (`lastTitle`/key guard) — per-frame `textContent` assignment flickers in HF render.
- **`min-height` on the body element** — without reservation, downstream elements (progress bar, brand) jitter as content height varies.
- **Sequential only** — for parallel tracks use a different reduction.
- **Titles fit one line at the chosen size; bodies fit inside `min-height` after wrapping.**

## See also

`discrete-text-sequence` (per-entry typewriter on the body) · `context-sensitive-cursor` (cursor color per chapter) · `vertical-spring-ticker` (animated word swap instead of hard cut) · `scale-swap-transition` (visual morph between entries).
