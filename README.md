# Balash

`Balash` is a **Claude Code plugin** that keeps coding-agent work pointed at the right engineering
objective as a product evolves, by separating *what to optimize now* (the Guide) from *how to
implement it* (a delegated Worker), and by refusing to let unresolved product decisions get
silently guessed. Its aim is to make *design* the goal handed to the agent, not a review applied
after the fact.

This is a pivot. An earlier deterministic static-analysis CLI also lived under this name; it is
no longer the subject of this repository, and is not carried forward here.

## How it stays on without you doing anything

The plugin has two parts that work together:

- The **`balash-guide` skill** is *model-invoked*: Claude reads its `description` and enters it on
  its own whenever you build or materially evolve software — no slash command, the same way a
  UI-design skill triggers on a UI request.
- A **`UserPromptSubmit` hook** (`hooks/inject-goal.py`) fires on *every* turn, reads the project's
  `.balash/state.md`, and injects the current design objective back into context. This is what
  stops the goal from being forgotten when the conversation drifts onto something unrelated: a
  skill alone is re-evaluated per turn and its body isn't in context on an off-topic turn, so the
  durable objective has to live outside the conversation (in `state.md`) and be re-surfaced by
  something that always runs (the hook). On any project without a `.balash/state.md`, the hook is
  silent.

So the objective lives in `.balash/state.md`, not the chat; the skill supplies the method; the hook
keeps the goal present. Advancement is triggered either automatically (a Worker subagent returning)
or explicitly (`balash next`).

## Two ways to run it: automatic, or phase by phase

The same loop runs two ways, recorded in the `Mode` field of `.balash/state.md`
([`skills/balash-guide/references/modes.md`](skills/balash-guide/references/modes.md)):

- **Automatic** (default) — the Guide drives the whole loop end to end and pauses only for an *open
  product decision* it must not guess or for *receiving the next product change*. `/balash-auto`.
- **Stepped** — for when you want to supervise. The loop stops at every phase boundary and advances
  only on an explicit command, so you can inspect and edit between phases:
  - `/balash-plan` — choose one design objective and draft the Worker handoff; **stops before writing
    any code**, so you can approve or edit the objective first.
  - `/balash-build` — delegate the planned objective to a Worker; stops when it returns.
  - `/balash-review` — evaluate the result with the **review panel** and stop with reproduced findings,
    a verdict, and a recommendation.

The review panel ([`references/review-panel.md`](skills/balash-guide/references/review-panel.md)) is
scrutiny, not scoring: adversarial probes against the objective's exit criteria, where **every finding
carries a reproduction (a failing probe / concrete input→wrong output) or a `file:line` citation — never
a score**. `/balash-review` also runs **standalone on any diff, branch, or PR** that Balash did not
build, as a general review tool. (In pilot #4 this panel is exactly what caught the shipped bugs a
design-only judgment missed — see [`experiments/RESULTS.md`](experiments/RESULTS.md).)

## Layout

- [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) — the plugin manifest.
- [`skills/balash-guide/`](skills/balash-guide) — the skill itself: `SKILL.md`, its `references/`
  (discovery, objective selection, reviewing Worker evidence, the Worker handoff shape), and the
  `.balash/state.md` template it maintains per project.
- [`hooks/`](hooks) — `hooks.json` and the `UserPromptSubmit` script that re-injects the current
  objective (and, in stepped mode, the stop-policy) every turn.
- [`commands/`](commands) — the phase commands for stepped mode: `/balash-plan`, `/balash-build`,
  `/balash-review` (also a standalone reviewer for any diff/PR), and `/balash-auto`.
- [`experiments/guide-vs-direct/`](experiments/guide-vs-direct) — the pilot protocol and evidence
  comparing Guide-led development against a coding agent that receives requirements directly, plus
  a controlled test of what it takes to *review* the result honestly (a blind judge needs
  ground-truth product facts to tell "correct but unstated" apart from "over-engineered," and even
  then it still misses defects that a real static-analysis pass catches in seconds). Start at
  [`experiments/guide-vs-direct/FINDINGS.md`](experiments/guide-vs-direct/FINDINGS.md).

## Experiments

- [`experiments/design-first-vs-direct/`](experiments/design-first-vs-direct) — the **current**
  experiment for the post-pivot thesis (design as the goal). Its [`CHARTER.md`](experiments/design-first-vs-direct/CHARTER.md)
  fixes, in advance, what is being tested and how — including how the quality judge is scrutinized
  rather than trusted. The Balash arm is built and self-verified through stage 3; the plain-session
  arm and the blind judge pass are still to come, so **no comparison result exists yet** for this
  framing.
