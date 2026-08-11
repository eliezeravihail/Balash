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
  the Loop cursor to `planned:awaiting-build`. Record the round's decisions and their rationale in the
  design docs (`GOALS.md` / `BASE-DEPENDENCIES.md` / `ARCHITECTURE.md`), where the *why this over that*
  lives in proximity to the fact it explains.
- **Stop here. Do not delegate and do not write implementation code.** **Present a plan report** — an
  executive summary compiled from the objective and the design docs (dependencies, decisions and their
  rationale, chosen architecture, exit criteria) — so the user can read the round's reasoning, inspect
  or edit the objective, and comment before anything is built. It is a presentation, not a new stored
  file: the substance already lives in the design docs. Then tell them to run the build command when
  ready.

$ARGUMENTS
