# design-first (Balash) vs. a plain session

Tests the **current** Balash thesis: does making *design* the goal — a Guide that formulates one
design/quality objective at a time and a Worker that implements conforming to it — produce
better-designed code, across an evolving product, than a plain session handed the product goals
directly?

**Start with [`CHARTER.md`](CHARTER.md)** — it states the hypotheses (H1 design quality, H2
mechanism, H0 the null we will accept), the four-stage product, the ground-truth oracle, the two
conditions, and — crucially — how the quality judge is scrutinized rather than trusted.

## Contents

- [`CHARTER.md`](CHARTER.md) — what we test and how (written before the comparison completes).
- [`balash-arm/`](balash-arm) — the Balash condition: the staged codebase (through stage 3) plus the
  design artifacts (`DESIGN_STAGE2.md`, `DESIGN_STAGE3.md`) the design objectives produced. 92 tests
  green. Domain/service/execution untouched across the stage-3 storage change (the H2 mechanism, one
  concrete manifestation).
- [`judge/design-quality-brief.md`](judge/design-quality-brief.md) — the blind design-quality
  reviewer brief (judge design like Martin/Fowler/Metz; do not hunt bugs).
- [`logs/architect-questions.md`](logs/architect-questions.md) — the oracle: the fixed product facts
  and the questions asked of it.

## Status — complete (one pilot)

- Balash arm (`balash-arm/`): all four stages, self-verified, 110 tests.
- Direct arm (`direct-arm/`): all four stages, self-verified, 87 tests.
- Blind judge: run twice with **opposite** dispositions (pure-OO-quality and pro-simplicity/YAGNI).
- Judge scrutiny: claims verified against source; oracle reconciliation done.

**Result (see [`FINDINGS.md`](FINDINGS.md)): both blind judges chose the Balash arm** (Y) as better
designed — ~70–75% and ~60% confidence — so the verdict is robust to the judge's philosophy. The
margin is moderate, not a rout; the plain arm (X) is genuinely good and wins on a few axes (a stronger
status invariant, atomic whole-state writes, two masterclass minimal abstractions). The single most
decisive, disposition-independent finding: on the cycle requirement the design-first arm wrote *less*
by reasoning cycles impossible, while the plain arm built dead detection machinery. All seven of the
judge's load-bearing claims verified against source (`verdicts/claim-verification.md`) — unlike the
earlier pilots' judge. Still **N = 1**: a signal, not a validated result. Full caveats in `FINDINGS.md`.