- [`experiments/guide-vs-direct/`](experiments/guide-vs-direct) and
  [`experiments/discovery-tuning-v3-vs-v3.1/`](experiments/discovery-tuning-v3-vs-v3.1) — earlier,
  differently-framed pilots. Their main lesson (a blind LLM judge cannot tell "correct but unstated"
  from "over-engineered" without ground-truth product facts) directly shaped the judging method in
  the current charter.

## Status

**[`experiments/RESULTS.md`](experiments/RESULTS.md) is the clear at-a-glance summary of all pilots.**

Four completed pilots under the current thesis. Pilots #1–#3 all pointed one way (design-first won a
blind design verdict on three domains); **pilot #4 — the strongest design — deliberately split them
apart and did not sweep.** The strongest evidence from #1–#3 is the *sequence*: Balash needed *less*
mechanism (#1), *more* guarantee (#2), and gave a shared guarantee a *better owner* (#3) — three faces
of "when design is the goal, the agent asks where a truth should live." Pilot #4 then tested that under
**isolated operators, an evolving product, and separate design/product verdicts** — and found design-first
still wins *design* (it deleted a structural assumption a new invariant had falsified) but **loses
*product*** here, shipping two real bugs and cutting an affordance by the very same minimalist discipline.
That "win design, lose product" split is the honest headline, and it is why the two verdicts are scored
separately. The completed pilots:

- [`experiments/design-first-vs-direct/`](experiments/design-first-vs-direct) — pilot #1, a Python task
  CLI evolved through four stages.
- [`experiments/pilot2-bingo-web/`](experiments/pilot2-bingo-web) — pilot #2, a static-web printable
  bingo-card generator (the Balash arm shipped to its own product repo).
- [`experiments/pilot3-sudoku-sonnet/`](experiments/pilot3-sudoku-sonnet) — pilot #3, a static-web
  Sudoku generator built with the executing Worker on **Sonnet**.
- [`experiments/pilot4-roombook-evolving/`](experiments/pilot4-roombook-evolving) — pilot #4, an
  evolving meeting-room booking core with **isolated operators** and **separate design/product verdicts**
  (design → Balash, product → Direct).

In each, the two final codebases were judged blind by two reviewers with **opposite** dispositions
(pure-OO-quality and pro-simplicity/YAGNI), and in each, **both reviewers chose the Balash arm**
(pilot #1: ~70–75% / ~60%; #2: ~80% / ~65%; #3: ~80% / ~70%), with every load-bearing judge claim
verified against source. The consistent mechanism: design-first won by right-sizing — or properly
owning — the one subtle, product-consequential design decision the feature framing glosses over:
writing *less* where a guard was dead (pilot #1's cycle detection), *more* where a guarantee was
missing (pilot #2's card distinctness), and owning-by-construction what the plain arm left to
convention (pilot #3's one-solution invariant) — while paying an edge tax of speculative ceremony
each time. Pilot #3 also showed a **Sonnet executor is good enough** to realize a strong design
objective (including its hardest invariant), with small conformance gaps a stronger executor might avoid.

**Pilot #4 is the most informative and the least flattering.** With isolated operators and an evolving
product, design-first produced the deepest design of the set — it recognized a Stage-4 cross-room rule
had *falsified* the "rooms are independent" assumption, fused two conflict rules into one owned
predicate, and deleted the now-dead partition — and *both* opposite-disposition judges scored its design
a clear win. But a separate product assessor scored the **Direct** arm the better product: the same
subtractive minimalism cut a waitlist-inspection affordance and left two real bugs (a cross-room
promotion that never fires; a recurring series that books backwards on a negative stride). Design-first
is not strictly better — it can win design and lose product. One bright spot: pilot #4 is the first run
after the skill gained its mandatory **subtractive pass**, and the edge-ceremony tax that recurred in
#1–#3 **reversed** — the leaner arm was Balash's this time (n=1).

Still small N, and pilot #4 improved but did not fully remove the operator confound (isolated agent
contexts, but one orchestrator authored both prompts) and collapsed the Guide→Worker split into a single
agent. A meaningfully stronger signal than one pilot, not a validated result. Full caveats in each
pilot's `FINDINGS.md`.
