# Findings: design-first (Balash) vs. a plain session

One pilot, run per the [`../CHARTER.md`](../CHARTER.md). Two conditions built the same task-manager CLI
through the same four staged requirements, with **product information held constant** (both arms got
the same oracle facts, so any design difference is attributable to *process*, not discovery). The two
final codebases were judged blind, and the judge was then scrutinized rather than trusted.

Private key: **X = direct-arm** (plain session), **Y = balash-arm** (design-first).

## The two codebases

| | Y — Balash (design-first) | X — plain session |
|---|---|---|
| Production code | ~2,240 lines, ~30 files, layered | ~1,075 lines, 7 flat files |
| Tests | 110 (both backends) | 87 (both backends) |
| Storage | 4 per-entity ports + aggregate; real relational columns | one `load()/save(State)` interface; whole-state read/write |
| Domain | encapsulated objects, first-class id/status/prereq types | mutable dataclasses, bare `int`/`str` ids |
| Cycle rule | reasoned cycles impossible; enforced one existence rule | built transitive DFS cycle detection |

## Result: both blind judges, opposite dispositions, chose Y

The verdict was tested for the failure mode the user flagged — *a judge biased by its own
philosophy*. Two independent blind reviews were run with deliberately opposite priors:

- **Judge A (pure OO-quality prior):** Y better designed, **~70–75%** confidence. Y strong on 6/8
  questions, even on 2/8.
- **Judge B (pro-simplicity / YAGNI prior — "abstraction guilty until proven innocent"):** Y better
  designed, **~60%** confidence. A genuine close call, explicitly *not* awarded for Y being bigger.

**Both dispositions land on Y.** The verdict is robust to the judge's philosophy — the thing we were
most worried about. The margin is "moderate, not a rout," and both judges docked Y for real ceremony.

## The single most decisive, disposition-independent finding

On the prerequisite-cycle requirement, **the design-first arm wrote *less code* by reasoning, and the
plain arm wrote *more* dead machinery.** X built a transitive DFS cycle detector (`manager._reaches`);
Y reasoned that cycles cannot form (prerequisites are creation-time-only, immutable, and reference
existing tasks, so every edge points strictly backward) and enforced the single existence rule
instead. Both judges — including the YAGNI-hardline one — called this **clearly Y's**, because X's
detector guards a state its own rules make unreachable: the textbook wrong abstraction.

This is the cleanest evidence for the mechanism the experiment set out to test (H2). And it plausibly
traces to the method: the Balash Worker's handoff was a *design objective* that explicitly asked it to
"reason about whether a cycle can actually arise and design proportionately"; the plain session got
the product requirement "a cycle is invalid and must be rejected" and dutifully built a rejecter.
Making design the goal surfaced a judgment that the feature framing did not.

## Honest counter-evidence (the plain session was not simply worse)

The adversarial judge surfaced genuine points **for X** that the first judge missed:

- **X's `Status` is a stronger invariant** — `Status.next()` is forward-only (todo→in_progress→done,
  no skip, no regress). Y's `change_status` allows any transition. On this value object X guards more.
- **X has whole-state write atomicity**; Y's four separate JSON repositories each rewrite their own
  file, so Y *gave up* the cross-entity atomicity X gets for free from one `save(State)`.
- **X contains two masterclasses in minimal sufficient abstraction** — the `TaskStore` load/save-State
  contract and the `AgentRunner = Callable[...]` seam (four lines) that Y models with a whole package.

And Y carries real dead weight both judges would cut: a `Readiness` enum that is a `bool` with a
label; a four-way JSON repository split that pays on SQLite but not on JSON; a speculative
`TaskService`/`ExecutionService` split; some Member/Team scope beyond what was asked.

The fair synthesis (Judge B's words): **X's defects are structural (an anemic, mutable `Task` that
can't guard itself; a fat `TaskManager` holding rules the domain should own; storage serialization
bleeding into the domain); Y's defects are decorative (ceremony confined to the edges, sound at the
center).** That asymmetry — structural weakness vs. cosmetic over-build — is why both judges lean Y.

## Was the judge itself trustworthy this time?

Per the charter, the verdict is only a result if the judge's concrete claims survive verification.
[`claim-verification.md`](claim-verification.md) checked all seven load-bearing claims against source:
**all seven verified**, in both directions (criticisms of X, criticisms of Y, and praise of Y). This
is the opposite of the earlier `guide-vs-direct` pilot, where a judge's "one-line fix" claim proved
false. Oracle reconciliation moved nothing (nothing scored as "over-engineering" was a product-
mandated behavior; nothing scored "simple" was a silent product guess). The instrument was reliable
*here* — but we say so because we verified it, not on its authority.

## What this does and does not establish

**Does:** In this pilot, with product information held constant, the design-first process produced the
better-designed codebase under two opposite judging philosophies, and produced the more *proportionate*
design on the one question (cycles) where proportionality was directly tested — writing less by
reasoning instead of more by defending.

**Does not:** prove the thesis. Real limits, stated plainly:
- **N = 1.** One product, four stages, one operator (the same person ran both arms), one model family.
  A signal, not a validated result.
- **A built-in asymmetry that *is* the method but must be named:** the Balash arm's advantage on the
  cycle question came partly because its design-framed handoff asked the proportionality question the
  plain arm was never asked. That is exactly what "make design the goal" is supposed to do — but it
  means the result partly reflects the quality of the handoff, i.e. the Guide, not the Worker alone.
- **Y is not strictly better:** it conceded atomicity and a stronger status invariant to X and carries
  cuttable ceremony. "Better designed overall" is not "better on every axis."
- **The judges are LLMs.** We trust this verdict only because its specific claims were source-verified;
  we do not extend that trust to the instrument in general.

The honest bottom line: this is the first comparison under the *current* thesis, and it points the
right way — moderately, robustly to judge disposition, and with the mechanism (design-as-goal → more
proportionate design) visible in a concrete, verified case. It earns a second pilot on a different
product, ideally with the two arms run by different operators, before it is called more than a signal.
