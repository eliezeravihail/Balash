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

One completed pilot under the current thesis. In `experiments/design-first-vs-direct/`, both arms
were built through four stages and judged blind by two reviewers with **opposite** dispositions
(pure-OO-quality and pro-simplicity/YAGNI); **both chose the Balash arm as better designed** (~70–75%
and ~60% confidence), and all the judge's load-bearing claims verified against source. It is still
**N = 1** — a robust signal, not a validated result. It earns a second pilot on a different product,
ideally with the two arms run by different operators.
