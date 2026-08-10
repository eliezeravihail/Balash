# Balash experiment results — at a glance

**The question.** Does *making design the goal* — a Guide that hands a capable Worker a **design/quality
objective** (with the feature as a constraint), then evaluates and iterates — produce better-designed
software than a plain session handed the product goal directly?

**The method (identical each pilot).** Both conditions build the *same* product; **product information
is held constant** (both get the same facts), so any difference is attributable to *process*, not
knowledge. The two final codebases are judged **blind** (anonymized X/Y) by reviewers told to judge
design like Martin/Fowler/Metz — not to hunt bugs. Then the judge is **scrutinized, not trusted**:
every load-bearing claim is verified against the source, and a second reviewer with the **opposite**
disposition (pro-simplicity/YAGNI) re-judges to test whether the verdict is an artifact of taste.

## Scoreboard

| Pilot | Product (domain) | Executor model | Blind judge A (OO) | Blind judge B (simplicity) | Winner | Claims verified |
|---|---|---|---|---|---|---|
| **#1** | Task-manager CLI, 4 evolving stages (Python) | strong default | Balash ~70–75% | Balash ~60% | **Balash** | all ✓ |
| **#2** | Printable bingo-card generator (static web) | strong default | Balash ~8/10 | Balash ~65% | **Balash** | all ✓ |
| **#3** | Printable Sudoku generator (static web) | **Sonnet (Worker)** | Balash ~80% | Balash ~70% | **Balash** | all ✓ |

In every pilot, **both reviewers — with opposite dispositions — chose the Balash arm. Six blind reviews,
three domains, two executor tiers: six-for-six.** The verdict is robust to the judge's philosophy (the
failure mode we most worried about).

## The decisive finding is the same shape each time

Balash did **not** win by writing more code, or less. It won by getting the **proportionality right on
the one subtle design decision the feature framing glosses over** — the decision its design objective
explicitly asked the Worker to reason about:

- **Pilot #1 — wrote *less*.** The plain arm built a transitive cycle-detector for task prerequisites;
  the Balash arm reasoned that a cycle is structurally impossible (creation-time-only, immutable,
  backward-pointing edges) and enforced one existence rule instead. Both judges: the dead machinery is
  the wrong abstraction (Metz), so the point goes to Balash.
- **Pilot #2 — wrote *more, where it mattered*.** The plain arm builds bingo cards from per-card
  sub-seeds and *hopes* they differ — it can silently hand two players identical cards. The Balash arm
  made within-batch distinctness a first-class enforced guarantee (reject-and-redraw on a card
  fingerprint) and honestly reports when the word pool is too shallow.

Consistent secondary pattern: **Balash over-builds at the edges** (pilot #1: a boolean-as-enum, a
four-way JSON split; pilot #2: triplicated construction-token guards, a dead method). It is sound at
the center, ceremony at the seams — and both judges dock it for that. The plain arm is genuinely good
and wins the readability/size axis.

## Why the method plausibly causes it

The Balash handoff frames the objective as a **design outcome and names the hard decision to reason
about** ("what uniqueness do you guarantee?", "reason about whether a cycle can occur"). The plain
session, handed the feature, does the feature and moves past that decision. Making design the goal
surfaces the judgment the feature framing lets evaporate.

## What the pilots do NOT establish (honest limits)

- **Small N, one operator.** The same person ran both arms in every pilot. Operator bias is
  uncontrolled; the strongest next step is independent operators per arm.
- **Part of the win is the Guide's handoff** asking the right design question — that *is* the method,
  but it means the result reflects the objective's quality, not the Worker alone.
- **Balash is not strictly better** — it over-builds at the seams and loses on readability/size.
- **The judges are LLMs**, trusted only because their specific claims were source-verified each time.

## Pilot #3 — a weaker executor (Sonnet) still clears the bar

Pilot #3 repeated the method on a Sudoku generator with the **executing Worker on Sonnet** (Guide stayed
strong). **Both judges still chose Balash** (~80% / ~70%): the strong design objective carried the weaker
implementer — Sonnet built the hard invariant *by construction* (`Puzzle.tryCreate`, so a puzzle cannot
exist unless it has exactly one solution), the load-bearing evidence that a strong director carries a
weaker executor.

Honest caveats, and they matter: this was the **closest** pilot. Because uniqueness is *intrinsic* to
Sudoku, the plain Sonnet arm did not miss it (it enforced it too, by convention rather than construction),
so the win narrowed to *ownership quality*. The plain arm also shipped a **better product feature** (a
technique-based difficulty rater vs Balash's approximate given-count bands). And the Sonnet executor left a
**verified fidelity slip** — a dead `Difficulty.isSatisfiedBy` with a doc comment that overstates it — the
kind of ~5% conformance gap a weaker executor introduces. Bottom line: **good enough, with caveats.**

Per-pilot detail: [`design-first-vs-direct/`](design-first-vs-direct) (#1),
[`pilot2-bingo-web/`](pilot2-bingo-web) (#2), [`pilot3-sudoku-sonnet/`](pilot3-sudoku-sonnet) (#3).
