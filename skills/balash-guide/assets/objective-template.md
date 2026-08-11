# Objective NNNN — <slug>

<!-- One file per objective, under .balash/objectives/, named NNNN-<slug>.md (zero-padded sequential
     number + a short kebab-case slug). This is the durable, ADR-style record of one design/quality
     outcome: what was asked for, the handoff that was sent, what came back, and how it measured.
     Once Status leaves "planned", treat Kind/Objective/Exit criteria/Preserve as historical fact —
     do not silently rewrite them; if the objective turns out wrong, that belongs in the Review
     section and a fresh objective, not a quiet edit here. Only Status, Worker handoff (once, at
     delegation), Result, and Review are filled in as the loop advances through this one objective's
     lifecycle. -->

**Kind:** <!-- design | implementation | refactoring — sets the review lens. -->

**Status:** <!-- planned | executed | reviewed -->

**Objective:**

**Why now:**

**Exit criteria:**
- [ ]

**Preserve:**
-

**Do not optimize for:**
-

## Worker handoff

<!-- The bounded handoff actually sent to the Worker (or executed inline in stepped mode) — see
     references/worker-handoff.md: ROLE / DESIGN GOAL / BEHAVIOR IT MUST SATISFY / WHY NOW /
     WHAT "GOOD" AIMS AT / RELEVANT CONTEXT-PRESERVE-NON-GOALS / RETURN TO GUIDE. Filled once, when
     the Loop cursor moves to planned:awaiting-build. -->

## Result

<!-- What the Worker returned when it reported back: working code + tests pointer, its design
     reasoning, its own self-reported result (met | partially_met | invalidated | blocked) and why,
     new facts or risks it surfaced. Filled when the Loop cursor reaches executed:awaiting-review. -->

## Review

<!-- The Guide's own measurement against the Exit criteria above — reproduced readings (a failing
     probe / concrete input→wrong output, or a precise file:line citation; no scores) — which criteria
     read as met/unmet, and what this implies for the next objective. Filled when the Loop cursor
     reaches reviewed:awaiting-decision. -->
