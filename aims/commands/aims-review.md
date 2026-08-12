---
description: Run the design review panel over the result — encapsulation, ownership, abstraction placement, the subtractive pass — and file what it concludes.
---

# /aims-review — skeleton

Invoke the `aims-guide` skill. Run the review panel over the current result
(`references/review.md`, `references/review-panel.md`):

1. **Judge the design**, not just correctness: is an invariant bypassable? is a rule enforced at one
   boundary or N? does a new variant slot in as a sibling or scatter edits? Apply the
   structure-vs-removable-blemish rule — a verdict turns on structural properties, not deletable
   local blemishes.
2. **Subtractive pass** — cut abstractions and affordances that do not pay for themselves.
3. **File the outcome:** a decision that changes direction → a new `decisions/` ADR (append-only,
   superseding the old by id); a durable lesson → `insights/`. Anchor each with `aims anchor`.

Output: the review verdict and any records filed. This command writes findings as knowledge; it does
not silently mutate prior ADRs (capsa decisions are append-only).
