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

In every pilot, both reviewers — with opposite dispositions — chose the Balash arm. Read that as **three
experimental units, each with its verdict robustness-checked**, not as six independent wins: the two
judges in a pilot read the *same* two codebases, so they test whether the verdict is a taste artifact
(the failure mode we most worried about), not whether the effect replicates. Replication is the count of
*pilots* — three, on three domains — and the honest strength of the evidence is less the tally than the
**sequence** below.

### The strongest evidence is the sequence, not the tally

The same idea shows up three different ways — which is harder to explain by chance than a raw win count:

- **Pilot #1 — needed *less* mechanism.** The plain arm built a cycle-detector; Balash reasoned cycles
  were impossible and enforced one existence rule. (Balash *removed* machinery.)
- **Pilot #2 — needed *more* guarantee.** The plain arm let batch cards silently collide; Balash made
  distinctness an enforced guarantee. (Balash *added* a guarantee.)
- **Pilot #3 — same guarantee, *better owner*.** Both arms enforced the one-solution invariant; Balash
  made it true *by construction* (`Puzzle.tryCreate`) where the plain arm held it by convention.

Three manifestations of one thing: **when design is the goal, the agent spends cognition on "where should
this truth live?" instead of only "how do I make the feature pass?"** That is the result worth taking
seriously.

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

Consistent secondary pattern, and it is a real defect in the method, not noise: **Balash over-builds at
the edges in all three pilots** (pilot #1: a boolean-as-enum, a four-way JSON split; pilot #2: triplicated
construction-token guards, a dead method; pilot #3: a data-only `PuzzleBatch` class, an over-built
`Difficulty` API, a dead `isSatisfiedBy`). Sound at the center, ceremony at the seams — both judges dock
it every time, and the plain arm wins the readability/size axis. This replicated failure is why the skill
now carries a mandatory **subtractive pass** (`references/review.md`): for every abstraction, name the
present product force that requires it, and delete the ones whose removal wouldn't damage a current
rule/invariant/boundary.

**Design quality is not product quality.** Pilot #3 made this sharp: the plain arm shipped a genuinely
better *product* (technique-based difficulty) while losing on *design*. Future pilots should carry **two
separate verdicts — a product-outcome verdict and a design-outcome verdict — never merged into one
score.** Winning design while losing product is a possible and important outcome.

## Why the method plausibly causes it

The Balash handoff frames the objective as a **design outcome and names the hard decision to reason
about** ("what uniqueness do you guarantee?", "reason about whether a cycle can occur"). The plain
session, handed the feature, does the feature and moves past that decision. Making design the goal
surfaces the judgment the feature framing lets evaporate.

## What the pilots do NOT establish (honest limits)

- **Same operator ran both arms — now the primary threat.** One person ran Balash *and* the plain arm in
  every pilot. Until arms are run by isolated operators, this is the biggest hole in the evidence.
- **Only pilot #1 was an evolving product.** Bingo and Sudoku are essentially one-shot builds. So the
  pilots support "design-first improves the *initial* design"; they barely touch Balash's bigger claim,
  "design-first *preserves* quality as the product changes over hidden stages" — that has one data point.
- **Part of the win is the Guide's handoff** naming the hard decision (e.g. "what do you guarantee?").
  That *is* the method, but the pilot #2 win is therefore not "product info held constant, pure better
  design" — it is partly Balash surfacing a latent guarantee. Real value, arguably larger, but a
  different claim than "discovery was neutralized."
- **Balash is not strictly better** — it over-builds at the seams (3/3) and loses on readability/size,
  and can lose on product quality (pilot #3) while winning design.
- **The Sonnet result is narrow.** It shows `strong-Guide + Sonnet-Worker > plain-Sonnet`. It does *not*
  show that beats "run a strong model on the whole task"; that needs a `strong-direct` vs
  `strong-Guide + cheap-Worker (+ strong review)` comparison on both cost *and* the two verdicts.
- **The judges are LLMs**, trusted only because their specific claims were source-verified each time.

### The highest-value next experiment

Stop producing more same-type one-shot pilots. The next one worth running is a single, stronger study:
**isolated operators per arm; a new product; several hidden changes over time** (to test quality *under
evolution*, Balash's real claim); a **product verdict kept separate from the design verdict**; and an
**explicit check of the edge-over-engineering** that recurred 3/3. If Balash still wins there, the claim
becomes materially more serious.

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
