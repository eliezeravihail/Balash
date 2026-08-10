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

## Layout

- [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) — the plugin manifest.
- [`skills/balash-guide/`](skills/balash-guide) — the skill itself: `SKILL.md`, its `references/`
  (discovery, objective selection, reviewing Worker evidence, the Worker handoff shape), and the
  `.balash/state.md` template it maintains per project.
- [`hooks/`](hooks) — `hooks.json` and the `UserPromptSubmit` script that re-injects the current
  objective every turn.
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

Three completed pilots under the current thesis, on three different domains (including one with the
executing Worker on **Sonnet**) — and all point the same way: **six blind reviews across opposite
dispositions, six-for-six for the Balash arm.** The completed pilots:

- [`experiments/design-first-vs-direct/`](experiments/design-first-vs-direct) — pilot #1, a Python task
  CLI evolved through four stages.
- [`experiments/pilot2-bingo-web/`](experiments/pilot2-bingo-web) — pilot #2, a static-web printable
  bingo-card generator (the Balash arm shipped to its own product repo).
- [`experiments/pilot3-sudoku-sonnet/`](experiments/pilot3-sudoku-sonnet) — pilot #3, a static-web
  Sudoku generator built with the executing Worker on **Sonnet**.

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

Still **N = 3, one operator** — a meaningfully stronger signal than one, but not a validated result.
The strongest next step is independent operators per arm. Full caveats in each pilot's `FINDINGS.md`.
