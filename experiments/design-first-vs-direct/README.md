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

## Status (honest)

- Balash arm: through stage 3, self-verified.
- Direct arm: **not built yet**.
- Blind judge + judge-scrutiny pass: **not run yet** for this framing.

No comparison result exists yet for the design-first framing. The prior, differently-framed pilots
(`../guide-vs-direct/`) are the only completed comparisons, and their main lesson — the blind judge
is unreliable without ground truth — is exactly why `CHARTER.md` builds judge-scrutiny into the
method here.
