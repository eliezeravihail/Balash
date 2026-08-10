# Discovery tuning: v3 vs v3.1, and does a design-principles checklist add real signal?

Two linked questions, tested together on the same four-stage scenario used in
`experiments/guide-vs-direct/`:

1. **Does budgeting discovery (v3.1: soft cap of 1 scenario + 3 questions per change, provisional
   defaults for cheap/reversible choices, an explicit never-ask list) cost anything relative to
   the uncapped v3 gate**, in either product fidelity or architecture quality?
2. **Does a literature-grounded, non-numeric design-principles checklist** (Tell-Don't-Ask/Law of
   Demeter, program-to-an-interface vs. a costume interface, Interface Segregation, Primitive
   Obsession, Anemic Domain Model, Feature Envy/Shotgun Surgery, Leaky Abstractions, Single
   Responsibility, Sandi Metz's rules) **add real review signal beyond fidelity/behavior/
   invariants review** — or is it redundant, or (the risk explicitly raised mid-experiment) just
   another gameable proxy?

Start with [`results/blind-review-fixed-judge.md`](results/blind-review-fixed-judge.md) — it
answers both questions directly, including the judge's own honest accounting of which of the 12
principles told it something new versus which were mechanical.

## What ran

Both conditions used the `balash-guide` skill, played by the same operator (this session) as
Guide, delegating to fresh Worker subagents per stage — identical to `guide-vs-direct`'s Guide
arm, except:

- **v3** (`.agents/skills/balash-guide/` as pushed to this repo) — the discovery gate with no
  question budget: sort every unresolved choice into grounded fact / open decision / technical
  freedom, ask about every open decision, no stopping rule beyond "no material open decision
  remains."
- **v3.1** (`references/discovery.md` only, everything else identical — see
  [`design-principles-drafts.md`](design-principles-drafts.md) for the full checklist as
  iteratively refined during review) — adds a soft budget (1 scenario + ≤3 questions per change),
  a stop-rule test ("would a different answer change the objective *now*?"), a "provisional
  product default" bucket for cheap/reversible choices, and an explicit never-ask list (fake-
  mechanism internals, exact command/flag names, error-message wording, blank-field policy absent
  a stated invariant, display columns).

Both arms also carried the design-principles requirement equally (added to the skill mid-run, see
`results/*/final-state.md` "Standing requirement" section) — every Worker handoff from stage 3
onward pointed at it, and every Worker reported which of the 12 principles it checked and what it
found, before the blind judge ever saw the code.

## Results at a glance

| | v3 (strict) | v3.1 (budgeted) |
|---|---:|---:|
| Discovery questions (4 stages) | 17 | 10 |
| Provisional defaults recorded | 0 | 9 |
| Final production LOC | 1982 | 1776 |
| Final test count | 263 | 195 |
| Design-principles tally (Correct / Hybrid / Incorrect) | 8 / 4 / 0 | 6 / 5 / 1 |
| Blind judge's overall pick | X (this one) | — |

The judge's first pass let a storage-layer defect in Y (a raw `KeyError`/`ValueError` leak on
malformed stored data, contradicting Y's own written error-handling contract) carry weight in its
overall pick — conflating a cheap, local bug with an architecture judgment. Asked to redo the
verdict separating "current defects, by fix cost" from "architecture, judged as if those defects
were fixed," the corrected pick is still X, but for a structural reason: Y's one class implementing
three storage interfaces is *why* the bug, the fat-interface issue, and the method-name smell all
exist, and undoing it means rebuilding what X's `Store` already is — whereas X's own misses are
each a cheap, local fix. Fixing Y's leak would not flip the pick. See
`results/blind-review-fixed-judge.md` for both the original and corrected FINAL sections, and the
README of `experiments/guide-vs-direct/` plus `FINDINGS.md` at the repo root for the fuller
synthesis across all pilots.
