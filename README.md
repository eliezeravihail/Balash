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

## Status

One pilot per condition, run twice by two independent operators. That is a minimum useful signal,
not a validated result — see the "Minimum bar for trusting a result" note in
`experiments/guide-vs-direct/README.md`. The next iteration on the skill itself (a tighter
discovery gate, referred to as v3.1 in `FINDINGS.md`) has not yet been built or tested.
