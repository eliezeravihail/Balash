# Balash

`Balash` is now the home of **`balash-guide`**: a skill that keeps coding-agent work pointed at
the right engineering objective as a product evolves, by separating *what to optimize now*
(the Guide) from *how to implement it* (a delegated Worker), and by refusing to let unresolved
product decisions get silently guessed.

This is a pivot. An earlier deterministic static-analysis CLI also lived under this name; it is
no longer the subject of this repository, and is not carried forward here.

## Layout

- [`.agents/skills/balash-guide/`](.agents/skills/balash-guide) — the skill itself: `SKILL.md`,
  its `references/` (discovery, objective selection, reviewing Worker evidence, the Worker
  handoff shape), and the `.balash/state.md` template it maintains per project.
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
