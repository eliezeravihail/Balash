# How to run another Balash pilot

A step-by-step protocol for adding a new experiment in the same style as the pilots in this folder. It
consolidates the conventions each pilot learned the hard way; read [`RESULTS.md`](RESULTS.md) first for
what the sequence has found, and [`guide-vs-direct/RUNBOOK.md`](guide-vs-direct/RUNBOOK.md) and
[`evolving-task-balash-vs-clean/`](evolving-task-balash-vs-clean) as worked instances.

The whole method exists to answer one honest question, so keep it in view the entire time:

> **When a product evolves through requirements nobody stated up front, does Balash's result end up
> architecturally better than what an equally capable agent with no method reaches on its own — even when
> that agent is free to refactor at every step?**

Writing code is cheap and a strong model refactors deeply, so "nicer code in one shot" is not the bar.
Only the **quality of the final architecture**, at the point the product kept changing, counts.

---

## 0. Decide what kind of pilot this is

Two shapes, judged differently:

- **A build pilot** (most of them — inventory, labeling, bingo, Sudoku, RoomBook). Both arms build a real
  product across staged reveals; you judge the final architecture (and, separately, the product).
- **A feasibility-gate pilot** (the "C" domains). The premise itself is unproven or false (e.g. automating
  a *regular* WhatsApp account is against its terms). Here **success is a reasoned stop**, not a build:
  the arm must detect the shaky foundational assumption, ask the one concrete product question, and refuse
  to silently substitute another route. Direct may reach the same stop — if it does, that is a fair result
  *against* Balash, not a failed experiment.

Pick one product per pilot and **one architectural axis** its evolution will stress (identity/ownership
introduced late; a second/third variant that reveals a missing abstraction; a delivery boundary; a
feasibility gate). If you can't name the axis, the pilot won't discriminate.

## 1. Fix the experiment package *before* any agent runs

Freeze and do not edit mid-run:

1. **`starter/`** — identical for both arms: runtime, test tool, fixtures, run instructions, permissions.
2. **Stage cards**, one per evolution step. Only the current card is visible; the next is revealed **only
   after both arms have closed the current one**. The first card may be deliberately thin (see B) — that is
   legal *only* because both arms can query the same oracle.
3. **A hidden staged spec + oracle answers** the agents never see (see
   [`evolving-task-balash-vs-clean/hidden-specs/`](evolving-task-balash-vs-clean/hidden-specs) for the
   shape). It holds the whole product including future stages, and the canonical answers to likely
   questions per stage.
4. **Visible acceptance per stage**, and separately **hidden final probes** derived *only* from
   requirements already revealed. No surprise test that invents a feature nobody asked for.
5. **One equal time/cost ceiling** per arm. A failed acceptance does not buy an arm free time — it is
   recorded and charged against the same budget.

## 2. The two arms

| | Balash arm | Direct / clean arm |
|---|---|---|
| Prompt | identical minimal request **+ one line**: "follow the `balash-guide` skill" | the identical minimal request, told nothing about method ("build it well") |
| Structure | Guide selects a design objective, delegates to a Worker, measures, iterates | one capable agent, free to plan/inspect/code/test/refactor as it likes |
| Right to ask | yes — one material product question at a time, to the oracle | yes — same channel, same right to ask the same oracle |

Keep everything else identical (§3). The Guide arm may spend more model calls — that extra reasoning loop
**is the treatment**; record the cost, never equalize it by feeding Direct hidden architecture hints.

## 3. Controlled variables — and the two standing conventions

Hold constant across arms: the model and version, the reasoning/budget setting, tools and repo
permissions, fresh empty repositories, the exact stage requirements, the test/runtime environment, and
**no access to any later-stage file before the current stage is complete**.

Two conventions the sequence adopted after being burned:

