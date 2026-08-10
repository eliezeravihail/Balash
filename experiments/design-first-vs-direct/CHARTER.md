# Experiment charter: design-first (Balash) vs. a plain session

This is the charter for the experiment that tests the **current** Balash thesis — the one after the
pivot to *design as a first-class goal*. It states, up front and honestly, **what we are trying to
show** and **how we intend to show it**, including how we guard against fooling ourselves. It is
written before the comparison is complete, so it commits us to a method rather than letting the
method be chosen after the result is known.

Read this together with:
- the skill it tests — [`../../skills/balash-guide/`](../../skills/balash-guide) (`SKILL.md` and its
  `references/`, especially `design-principles.md`, the standard "good design" is judged against);
- the earlier, differently-framed pilots — [`../guide-vs-direct/FINDINGS.md`](../guide-vs-direct/FINDINGS.md)
  and [`../discovery-tuning-v3-vs-v3.1/`](../discovery-tuning-v3-vs-v3.1) — whose main lesson (the
  blind judge is unreliable without ground truth) directly shapes the judging method below.

## What we are testing (the hypotheses)

**H1 — primary.** Across an *evolving* product, a session with Balash installed produces
**better-designed** code than a plain session that receives the same product goals directly.

- "A session with Balash installed" = the `balash-guide` skill drives the work: the Guide grounds
  product behavior with focused questions, formulates **one design/quality objective at a time**,
  delegates implementation to a Worker framed around that design outcome, verifies the evidence, and
  chooses the next objective — the design→implement rhythm, not a feature ticket.
- "A plain session" = a capable coding agent receives each stage's product requirement verbatim and
  builds it, free to refactor as it goes. No design-objective framing, no discovery gate.
- "Better-designed" is defined **only** by [`design-principles.md`](../../skills/balash-guide/references/design-principles.md)
  — single responsibility, genuine (not costume) interfaces, a domain that owns its rules, no leaky
  storage abstractions, tell-don't-ask, no primitive obsession, change locality, and the right
  duplication-vs-abstraction trade-off (Metz: the wrong abstraction is worse than duplication). It is
  **not** defined by bug count, test count, lines of code, or architectural sophistication for its
  own sake.

**H2 — mechanism.** The advantage, if any, comes from *making design the goal*, not from Balash
merely having more information. Specifically: because a sound design is reached and evaluated as its
own objective before implementation, new capabilities added in later stages **conform to that design
instead of eroding it** — where a plain session, optimizing each stage's feature, lets design become
whatever survives shipping.

**H0 — the null we must be willing to accept.** It is a real possible outcome that the two are
**indistinguishable** on design at this scale, or that the plain session's later refactors close the
gap. The charter commits us to reporting that if it happens, not to manufacturing a winner. A single
pilot is a *signal, not proof*.

## How we test it

### The product (same as prior pilots — one oracle)

A task-management CLI evolved through **four previously-hidden stages**, each introducing a genuine
change of a different kind:

1. CRUD + persistence (create/assign/status/list; survive restart).
2. AI-agent assignees (a task may be assigned to a human member *or* an AI agent; agents execute and
   produce results).
3. A second storage backend (the store must be swappable without the core knowing).
4. Task prerequisites (a task may be blocked by others; cycles are invalid).

The stages are hidden from both conditions until reached — this is the anti-waterfall crux: neither
condition may design stage *N+1* into stage *N*. A stage introduces a *new axis of change*, and good
design is precisely what makes that cheap.

### The oracle (ground-truth product facts)

The operator holds a fixed set of product facts (identity rules, append-vs-overwrite, cycle
handling, migration expectations, …) recorded in [`logs/architect-questions.md`](logs/architect-questions.md).
**Both** conditions may ask product questions; the oracle answers from this fixed set and never
volunteers a fact that was not asked. The oracle exists so the judge can later tell a *correct but
unstated* decision apart from *over-engineering* — the distinction the earlier pilots proved a blind
judge cannot make on its own.

### The two conditions

- **Balash arm** — [`balash-arm/`](balash-arm): the skill drives the loop; the operator plays
  product owner (answers oracle questions) and relays design objectives to a Worker; each stage is
  evaluated before the next. Design objectives are captured as `DESIGN_STAGE*.md` artifacts and the
  staged code is tagged per stage.
- **Direct arm** — `direct-arm/` (to be built): a plain coding session receives each stage's
  requirement verbatim and implements it, free to refactor. Same four stages, same oracle available
  on request.

Both arms produce a final codebase after stage 4. Those two codebases are the objects of judgment.

### The judge — and why we do not trust it blindly

Design quality is scored by a **blind reviewer** (`judge/design-quality-brief.md`) that sees both
final codebases anonymized as X and Y, does **not** know which is which, and is instructed to judge
design the way Martin, Fowler, and Metz would — **not** to hunt bugs, count crashes, or estimate fix
cost. That brief is deliberately plain-language and avoids checkbox metrics that get ticked without
understanding.

But the central lesson of the prior pilots is that **the judge itself is fallible**, so a single
blind verdict is not the result. Every verdict is subjected to critical scrutiny of the judge:

1. **Oracle reconciliation.** Re-run the judge (or a second reviewer) *with* the oracle facts, and
   ask specifically whether anything it called "over-engineering" is in fact a correct response to a
   product fact it did not know — and whether anything it praised as "simple" is actually a silent
   product guess.
2. **Claim verification against source.** Every concrete claim the judge makes ("this is a one-line
   fix", "nothing else could implement this interface", "this rule is enforced in one place") is
   checked against the actual code. We already caught one such claim being false in a prior run — a
   judge asserted a defect was a trivial fix when the code had five independent call sites and no
   central point to fix. A judge's *self-correction* is verified too, not taken on faith.
3. **Instrument disclosure.** We record where the judge's reasoning did **not** survive (1) and (2),
   and weight the verdict accordingly. If the judge cannot be made reliable for a given claim, we say
   so rather than reporting its verdict as fact.

### What counts as a result

A finding is reportable only as: *the blind judge preferred X's design for reasons A, B, C; on oracle
reconciliation reasons A and C survived and B did not (B was a correct-but-unstated decision); on
source verification all three of X's cited examples checked out.* A bare "X won" is not a result.
Confidence is stated explicitly, and "genuinely too close to call on design" is an allowed and
honest outcome.

## Status

- Balash arm: built and self-verified through **stage 3** (SQLite backend behind a storage boundary,
  core untouched; 92 tests green). Stage 4 pending.
- Direct arm: **not yet built**.
- Blind judge + judge-scrutiny pass: **not yet run** for this framing.

This charter is committed before those steps so the method is fixed in advance.
