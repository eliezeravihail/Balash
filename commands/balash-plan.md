---
description: "Balash — run only the PLAN phase: choose one design objective and draft the Worker handoff, then stop for review. Does not write code."
---

Enter the `balash-guide` skill and run **only the PLAN phase** (operating-loop steps 1–3), following
`references/modes.md` (stepped mode) and `references/objective-selection.md`.

- Set `Mode: stepped` in `.balash/state.md` (create it from `assets/state-template.md` if absent).
- Establish current state, run discovery, and resolve any **open product decisions** by asking the
  user one concrete question at a time — planning is where those questions belong.
- Choose the single most valuable **design/quality objective** now, **declare its Kind** (`design` |
  `implementation` | `refactoring` — see `references/objective-selection.md`; it sets the review lens),
  and draft a bounded Worker handoff per `references/worker-handoff.md`. Write both into `state.md`; set
  the Loop cursor to `planned:awaiting-build`.
- **Write the plan report.** Produce `.balash/plan-report.md` from `assets/plan-report-template.md` — the
  executive summary of this round: the dependencies, the deliberations (the real dilemmas and *why this
  over that*), the decisions, the chosen architecture, and the exit criteria. This is the whole point of
  the manual mode — the user reads it and comments before anything is built.
- **Stop here. Do not delegate and do not write implementation code.** Show the compact Guide
  checkpoint (Objective / Why now / Exit criteria / Preserve / Do not optimize for) **and present the
  plan report** (`.balash/plan-report.md`) so the user can read the full reasoning, inspect or edit the
  objective, and comment before anything is built. Tell them to run the build command when ready.

$ARGUMENTS
