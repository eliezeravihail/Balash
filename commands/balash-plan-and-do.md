---
description: "Balash — plan and execute one objective in sequence: choose a design objective + draft the handoff, then delegate it to a Worker, and stop before review."
---

Enter the `balash-guide` skill and run the **PLAN and BUILD phases back to back** for a single
objective (operating-loop steps 1–4), following `references/modes.md`, `references/objective-selection.md`,
and `references/worker-handoff.md`. This is the one-objective sibling of `auto`: it does *plan → do* in
sequence and then **stops for review** — it does not loop.

**Plan (steps 1–3), first:**
- Reload `.balash/state.md` (create it from `assets/state-template.md` if absent).
- Establish current state and run discovery. Resolve any **open product decisions** by asking the user
  one concrete question at a time — this is where those questions belong. **Establish the foundational
  dependencies at day zero** (SKILL step 1) before choosing the objective.
- Choose the single most valuable **design/quality objective** now, **declare its Kind** (`design` |
  `implementation` | `refactoring`), and draft a bounded Worker handoff per
  `references/worker-handoff.md`. Write both into `state.md`.

**Do (step 4), in the same run — no stop in between:**
- **Delegate to a Worker subagent** with the handoff. (This is the deliberate difference from
  `/balash-build`, which runs one already-planned phase *inline* under your supervision: `plan-and-do`
  runs the fuller flow and delegates for real, like `auto` — just for one objective.)
- When the Worker returns, record its result and an evidence pointer in `state.md` and set the Loop
  cursor to `executed:awaiting-review`.

**Then stop — before review.**
- **Do NOT measure, accept, or choose the next objective.** Show the compact Guide checkpoint
  (Objective / Why now / Exit criteria / Delegation result / where the evidence is) and tell the user to
  run the review command (`/balash-review`) when ready — or `/balash-auto` to continue looping.

If, during planning, a material open product decision cannot be resolved, stop at that question and do
not proceed to Do — planning is not complete while a product decision is open.

$ARGUMENTS
