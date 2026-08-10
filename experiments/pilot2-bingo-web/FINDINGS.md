# Findings: pilot #2 — design-first (Balash) vs. a plain session, on a web product

Second pilot of the current thesis, on a deliberately **different domain** from pilot #1 (which was a
Python CLI). Here both arms built the same product — a standalone static-web **printable bingo-card
generator** (paste words → deterministic batch of printable cards; no gameplay). Product information
was held constant (both arms got the same facts). Method as in
[`../design-first-vs-direct/CHARTER.md`](../design-first-vs-direct/CHARTER.md): build both arms,
judge blind, then scrutinize the judge.

Private key: **X = balash-arm** (design-first: a design objective, evaluated, then an implementation
that conformed to it), **Y = direct-arm** (plain session handed the requirement).

## The two codebases

| | X — Balash (design-first) | Y — plain session |
|---|---|---|
| JS (excl. tests) | ~767 lines, `src/core/` of 8 concept modules + edge | ~420 lines, 2 files (`bingo.js` + `app.js`) |
| Core tests | 19 | 13 |
| Concepts | real types: `WordList`, `GridSize`, `Card`, `CardSet`, `Seed` | free functions over plain objects/arrays |
| Distinctness | enforced in `CardSet` (reject-redraw on fingerprint) + truncation reported | none — per-card sub-seed, cards can collide silently |

## Result: both blind judges, opposite dispositions, chose X (Balash)

- **Judge A (pure OO-quality prior):** X better designed, **~8/10, "not a close call."**
- **Judge B (pro-simplicity / YAGNI prior):** X better designed, **~65%** — stated "as someone
  actively looking to punish X for its file count," and did dock it.

Both landed on X. As in pilot #1, the verdict is **robust to the judge's philosophy**.

## The decisive difference is substantive and source-verified — not "more types"

Both judges converged, independently, on one point: **the plain arm can silently hand two players
identical bingo cards.** Y builds exactly `cardCount` cards from per-card sub-seeds and *hopes* they
differ — there is no fingerprint check, no dedupe, no "can't make that many distinct" outcome (with 9
words → 3×3, two identical cards can come out undetected; its passing "cards differ" test passes
probabilistically, not by construction). X made distinctness a first-class enforced guarantee owned in
one place (`CardSet.build`: reject-and-redraw on `fingerprint`, a permutation ceiling, and
`isTruncated`/`producedCount` reporting). [`claim-verification.md`](claim-verification.md) confirmed
this and every other load-bearing claim against the source. For a *batch* product this is a real design
gap with a product consequence, not a stylistic preference.

Judge B named the hinge honestly: the verdict turns on whether within-batch distinctness is a real
requirement. For a batch of bingo cards handed to a group, it is (two identical cards = two players win
at once). Both judges judged it real.

## Why the method plausibly caused it (mechanism, H2)

The Balash design objective explicitly named *"how cards are made distinct and what uniqueness you
guarantee"* as a design decision the Worker had to own; the design Worker reasoned it out (no two
identical; stop at the max producible; report truncation — never pad, never loop), and the
implementation conformed. The plain session, handed the feature, produced cards by sub-seed and moved
on. **Making the design the goal surfaced a guarantee the feature framing let evaporate.**

*Framing caveat (added on review):* this makes pilot #2 a weaker example of "product info held
constant, so the win is pure process" than first stated. Product *facts* were held constant (both arms
knew it was a batch for a group), but the Balash handoff explicitly asked "what uniqueness do you
guarantee?" and the plain arm was never asked. So part of the win is the Guide *posing that design
question* — design-level discovery, not "same information, better design." That is arguably a *more*
valuable capability of the method, but it is a different claim; do not read pilot #2 as discovery being
fully neutralized. Pilot #3 (both arms independently confronted the hard invariant) is the cleaner test
of "same understanding, better structural owner."

## Honest counter-evidence (Balash over-built at the edges — again)

Both judges docked X for real over-engineering, verified in source: the **triplicated `Symbol`
construction-token guards** on `GridSize`/`Seed`/`WordList` (library-grade defense a single static page
doesn't need), a **dead `WordList.supports()`**, and an overflow-cap guarding `Number.MAX_SAFE_INTEGER`
in a print tool. Both said they'd delete these. X is sound at the center, ceremony at the seams; Y's
leanness is the correct instinct for the size, and Y wins the "hold it in your head in five minutes"
axis outright.

## Cross-pilot synthesis (now N = 2, on two very different domains)

| | Pilot #1 (Python task CLI) | Pilot #2 (JS static web bingo) |
|---|---|---|
| Both judges (opposite priors) chose | Balash | Balash |
| Confidence (A / B) | ~70–75% / ~60% | ~80% / ~65% |
| Decisive design call | Balash **didn't build** dead cycle-detection; plain arm did | Balash **did enforce** a real distinctness guarantee; plain arm didn't |
| Balash's edge-ceremony (docked) | Readiness enum, four-way JSON split | Symbol-token guards, dead `supports()` |
| Judge claims vs. source | all verified | all verified |

The consistent, non-obvious pattern across both domains: **design-first didn't win by writing more code
or less — it won by getting the *proportionality right on the one subtle design decision the feature
framing glosses over.*** Once that decision showed cycles were impossible, design-first wrote *less*
(no DFS); once it showed a batch needs a distinctness guarantee, design-first wrote *more* (an enforced
one). In both, the design-objective handoff had explicitly asked the Worker to reason about exactly
that decision. And in both, design-first paid an edge tax of speculative ceremony the plain arm avoided.
The verdict was robust to opposite judging philosophies both times.

## What this does and does not establish

**Does:** On two products in two languages/paradigms, with product information held constant, the
design-first process produced the better-designed codebase under two opposite judging philosophies, and
did so by right-sizing the subtle, product-consequential design decision — a mechanism now visible and
source-verified in two independent cases.

**Does not** prove the thesis. Limits, unchanged and honestly stated:
- **N = 2, one operator.** I ran both arms in both pilots. Operator bias is uncontrolled; the strongest
  next step is independent operators per arm.
- **Part of the win is the Guide's handoff** asking the right design question. That *is* the method
  (making design the goal), but it means the result reflects the quality of the objective, not the
  Worker alone.
- **Balash is not strictly better:** it over-builds at the edges in both pilots and loses the
  readability/size axis; the plain arm is genuinely good.
- **The judges are LLMs**, trusted only because their specific claims were source-verified each time.

Two pilots, two domains, both converging under opposite judge priors with verified claims, is a
meaningfully stronger signal than one — but it is a signal, not a validated result.
