---
description: "Balash — plan and build autonomously, end to end: repeatedly choose the next design objective, delegate it to a Worker, measure the result, and continue the plan → build → review loop until the change is fully delivered. Pauses only for open product decisions."
---

Enter the `balash-guide` skill and run the **full autonomous loop** (`references/modes.md`, automatic
mode). This is the end-to-end driver — **not** a single plan-then-build pass. It keeps going, one
objective after another, until the current product change is delivered. (For a single supervised phase,
use `/balash-plan`, `/balash-build`, or `/balash-review` instead.)

- Set `Mode: auto` in `.balash/state.md` (create it from `assets/state-template.md` if absent; create
  `.balash/knowledge.md` from `assets/knowledge-template.md` if absent), and resume the loop from the
  current Loop cursor — a plan drafted in stepped mode is built and reviewed the same way here;
  switching mode never discards the cursor or the objective file it points at.
- Drive the full operating loop yourself, **repeating** in the design → implement rhythm: choose one
  objective → delegate to a Worker subagent → measure the evidence yourself → choose the next objective
  → and so on. A returning Worker **auto-advances** the loop; you do not stop after one objective.
- On the first objective of a new product, establish state and run discovery first — including the
  **day-zero foundational dependencies** (SKILL step 1) — before choosing the objective.
- Pause only at the **two legitimate human moments**: an *open product decision* you must not guess,
  and *receiving the next product change*. Do not run away — the same guardrails apply: one objective
  at a time, never mark met on the Worker's word without measuring the evidence yourself, never guess a
  product decision, no pre-planned roadmap.

$ARGUMENTS
