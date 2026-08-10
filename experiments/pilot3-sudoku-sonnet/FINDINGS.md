# Findings: pilot #3 — design-first (Balash) vs. a plain session, with a **Sonnet executor**

The question this pilot adds: **does Balash still clear the bar when the executing Worker is a weaker
model?** Same method as pilots #1–2, same domain family as #2 (a static-web generator), but this time
both arms' **executing agents ran on Sonnet**, while the Guide (design direction) stayed strong. The
product: a deterministic printable **Sudoku generator**. The hard invariant: **every puzzle has exactly
one solution.** Private key: **X = direct-arm** (plain Sonnet session), **Y = balash-arm** (a strong
design objective, implemented by Sonnet Workers).

## Result: both blind judges, opposite dispositions, chose Y (Balash) — again, but closer

- **Judge A (OO prior):** Y better, **~80%.**
- **Judge B (pro-simplicity prior):** Y better, **~70%** ("not a blowout").

Three pilots, three domains, six blind reviews across two opposite dispositions — **all six chose the
Balash arm.** So the headline answer to the question is: **yes — with a Sonnet executor, design-first
still produced the better-designed codebase.** The strong design objective carried the weaker
implementer: Sonnet, handed the objective, correctly built the invariant *by construction*
(`Puzzle.tryCreate` + a private `CREATE_GUARD` symbol → a puzzle that cannot exist unless it has exactly
one solution), which is precisely the hard thing the design named.

## But this was the closest pilot, and honesty requires the caveats

**The plain Sonnet arm was genuinely strong — and here it did NOT miss the hard invariant.** Unlike
pilots #1–2 (where the plain arm missed the subtle guarantee), uniqueness is *intrinsic* to Sudoku — you
cannot build a generator without confronting it — so the plain arm enforced it too, just **by convention**
(gated inside its digging loop, shipping a bare-array puzzle) rather than **by construction**. The
decisive axis therefore shifted from "did they get the invariant" to "who *owns* it": Y makes the illegal
state unrepresentable; X relies on a routine's discipline. Both judges still gave this to Y, but it is a
narrower, more design-purist win than before.

**The plain arm shipped a better product feature.** Both judges credited X's ~170-line technique-based
difficulty rater (Easy = provably solvable by singles, no guessing) as genuinely better than Y's
admittedly-"approximate" given-count bands. On *product*, X arguably leads; on *design*, Y leads.

**The Sonnet executor left one verified design-conformance failure.** Judge B caught — and
source-verification confirmed — that Y's `Difficulty.isSatisfiedBy` is **dead in production**: the design
specified the generator would "ask Difficulty to judge," the Sonnet Worker built the method, but then
wired the generator to compare `difficulty.min/max` inline and left `isSatisfiedBy` used only by tests,
with a doc comment that overstates reality. That is the honest statement — *one verified conformance
failure*, not a "~95% conformance / 5% gap" (there is no measurement that produced such a number, and
inventing quality percentages is exactly what this project exists to avoid). It did not sink the design,
and both judges also flagged Y's other edge-ceremony (a data-only `PuzzleBatch` class, an over-built
`Difficulty` API, an immutable `Grid.withCell` copying 81 cells in the solver's hot path).

**Follow-up — the "cheap Worker + strong review" policy caught and fixed it.** A separate strong-model
design-fidelity review was then run over this same Sonnet arm (see
[`../../skills/balash-guide/references/review.md`](../../skills/balash-guide/references/review.md),
"Mixed-tier execution"). It found *exactly* this one gap and no invented others, routed the generator
through `difficulty.isSatisfiedBy` so the ownership the design claimed became real, added a regression
test (16 pass, was 15), and confirmed the one-solution invariant and the seams were untouched. So the
conformance failure a cheaper executor introduced was repairable at *review* cost — direct evidence for
the policy, though a single case, not a validated cost model. (The judged arm in this folder is kept as
the pre-review artifact; the fix lives in the working copy.)

## Cross-pilot synthesis (now N = 3, three domains, two executor tiers)

| | #1 Task CLI (Python) | #2 Bingo (web) | #3 Sudoku (web), **Sonnet executor** |
|---|---|---|---|
| Both opposite-prior judges chose | Balash | Balash | Balash |
| Confidence (A / B) | 75% / 60% | 80% / 65% | 80% / 70% |
| The subtle design decision | cycles impossible → **no DFS** (wrote less) | batch distinctness → **enforced** (wrote more) | uniqueness → **owned by construction** vs by convention |
| Plain arm's handling of it | built dead machinery | omitted the guarantee | got it, but by convention |
| Balash's edge weakness (docked) | Readiness enum, JSON split | token guards, dead method | dead `isSatisfiedBy`, `Grid` hot-path copy |
| Judge claims vs. source | all verified | all verified | all verified |

**Six-for-six across opposite dispositions and three domains** is a materially stronger signal than any
single pilot. The consistent mechanism holds: design-first wins by right-sizing (or properly owning) the
one design decision the feature framing glosses over — and it consistently pays an edge tax of ceremony.
Pilot #3 adds two honest refinements: (a) when the hard decision is *intrinsic* to the domain (Sudoku
uniqueness), the plain arm won't miss it, so the win narrows to *ownership quality*; and (b) a **Sonnet
executor is good enough** to realize a strong design objective — including its hardest invariant — while
introducing small conformance gaps a stronger executor might avoid.

## Answer to the question asked ("is it still good enough with Sonnet?")

**Yes, with caveats.** Design-first with a Sonnet Worker still produced the better-designed codebase under
both judging philosophies, and Sonnet correctly implemented the design's hard invariant-by-construction —
the load-bearing evidence that a strong director carries a weaker implementer. The caveats are real and
worth stating: the margin narrowed against a strong plain-Sonnet arm that also shipped a better difficulty
feature, and the Sonnet executor introduced a verified fidelity slip (a dead abstraction with a misleading
comment). Still **N small, one operator** — a strengthening signal, not proof.
