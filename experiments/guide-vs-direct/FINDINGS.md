# Findings: Guide vs Direct, and what it takes to judge the result

This document synthesizes three linked pieces of evidence gathered while testing whether the
`balash-guide` skill (Guide selects one engineering objective at a time, delegates to a Worker,
evaluates evidence, repeats) produces better software evolution than a coding agent that receives
each product requirement directly. It is written after a pivot: the deterministic Balash CLI
(cycle/fan-out/documentation rules) is no longer the subject. The skill is.

## 1. Two independent pilots agree on the headline, disagree on the margin

Two independent operators ran the same protocol (`RUNBOOK.md`, `scenario/`): a task-management CLI
evolved through four staged, previously-hidden requirements, once under **Direct** (the coding
agent receives each requirement verbatim) and once under **Guide** (a discovery→objective→delegate→
evaluate loop, per the skill). Both pilots then had a blind reviewer compare the anonymized final
code with no knowledge of which repository came from which condition.

- **Claude pilot** (`results/claude-pilot-v2skill/`), using the pre-v3 skill (no explicit
  silent-decision gate): the Guide condition still asked 4 real discovery questions across the
  4 stages (not the 0 the un-gated skill nominally permits). Blind review without ground-truth
  product facts: a genuine split — "prefer Guide's tests, prefer Direct's production code."
- **GPT pilot** (`results/gpt-pilots-v2-v3/`), run twice: once on the unmodified skill (**v2**), once
  on the skill with the silent-decision gate added (**v3**, the version now installed in this repo
  at `.agents/skills/balash-guide/`).
  - v2: the Guide condition asked **0 questions** across all 4 stages (`logs/guide-questions.md` and
    `usage.csv` in the original package are empty) and silently guessed the same class of product
    facts the Claude pilot's Guide asked about. Blind review (no oracle) still leaned toward Guide's
    architecture, but on ownership/locality grounds, not product fidelity.
  - v3: the Guide condition asked 21 questions (7/8/1/5 per stage), of which the report estimates
    13 were high/medium value, 7 low value, 1 purely technical and mis-asked. Blind review, *with*
    the operator-only product facts as ground truth, was decisive: Guide's product model was
    "much more faithful" and its stage-4 evolution was "the most valuable property for unknown
    change."

**The shared finding across three separate runs (Claude, GPT v2, GPT v3) is that the un-gated
skill under-asks.** Whether that shows up as 0 questions (GPT, different underlying model/harness)
or 4 questions (Claude) depends heavily on which model is executing the skill text — the skill
alone did not reliably produce grounded discovery. The v3 gate (see `.agents/skills/balash-guide/
references/discovery.md`, "Mandatory discovery gate" / "Product-assumption test") is a direct,
evidenced fix for that failure mode, at the cost of asking more than necessary in places (GPT's own
v3 report proposes a further-tuned "v3.1": cap it to one scenario + up to 3 highest-value questions
per change, add a `provisional product default` bucket for reversible unknowns, forbid asking about
pure technical freedoms).

## 2. The blind judge's verdict depends heavily on whether it has ground truth

This was tested directly, not just inferred, using the Claude pilot's own repositories:

- **Same code, no oracle facts** (`blind-review-no-oracle.md`): split verdict. The judge
  characterized Guide's agent-registry, agent-identity, and execution-history modelling — all
  driven by real oracle facts the Guide had access to — as `"invented"`, `"unrequested scope"`,
  and complexity that "had to be carried through stages 3 and 4." It could not distinguish a
  correct-but-unstated product decision from genuine over-engineering, because it had nothing to
  check either against.
- **Same code, oracle facts added as explicit ground truth, with a "fidelity to product facts"
  rubric section** (`blind-review-with-oracle.md`): decisive verdict for Guide. The same agent
  registry is now explicitly labelled "a correct product decision driven by exactly this
  ground-truth fact, not speculative scope," and Direct's simpler model is reclassified from
  "leaner" to containing three concrete **fidelity defects**: no stable member identity (a bare
  name string), provider/model duplicated per task instead of owned by an agent entity, and —
  the sharpest one — no success/failure field on the execution result at all, so a failed AI
  execution is *indistinguishable from never having run*.

**Practical implication:** a blind code-quality review of an agent's output is only as good as
what it is allowed to check the code against. Without the true, complete intent (not just the
literal request text), "the judge preferred X" mostly measures "which model matched the judge's
own priors about size and directness" — which is a different question from "which model matched
the product." This is exactly the failure mode the skill's discovery gate exists to prevent one
level up (in the *builder*, not the *judge*), and it turns out the reviewer needs the same
correction.

## 3. Neither blind LLM judge, however careful, is a substitute for deterministic measurement

A live check was run against the same two anonymized repositories using the (separately maintained,
no-longer-in-scope-here) Balash deterministic engine plus `ruff --select ALL`:

- Balash's architecture rules fired **zero cases on either repository** — no cycles, fan-out well
  under threshold in both, and critically, its dedicated "mechanical forwarding chain" detector did
  **not** flag the `AgentView` pass-through adapter that the first blind LLM judge called out in
  prose as duplicated three-hop indirection. At this repository size (~750–1200 production LOC),
  the current deterministic rule thresholds do not engage at all.
- `ruff --select ALL` (a strict rule set including cyclomatic complexity, docstring coverage,
  security, and pylint-style checks — none of which either blind LLM judge, across two full
  reviews and 29+ tool calls in the more thorough one, ever ran or mentioned) found a real,
  verifiable complexity defect neither judge caught: Guide's `cli.py:run` dispatcher trips
  `C901`/`PLR0912` (cyclomatic complexity 17 vs. a threshold of 10; 20 branches vs. 12) — a
  legitimate, fixable finding (a command-registry dict instead of an `if/elif` chain). It also
  flagged a possible SQL-injection pattern (`S608`) in Direct's SQLite layer, which on inspection
  was a false positive (the interpolated value is a fixed internal column-name constant, not
  external input) — itself a reminder that deterministic diagnostics still need a verification
  pass, the same principle behind this repository's `validate_luna_review.py`-style citation
  checking.

**Practical implication:** an LLM judge — even blind, even adversarial, even given ground-truth
product facts and 29 tool calls of manual verification — is still an LLM, and shares the coding
agents' own blind spots for certain classes of mechanically-checkable defects (cyclomatic
complexity chief among them in this run). "No code smell, proper encapsulation and abstraction" —
the actual target of this whole line of work — was never directly measured by any review in this
experiment until a real linter was pointed at the code. The skill's discovery gate fixes what the
*builder* doesn't know to ask; a real static-analysis pass is still needed to catch what the
*reviewer* doesn't know to look for, independent of how good the reviewing model is.

## Open items for the next iteration (v3.1)

1. Tune `.agents/skills/balash-guide/references/discovery.md` per GPT's own v3 report: one
   concrete scenario + up to 3 highest-value questions per change; a "provisional product default"
   bucket for reversible unknowns that does not require a question; an explicit stop-rule
   ("would a different answer change the objective/exit-criteria *now*? If not, don't ask").
2. Any comparative "Guide vs Direct" review going forward should give the blind judge the true
   product facts (or an equivalent ground truth) explicitly, labelled as such, with a rubric
   section that forces it to separate "correct but unstated" from "speculative." Section 2 above
   is the direct evidence for why this is not optional.
3. Any comparative review should also run real static analysis (cyclomatic complexity at minimum,
   plus whatever linter is appropriate to the language) as a fourth, deterministic input alongside
   behavior/fidelity/locality — not as a replacement for the LLM review, but because the LLM review
   demonstrably misses things a two-second tool run catches exhaustively.
