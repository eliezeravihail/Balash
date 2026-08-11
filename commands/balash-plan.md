---
description: "Balash — run only the PLAN phase: choose one design objective and draft the Worker handoff, then stop for review. Does not write code."
---

Enter the `balash-guide` skill and run **only the PLAN phase** (operating-loop steps 1–3), following
`references/modes.md` (stepped mode) and `references/objective-selection.md`.

- Set `Mode: stepped` in `.balash/state.md` (create it from `assets/state-template.md` if absent);
  create `.balash/knowledge.md` from `assets/knowledge-template.md` if absent.
- Establish current state, run discovery, and resolve any **open product decisions** by asking the
  user one concrete question at a time — planning is where those questions belong. Record facts and
  decisions in `.balash/knowledge.md`.
- Choose the single most valuable **design/quality objective** now, **declare its Kind** (`design` |
  `implementation` | `refactoring` — see `references/objective-selection.md`; it sets the review lens),
  and draft a bounded Worker handoff per `references/worker-handoff.md`. Write both into a new
  `.balash/objectives/NNNN-<slug>.md` (from `assets/objective-template.md`); point `state.md`'s `Active
  objective` at it and set the Loop cursor to `planned:awaiting-build`.
- **Stop here. Do not delegate and do not write implementation code.** Show the compact Guide
  checkpoint (Objective / Why now / Exit criteria / Preserve / Do not optimize for) so the user can
  inspect or edit the objective before anything is built. Tell them to run the build command when ready.

$ARGUMENTS
