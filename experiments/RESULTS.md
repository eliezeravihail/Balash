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
| **#4** | RoomBook booking core, 4 evolving stages, **isolated operators** | strong (both) | **design → Balash** (2 opp. judges, "clear") | **product → Direct** (clear) | **split** | all ✓ (probed) |

In pilots #1–#3 both reviewers — with opposite dispositions — chose the Balash arm. Read that as **three
experimental units, each with its verdict robustness-checked**, not as six independent wins: the two
judges in a pilot read the *same* two codebases, so they test whether the verdict is a taste artifact
(the failure mode we most worried about), not whether the effect replicates. Replication is the count of
*pilots*, and the honest strength of the evidence is less the tally than the **sequence** below.

**Pilot #4 is the important one, and it did not sweep.** It is the first pilot with isolated operators,
an evolving product, and *separate* design / product verdicts — and the arms **split**: the two
opposite-disposition judges chose Balash for **design** (clear), while a blind product assessor chose
Direct for **product** (clear). Design-first produced the deeper design (it saw the Stage-4 cross-room
person-rule *falsify* the "rooms are independent" assumption, fused both conflict rules into one owned
predicate, and *deleted* the now-false per-room partition) — and, by the *same* minimalist discipline,
shipped two real bugs and cut a real affordance (a broken cross-room waitlist promotion; a series that
books backwards on a negative stride; no way to inspect the waitlist). This is the "win design, lose
product" outcome the method can produce, now demonstrated rather than hypothesized — the reason the two
verdicts must never be merged. See [`pilot4-roombook-evolving/FINDINGS.md`](pilot4-roombook-evolving/FINDINGS.md).
Notably, pilot #4 is the first run *after* the skill gained its mandatory **subtractive pass**, and the
edge-over-engineering that recurred in #1–#3 **reversed**: the blind edge auditor found the *Direct* arm
carried the ceremony this time and the Balash arm was leaner (n=1, suggestive).

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

- **Operators: improved in pilot #4, not yet fully controlled.** Pilots #1–#3 had one operator run both
  arms. Pilot #4 ran the arms as **two isolated agent contexts** that never saw each other — but one
  orchestrator still authored both arms' stage prompts from identical spec text. Genuine independent
  human operators remain the stronger control.
- **Evolving product: now two pilots (#1, #4), still small.** Bingo and Sudoku are one-shot builds. The
  "design-first *preserves* quality as the product changes over hidden stages" claim rests on #1 and #4.
- **Part of the win is the Guide's handoff** naming the hard decision (e.g. "what do you guarantee?").
  That *is* the method, but the pilot #2 win is therefore not "product info held constant, pure better
  design" — it is partly Balash surfacing a latent guarantee. Real value, arguably larger, but a
  different claim than "discovery was neutralized."
- **Balash is not strictly better — and pilot #4 proves it can lose product while winning design.** In
  #1–#3 it over-built at the seams and lost on readability/size; in #4 it shipped two real bugs and cut a
  real affordance by the same minimalist discipline that won the design. Design quality ≠ product quality.
- **Within-arm role separation was not enacted in #4.** One agent played both Guide and Worker there; the
  design-first cognition was present but the Guide→Worker delegation of #1–#3 was not.
- **The Sonnet result is narrow.** It shows `strong-Guide + Sonnet-Worker > plain-Sonnet`. It does *not*
  show that beats "run a strong model on the whole task"; that needs a `strong-direct` vs
  `strong-Guide + cheap-Worker (+ strong review)` comparison on both cost *and* the two verdicts.
- **The judges are LLMs**, trusted only because their specific claims were source-verified each time.

### Next steps the pilots now point to

Pilot #4 ran the "isolated operators + evolving product + separate verdicts + edge-audit" study the
earlier results called for. What it surfaced sets the next questions: (1) restore the **Guide→Worker
delegation** inside the Balash arm (it was collapsed to one agent in #4) and re-check whether the product
bugs persist when a Worker executes a Guide's explicit exit criteria; (2) **genuinely independent
operators** (not one orchestrator authoring both prompts); (3) confirm the **subtractive-pass reversal**
of edge-over-engineering on more than one pilot; (4) the standing **cost** comparison —
`strong-direct` vs `strong-Guide + cheap-Worker + strong review`.

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
