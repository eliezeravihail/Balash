---
description: "Balash — run the REVIEW phase: evaluate against exit criteria with the review panel, producing reproduced findings (no scores). Also works standalone on any diff/branch/PR."
argument-hint: "[optional target: a diff / branch / path / PR to review standalone]"
---

Enter the `balash-guide` skill and run the **REVIEW phase**, following `references/review.md` and
`references/review-panel.md`. Two uses, decided by whether a target is given:

**In-loop review (no target given).** Reload `.balash/state.md`; require the Loop cursor at
`executed:awaiting-review`. Evaluate the Worker's evidence against the objective's **exit criteria**,
and run the review panel scaled to the objective (verification-probe first; add fidelity, subtractive,
and an opposite-disposition second reviewer as the stakes warrant). End with reproduced findings, a
verdict (met | partially_met | invalidated | blocked), and a recommendation (accept → set cursor
`ready-to-choose-next`; or reopen → name the failed criterion and set the cursor back). Do not silently
repair everything reported — decide what matters to the product now.

**Standalone review (a target is given in the arguments).** Review the target change without requiring
a `.balash/state.md`. Establish the ground truth to probe against — the change's stated intent /
acceptance criteria; if it is unstated and material, ask the user one concrete question rather than
inventing criteria. Run the same panel roles, scaled to the change.

In both uses, obey the panel's core rule: **every finding carries a reproduction (a failing probe /
concrete input→wrong output) or a precise `file:line` citation — no scores, no percentages.** Before
acting on a decisive finding, reproduce it yourself. An empty findings list is a valid, honest result.

Target (if any): $ARGUMENTS
