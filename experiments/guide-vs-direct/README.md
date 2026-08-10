# Guide vs Direct: a staged evolution pilot

Tests whether `balash-guide` (discovery → one engineering objective → delegate to a Worker →
evaluate evidence → repeat) produces software that absorbs unforeseen product change better than
a coding agent that receives each requirement directly, with no process guiding it.

Start with [`FINDINGS.md`](FINDINGS.md) — it synthesizes both pilots plus a controlled test of the
review methodology itself. The rest of this directory is the protocol and raw evidence:

- [`RUNBOOK.md`](RUNBOOK.md) / [`EXPERIMENT_V2.md`](EXPERIMENT_V2.md) — the protocol: two
  conditions, four staged and previously-hidden requirements, no future stage visible to either
  condition, independent verification before each commit, then a blind comparative review.
- [`scenario/`](scenario) — the four stage requirements and the operator-only oracle (the true
  product facts, revealed to the review only, never to either build condition directly).
- [`evaluator/`](evaluator) — `collect_metrics.py` (low-interpretation repository facts, no quality
  score) and `review-rubric.md` (what the blind reviewer is asked).
- [`reveal_stage.py`](reveal_stage.py) — copies exactly one stage's requirement into a condition's
  workspace without exposing later stages.
- [`results/claude-pilot-v2skill/`](results/claude-pilot-v2skill) — one full pilot run under the
  pre-v3 (un-gated) skill: final Guide state, discovery log, per-stage metrics, an HTML report, and
  **two** blind reviews of the identical final code — one without ground-truth product facts, one
  with — run specifically to test whether the reviewer's access to ground truth changes its
  verdict. (It does, substantially — see `FINDINGS.md` §2.)
- [`results/gpt-pilots-v2-v3/`](results/gpt-pilots-v2-v3) — an independently run pair of pilots
  (different operator, different model) comparing the un-gated skill (v2: 0 discovery questions)
  against the gated skill now installed at `.agents/skills/balash-guide/` (v3: 21 questions, more
  product-faithful code, decisive blind-review preference for Guide once given the oracle facts).

## Minimum bar for trusting a result

One run per condition, as recorded here, is a pilot, not evidence of a trend. The protocol's own
bar is at least three independent runs per condition with fresh model contexts before treating a
direction as established (`RUNBOOK.md`, "Number of runs").
