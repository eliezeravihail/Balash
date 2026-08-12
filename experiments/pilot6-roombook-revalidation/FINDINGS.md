# Pilot #6 — RoomBook re-validation: did the method fixes close pilot #4's product gap?

Pilot #4 produced the method's sharpest honest result: **design-first won the design and lost the
product** — the same minimalist discipline that produced the deeper design also shipped two real bugs
(a broken cross-room waitlist promotion; a recurring series that booked backwards on a negative stride)
and cut a real affordance (no way to inspect the waitlist). Between #4 and now, the skill changed:
**Guide→Worker delegation was restored** (in #4 one agent played both), **exit criteria became
adversarial / lifecycle-falsifier-shaped**, and a **probe reviewer** entered the review panel. The
standing question — *did those fixes close the product gap?* — was an **unverified claim**, exactly the
kind the method forbids. Pilot #6 tests it.

## Setup — the same product, the current method, an uncontaminated Guide

- **Product:** RoomBook, pilot #4's exact staged spec (`../pilot4-roombook-evolving/STAGES.md`), verbatim
  — four hidden stages revealed one at a time (same-room conflict → recurring series + cancel → waitlist
  + auto-promotion → capacity + a cross-room person-overlap invariant).
- **Method:** `balash-guide` at commit **`11983a5`** (the current head at run time).
- **Roles genuinely separated this time** (the #4 fidelity gap): a **single persistent Guide agent**
  that **never saw pilot #4's findings** planned every stage and measured every return; **fresh Worker
  agents** built each design and each implementation. The orchestrator (the main session) ferried
  handoffs and returns **verbatim** and answered product questions only from the spec ("no requirement
  beyond the spec" otherwise) — the same oracle discipline as #4.
- **Pre-registered before running** — the four criteria, mapped to #4's documented defects:
  - **A1** — a cancellation that frees a *person* promotes a compatible waitlist entry in *another* room.
  - **A2** — a waitlist **read** affordance exists (a user can see who is queued).
  - **A3** — a non-positive recurring stride is rejected and books nothing.
  - **D** — the conflict truth stays in **one owner** at stage 4 (the design win is not lost).

## Result — 3 of 4 closed; A2 recurs

The four criteria were measured by **deterministic probes** (`probes.mjs`, reproduced against the final
`balash-arm/roombook.js`) and by source citation — not by opinion:

| # | pilot #4 | pilot #6 | evidence |
|---|---|---|---|
| **A1** cross-room promotion on a person-freeing cancel | ❌ broken (entry stranded forever) | ✅ **closed** | `probes.mjs` A1a+A1b: after `cancel` in room A frees person `p1`, the room-B entry promotes; and it is **not** promoted while `p1` is still busy (both directions). Design: `promoteWaitlist` is global, `cancel` unscoped (`roombook.js` cancel→promote; test T56). |
| **A3** non-positive stride rejected, nothing booked | ❌ booked backwards in time | ✅ **closed** | `probes.mjs` A3a+A3b: `InvalidRecurrenceError`, `schedule` empty. Criterion was **derived by the Guide itself** in the stage-2 handoff ("`everyMinutes < 1` … invalid input"), with no knowledge of #4. |
| **D** one conflict owner at stage 4 | ✅ | ✅ **preserved/strengthened** | One `overlaps()` encoding; `commitBookings` is the sole writer and sole enforcer of all state rules; person-overlap absorbed as a **cross-room read leg** on the same predicate; the promotion trigger **re-judged and re-homed** to global when the person rule falsified room-independence (source-cited in the stage-4 design review). |
| **A2** waitlist read affordance | ❌ cut | ❌ **recurs** | `probes.mjs` A2: public surface is `book, bookRecurring, schedule, cancel, joinWaitlist, setCapacity` — **no waitlist read**. The Guide declared "no waitlist inspection" a non-goal with a recorded reason; the subtractive pass cut it, exactly as in #4. |

All four RoomBook stages: **63/63 tests green**, `node --check` clean, zero dependencies; each stage
measured by the Guide reproducing the evidence itself (hashed byte-identity of the regression gate,
grepped single-owner/one-encoding facts, source-read falsifiers) — not on a Worker's word.

## What this establishes

- **The two product *bugs* are closed** — and by mechanisms traceable to the specific fixes. A3 closed
  because the Guide's adversarial exit criteria **name the negative/zero edge by default** (it produced
  the `everyMinutes < 1` criterion cold). A1 closed because restored Guide→Worker delegation plus the
  probe reviewer plus the "offer-to-the-authority" design (promotion cannot self-check; it can only ask
  the one authority to commit) make a stranded cross-room entry a first-class falsifier (T56) rather
  than an emergent gap. In #4 the same insight was *written and then not propagated to the trigger*;
  here the trigger is the design's subject.
- **The design win survived evolution and the fidelity gap was fixed.** With a real Worker executing a
  real Guide's criteria, the stage-4 design re-homed the invariant (person-overlap as the first
  cross-room rule; the promotion trigger re-judged for the enlarged enabling set) — #4's design-quality
  result reproduced *with* the Guide/Worker separation it lacked.

## What it does NOT establish — and the finding that matters

- **A2 recurs: the affordance cut is not fixed.** This is the important negative result. The subtractive
  pass still removes a genuine product affordance whenever no *present* force names it — "a user cannot
  see the queue" is not expressible as a violated invariant, so the discipline that correctly deletes
  dead machinery also deletes it. The method now reliably closes product **bugs** (a wrong output has a
  falsifier) but not product **omissions** (a missing affordance has none). **This points to the next
  skill gap: the subtractive pass needs a product-completeness counterweight** — a check that asks, of
  each capability, "what can a user *not* do that the spec's scenario implies they'd need?", which no
  current criterion supplies.
- **n = 1**, one product, one domain. Directional, not proof.
- **Mixed-model confound (infrastructure-forced).** Stages 1–3 and the stage-4 **plan and design** ran
  on `claude-fable-5`; a container restart mid-stage-4 plus a user model switch moved the stage-4
  **design-review and implementation** to `claude-opus-4-8`. The decisive design-level captures (the A1
  cross-room falsifier; the D re-homing) were produced by **fable, before the switch** — but the clean
  single-model comparison to #4 is not preserved. Recorded, not hidden.
- **Single orchestrator, not independent operators** (same limit as #4): one main session ferried both
  the Guide's and Workers' text. It ferried **verbatim**, but a few ferry-back messages *reminded the
  Guide of its own review duties* (drawn from the Guide's own prior checkpoints) — a small contamination
  vector to remove next time (ferry the return and "proceed per the skill", nothing more).
- **The orchestrator knew #4's findings.** This cannot bias A1/A3 (deterministic behavioral probes) or
  A2 (objective surface inspection), and the **Guide** never saw them — but a fully blind orchestrator
  is stronger.

## Provenance

- Method: `balash-guide` @ `11983a5`. Product spec: pilot #4's `STAGES.md`, verbatim.
- Final code + design docs: [`balash-arm/`](balash-arm) (`roombook.js`, `roombook.test.js` 63 tests,
  `ARCHITECTURE.md`, `GOALS.md`). Probes: [`probes.mjs`](probes.mjs).
- Guide plans/handoffs and per-stage measurements are in the run transcripts; the Guide's durable state
  (objectives, exit criteria, reproduced evidence) is in the workdir `.balash/state.md` at run end.
