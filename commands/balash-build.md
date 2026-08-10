---
description: "Balash — run only the BUILD/execute phase: delegate the current planned objective to a Worker, then stop before evaluation."
---

Enter the `balash-guide` skill and run **only the BUILD phase** (operating-loop step 4), following
`references/modes.md` (stepped mode) and `references/worker-handoff.md`.

- Reload `.balash/state.md`. Require the Loop cursor at `planned:awaiting-build` (or a reopened
  objective). If there is **no current objective**, stop and tell the user to run the plan command
  first — do not invent an objective here.
- Delegate the drafted handoff to a **Worker subagent** (or, if no subagent facility exists, execute
  the handoff as a clearly separated phase). Do not pre-make the Worker's design.
- When the Worker returns, record the result and an evidence pointer in `state.md`; set the Loop cursor
  to `executed:awaiting-review`.
- **Stop here. Do NOT evaluate, accept, or choose the next objective** — that is the review phase.
  Report what was built and where the evidence is, and tell the user to run the review command.

$ARGUMENTS
