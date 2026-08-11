# Balash Guide State

Loop status only — the flags that drive the loop and let it survive compaction. This file is **not**
the design record. The durable engineering design lives in the product's own `GOALS.md`,
`BASE-DEPENDENCIES.md`, and `ARCHITECTURE.md` (facts, kept next to the code). Keep this short; do not
use it as a transcript or a worker task log.

<!-- SCHEMA CONTRACT (this template owns it): the balash commands read the goal from this file by
     heading and marker when they run. The load-bearing anchors are the headings `## Current objective`
     (with its `**Objective:**` and `**Kind:**` markers), `## Mode`, and `## Loop cursor`. Keep those
     headings and marker formats intact — a resuming command re-orients from them; rename one and the
     command reads the wrong thing (or nothing). -->

## Mode

auto

## Loop cursor

awaiting-worker 0001-pilot6-validate-product-fix

## Current objective

**Kind:** implementation

**Objective:** Prove (or refute) that the current method — restored Guide→Worker delegation,
adversarial/falsifier exit criteria, probe review — closes pilot #4's product gap. Run the Balash arm
of RoomBook (4 hidden stages, isolated uncontaminated Guide agent) at method commit `11983a5`, then
assess blind against the pre-registered criteria below.

**Why now:** "We fixed the product loss" is currently an unverified claim — the exact kind the method
forbids. It is the highest-value open uncertainty in the project (RESULTS.md next-steps #1).

**Exit criteria:**
- [ ] A1-class probe: a cancel that frees a *person* promotes a compatible waitlist entry in another room.
- [ ] A2-class: a waitlist read affordance exists (a user can see who is queued).
- [ ] A3-class probe: a non-positive recurring stride is rejected (nothing booked).
- [ ] D: at stage 4 the conflict truth (overlap AND (same room OR shared attendee)) is owned in one
      cited place — the design win did not regress.
- [ ] The run is recorded in experiments/pilot6-* with method hash, final code, probes, and an honest
      outcome (including failure, if that is the reading), and RESULTS.md is updated.

**Preserve:** Guide agent must never see pilot-#4 findings; product info limited to the stage specs;
oracle answers only from spec ("no requirement beyond the spec" otherwise).

**Do not optimize for:** a flattering outcome; teaching the arm the known defects; a full two-arm
re-run (Direct baseline is already recorded in pilot #4).

## Open Guide TODO

- [ ] 0002 (refactoring): subtractive/consolidation pass on the skill docs — canonical home per rule +
      pointers; A/B-validate behavior preservation. Run AFTER 0001 (its outcome may change the skill).
- [ ] 0003 (implementation, small): README install instructions (EN+HE); record method-hash rule for
      experiments; commit the feasibility-gate A/B record into experiments/; note the n≥2 replication
      rule for load-bearing wording changes.

## Last evaluated result

(none yet this loop)
