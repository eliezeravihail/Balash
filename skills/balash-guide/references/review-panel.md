# The review panel — scrutiny, not scoring

This is the review step (`SKILL.md` step 5) done as an explicit, escalating pass. It also runs
**standalone** as a review tool on any diff/branch/PR that Balash did not build. It exists because a
plain "is this good?" LLM judgment is weak: with no second implementation to contrast against, a solo
judge drifts to vague praise and invented grades. What made the experiment judges trustworthy was not
their authority — it was **an adversarial contrast plus reproduction of every decisive claim.** This
panel rebuilds both without a second arm.

## The one rule that makes it real: a finding must be reproduced or cited

A review output is not an opinion and never a number. **Every finding carries either:**

- a **reproduction** — a probe/test that actually fails, or a concrete input → wrong output/state; or
- a **precise code citation** — `file:line` of the dead abstraction, the duplicated rule, the leaked
  boundary, the comment that overstates the code.

No scores, no percentages, no "looks solid," no "8/10." A finding without a reproduction or a citation
does not exist — drop it. (Inventing quality numbers is the exact failure this whole project exists to
avoid.) The contrast that a second arm used to provide is replaced by the **exit criteria / stated
intent**: probe the deliverable against *that* ground truth, not against taste.

## The reviewer roles — spawn what the task needs, scale to it

Do not convene a panel for a one-line change; the Guide's own step-5 check is enough. **Escalate** for
invariant-bearing, cross-cutting, evolving, or high-stakes work.

**Where the roles run.** When review is reached by an explicit command (the `review` phase, or a
standalone `review <target>`), run the roles **inline in this session on the currently selected model —
no subagents**; adopt each lens in turn. Only in `auto` mode may the roles be spawned as subagents (for
independent contexts when no human is watching). The reproduce-or-cite rule below is what guarantees an
inline review is honest — not a process boundary.

Roles, in value order:

1. **Verification reviewer (the one that catches real defects).** Writes *adversarial probes* against
   each exit criterion and each invariant/boundary — especially the paths the tests don't exercise —
   and reports the failures it reproduces. In pilot #4 this is the role that caught the shipped bugs
   (a cross-room promotion that never fired; a series that booked backwards): behavior probed against
   the spec, not code read for vibes.
2. **Fidelity reviewer.** Design claims and comments vs the code: a decision claimed but not wired up,
   an abstraction that exists but is dead with its rule inlined elsewhere, a comment that overstates.
   (Same pass as the mixed-tier policy in `review.md`.)
3. **Subtractive reviewer.** The subtractive pass from `review.md`: for every type/guard/wrapper, name
   the present force that requires it; flag the ones whose removal wouldn't damage a current
   rule/invariant/boundary.
4. **Opposite-disposition second reviewer.** *Only* for genuine judgment/taste calls. A reviewer with
   the opposite bias (minimalist vs rigor) re-checks the call, to test that a verdict is not a taste
   artifact. If both dispositions land the same way, the verdict is robust; if they split, surface the
   split rather than pick.

## Trust discipline: the reviewer is scrutinized, not trusted

LLM reviewers miss defects and can be confidently vague. So the panel's output is an input to the
Guide, not a ruling: **before acting on a decisive finding, the Guide reproduces it itself** — runs the
failing probe, opens the cited line. That is exactly how pilot #4's claims were confirmed. A finding
that cannot be reproduced on demand is downgraded, not shipped as a verdict.

## Standalone use (review any change, no Balash loop required)

`review <target>` where target is a diff, branch, path, or PR:

1. Establish the ground truth to probe against — the change's stated intent / acceptance criteria. If
   it is unstated and material, ask the user one concrete question rather than inventing criteria.
2. Run the roles above, scaled to the change.
3. Return **findings, not a grade.**

## Output shape

```
Findings (most severe first):
- <what> — <file:line> — reproduction: <failing probe / input→wrong output> — why it matters: <one line>
...
Verdict: met | partially_met | invalidated | blocked
Recommendation: accept  |  reopen: <which exit criterion / objective, and why>
```

No summary score. If nothing survived reproduction, say so plainly — an empty findings list is a valid,
honest result, not a failure to find something.