- **Pin the method commit.** Record the `balash-guide` commit hash the run executed under — the skill
  changes, so "which Balash" is part of the result (pilot #5 pinned `8baab0b`; pilot #7 too). A pilot
  whose pin you can't name is not reproducible.
- **A load-bearing wording change wants n ≥ 2 per arm.** A single run of an internal A/B that validates a
  *skill* wording change is **directional, not robust** — treat the change as confirmed only after it
  reproduces across at least two runs per arm. Per-product build pilots are typically n = 1 and are read as
  *suggestive*, with strength coming from the **sequence**, not any single unit.

If you run the *same design under a different harness or model* (as pilot #7/Codex did against the
Claude/Opus `evolving-task-balash-vs-clean`), that is **convergent evidence across implementations**, not a
controlled replication — do not compare the two per-arm results head-to-head.

## 4. Oracle policy — strict, passive, no volunteering

The operator plays an ordinary product owner, **not an architect**. Asking the right question is itself
part of what's under test, so an arm that doesn't probe a complement or invariant simply doesn't get told
it — and its product reflects that.

1. Answer only from facts in the hidden spec for the **current** stage.
2. Volunteer nothing the arm did not ask for.
3. **Never reveal a later-stage requirement.** When asked "will there be web / more channels / other label
   types later?", the honest current answer is always "not now — build for today." Balash earns nothing by
   guessing the future (its own subtractive pass cuts speculative future-proofing anyway).
4. For a technical-choice question an ordinary user would not decide (architecture pattern, interface
   shape, DB abstraction): answer *"I don't know; choose a simple sensible technical approach."*
5. **Word answers neutrally.** A single leak word disqualifies the run — pilot #7 threw out an A2 answer
   for containing "still/עדיין", which hints a later stage exists. If you contaminate, discard and re-run
   that stage.
6. Log every question and the verbatim answer. If the other arm later asks the same question, it gets the
   **same answer, word for word**.

## 5. Run procedure

For each arm, each stage:

1. Ensure only the current + previous requirements are visible; the two arms never see each other's repo,
   code, reasoning, or output.
2. Deliver the current stage card verbatim.
3. Let the arm work until it claims the requested behavior is complete.
4. Run the project's tests; run the visible acceptance.
5. Commit with a `stage-N` tag; save the transcript, the Q&A log, and cost (turns, tokens, wall-clock,
   model calls). A failed acceptance is recorded, not silently retried for free.
6. Only then reveal the next stage — to **both** arms.

For a feasibility-gate pilot, there is usually one stage: deliver the premise, let each arm investigate
public sources, and record **when and why** it stops (or fails to) — not lines of code.

## 6. Judge blind — and then scrutinize the judge

1. **Anonymize.** After the last stage, strip method-revealing names (`.balash/`, `HANDOFF`, branch names,
   commit messages) and relabel the two codebases X/Y (or Product-1/Product-2). The judges must not know
   which arm is which.
2. **Three separate reports, never merged into one score** (this is load-bearing — pilot #4 split):
   - **Design** — judged against Balash's own [`../skills/balash-guide/references/design-principles.md`](../skills/balash-guide/references/design-principles.md)
     and [`review.md`](../skills/balash-guide/references/review.md). Use **two opposite-disposition judges**
     (invariant-ownership vs. YAGNI/simplicity) reading the *same* two codebases — this tests whether a
     verdict is a taste artifact, the failure mode most worth catching.
   - **Product** — a black-box judge that receives only the product cards (not the method label) and checks
     acceptance/probes or an exact UI/API path.
   - **Cost** — a recorder (tokens, time, rounds, model calls, external deps), no quality verdict.
3. **Two judging refinements adopted mid-sequence, now standard:**
   - *structure vs. removable blemish* — a verdict must turn on structural properties (can an invariant be
     bypassed? is authorization one boundary or N? is a new variant one sibling or scattered edits?); a
     *removable local blemish* (deletable in an afternoon) must not flip it.
   - *"small is not unearned"* — a private field with no setter, or a one-line funnel, is small **and**
     load-bearing, not ceremony.
4. **Verify the judge, don't trust it.** Every load-bearing claim must carry a reproduction (an input →
   wrong output, a failing test) or a precise `file:line`. Re-run each arm independently
   (`install`/`test`/`build`) before believing any "tests pass." An abstract verdict, even a correct one,
   does not count as a measurement. Watch for experiment artifacts that bias a judge (pilot #7/B: the test
   suite that *used* a store was stripped from the blind snapshot, inflating a "dead code" reading — judge
   with tests in view).

## 7. Interpretation rules, fixed in advance

- Judges pick **Balash**, **Direct**, or **no clear advantage** for design and for product — no percentages,
  no weighted composite.
- A design win does **not** cancel a product loss, or vice versa. "Win the design, lose the product" is a
  real, demonstrated outcome (pilot #4) and is reported as a **trade-off**, not a victory.
- The honest strength is the **sequence** — the same "put the rule where it belongs" effect recurring
  across different products (needed *less* mechanism in #1, *more* guarantee in #2, a *better owner* in #3)
  — not a win tally. n = 1 per product is suggestive; a handful of units is not general proof.
- Record Balash's own recurring cost honestly: over-build at the seams (blatant/mild/absent has varied by
  domain), extra discovery rounds, delayed builds to measure.

## 8. Artifacts to keep (so the judges can be audited too)

Per pilot: the stage cards and their versions, the oracle Q&A logs, per-stage `stage-N` commits, cost
logs, the anonymized X/Y snapshots, the design-principles docs used, and the three measurement reports —
each finding carrying a reproduction or `file:line`. Following the `pilot5`/`pilot7` convention, the full
raw run implementations need not be committed; the fixed inputs, the record, and cited evidence are the
reproducible core.

## 9. When to add it to `RESULTS.md`

Give it the next free pilot number (check the list at the bottom of [`RESULTS.md`](RESULTS.md) — numbers
are already taken through the current tip), add a scoreboard row or an external-run block, and cross-link
any parallel run of the same design. Say plainly what it is: build pilot or feasibility gate; blind or an
initial non-blind audit; n; the pinned method commit; and the single axis it stressed.
