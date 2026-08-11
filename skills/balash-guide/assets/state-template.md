# Balash Loop State

This file is **loop-control only** — a handful of flags the Guide re-reads before acting and the
injection hook re-reads every turn. It carries **no product knowledge and no objective content.**

- Durable product knowledge (purpose, scenarios, grounded facts, decisions, invariants, constraints,
  Guide TODO) lives in `.balash/knowledge.md` — append-first, reviewable like a decision log.
- Each objective (Kind, Exit criteria, the Worker handoff, its Result, its Review) lives in its own
  file under `.balash/objectives/`, one file per objective, never overwritten by the next one.

This file only says *which objective is active* and *where the loop is parked*. Keep it this small on
purpose: it changes almost every turn and carries no history worth preserving, so it should not be the
place design reasoning is written down or silently lost when the next objective replaces it.

<!-- SCHEMA CONTRACT (this template owns it, together with assets/objective-template.md): the
     injection hook (hooks/inject-goal.py) reads THIS file by heading/marker for `## Mode`,
     `## Loop cursor`, and `## Active objective` (a path under .balash/objectives/, or empty), then
     opens that path and reads ITS `**Kind:**` / `**Objective:**` markers the same way. Renaming or
     reformatting either contract stops the goal from being injected. If you must change the shape,
     change it here, in assets/objective-template.md, AND in the hook together — all three are one
     contract. (The hook says so loudly if a filled state file lacks `## Loop cursor`, or an Active
     objective path can't be resolved, rather than failing silent.) -->

## Mode

<!-- auto | stepped. `auto` = the loop runs end to end, pausing only for open product decisions and
     the next product change. `stepped` = stop at every phase boundary (plan / build / review) and
     advance only on an explicit command; a returning Worker parks at executed:awaiting-review, it
     does NOT auto-advance. See references/modes.md. Default when unset: auto. -->

auto

## Loop cursor

<!-- Where the loop is parked right now, so any turn (a returning Worker, or a "balash next" / phase
     command from the human) can resume from exactly here. One line, kept current:
     needs-plan | planned:awaiting-build | awaiting-worker | executed:awaiting-review |
     reviewed:awaiting-decision | ready-to-choose-next | awaiting-human <named open decision> -->

needs-plan

## Active objective

<!-- Path to the objective file the cursor above refers to, e.g. .balash/objectives/0001-slug.md.
     Empty when the cursor is needs-plan / ready-to-choose-next / awaiting-human — those states have
     no single objective file in flight. Never edit an objective file's Kind/Objective/Exit criteria
     after Status leaves "planned" except through a fresh objective (a new file); this pointer is what
     lets the loop resume at exactly the right record without state.md needing to hold its content. -->

## Last review

<!-- One line: met | partially_met | invalidated | blocked. This is a pointer, not the reasoning — the
     reproduced readings live in the Active/most-recent objective file's "## Review" section. -->
