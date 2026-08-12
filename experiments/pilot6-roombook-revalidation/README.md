# Pilot #6 — RoomBook re-validation (does the method close pilot #4's product gap?)

**Question.** Pilot #4 showed design-first can *win the design and lose the product* — two real bugs and
a cut affordance. The skill was then changed (restored Guide→Worker delegation; adversarial /
lifecycle-falsifier exit criteria; a probe reviewer). Did those changes close the gap?

**Method.** Re-run pilot #4's exact staged RoomBook product under the current skill (`11983a5`), with a
**persistent Guide agent that never saw #4's findings**, **fresh Worker agents** per stage, an
orchestrator ferrying **verbatim**, and a spec-only oracle. Four criteria were **pre-registered** against
#4's documented defects and measured by **deterministic probes** + source citation.

**Result — 3 of 4 closed; one recurs.**

| A1 cross-room promotion | A3 negative stride | D one conflict owner | A2 waitlist read |
|---|---|---|---|
| ✅ closed | ✅ closed | ✅ preserved | ❌ recurs |

The two product **bugs** (A1, A3) are closed and the design win survived; the cut **affordance** (A2)
returns. The subtractive pass reliably removes dead machinery *and* still removes a real product
affordance when no present force names it — the method fixes wrong outputs (they have falsifiers) but
not omissions (they have none). **Next skill gap: a product-completeness counterweight to the subtractive
pass.**

**Honest limits.** n = 1; a container restart + user model switch made this a **mixed-model** run
(stages 1–3 and the stage-4 plan/design on `claude-fable-5`; stage-4 review/impl on `claude-opus-4-8` —
the decisive design captures were fable's, pre-switch); one orchestrator ferried both sides (verbatim,
but a few ferry-backs echoed the Guide's own review duties); the orchestrator knew #4's findings (the
Guide did not, and A1/A3/A2 are deterministic, not judgments).

## Files
- [`FINDINGS.md`](FINDINGS.md) — full readings, evidence, mechanism, and limits.
- [`balash-arm/`](balash-arm) — final `roombook.js`, `roombook.test.js` (63 green), `ARCHITECTURE.md`, `GOALS.md`, `BASE-DEPENDENCIES.md`.
- [`probes.mjs`](probes.mjs) — the pre-registered A1 / A3 / A2 probes (run with `node probes.mjs` from `balash-arm/`).
