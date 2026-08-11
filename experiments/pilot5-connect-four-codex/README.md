# Pilot #5 — Balash vs a clean agent on Connect Four (external run)

**Provenance.** This pilot was run by **Codex** (a separate agent/operator), not by this repository's
maintainers or in the sessions that produced pilots #1–#4. The Balash version under test was **pinned to
commit `8baab0b`** (the state → design-docs split) — *before* the `buildable` / adversarial-exit-criteria
/ entering-existing-code fixes later in the history. The materials here are **as provided**: the report,
the fixed inputs, the two blind reviews, and one sample run's plan + README. The nine full run
implementations were **not** included, so links inside `REPORT.md` and the reviews that point into
`runs/…/implementation/…` refer to artifacts not in this folder.

## What it tested

A three-arm study on one product (a full browser Connect Four game, human vs computer, Easy/Normal/Hard):

| Arm | Product information | Method |
|---|---|---|
| **A — Direct** | short request; an oracle answers questions on demand | no Balash |
| **B — Direct + dossier** | the full fixed dossier up front | no Balash |
| **C — Balash + dossier** | the *same* dossier as B | Balash plan phase (@`8baab0b`) |

Three runs per arm (nine total). Because B and C get the **same** dossier, B-vs-C isolates *process*, not
information. Every run was independently re-run (`npm install/test/build`) and read by two **blind**
reviewers (structural, and product/acceptance); every finding carries a `file:line` or a reproducible
command; no composite score.

## The finding

The dossier required the human to **choose a difficulty before each game**. That product outcome held in
**C2 and C3 (2 of 3 Balash runs)** and in **none of the 3 B runs** — though B had the identical
information. Seven of the nine cases silently defaulted to Normal (an immediately playable game, or a
preselected radio) instead of requiring a real choice. All nine otherwise passed install/test/build and
routed human + computer moves through one shared rules engine.

## Is it sound? (this repo's assessment)

**Yes, as a small pilot, with the limits Codex itself states.** Strengths: product information held
constant (B vs C), a pre-registered differentiating criterion, blind reviewers, reproduce-or-cite
findings, no composite score, an independent command re-run, and an honest limitations section. Limits:
**n = 3** per arm; one small backend-less domain; Balash pinned to a pre-fix commit; and A-vs-B measures
the value of *information*, not active discovery. The headline result rests on a single lifecycle rule,
so it is **directional, not proof** — exactly as the report says.

## Why it matters here — convergence

Codex independently reproduced the failure mode this project keeps finding: **an explicit product /
lifecycle rule gets silently dropped unless it becomes a checkable exit criterion.** Same shape as pilot
#4's cross-room / negative-stride bugs, and as the room-booking plan A/B run while sharpening the skill.
Codex's recommended fix — every `GOALS.md` rule must appear as **(1)** an exit criterion, **(2)** an
acceptance scenario that starts in the right state and ends in visible behavior, and **(3)** a test that
refutes the tempting shortcut — is a fuller version of the "derive exit criteria *adversarially*"
guidance now in `skills/balash-guide/SKILL.md` (step 2). An independent run, the same lesson.

## Files

- [`REPORT.md`](REPORT.md) — Codex's experiment report (some links point to run artifacts not included).
- [`input/`](input) — the fixed request, dossier, oracle, and acceptance protocol given to the arms.
- [`reviews/`](reviews) — the blind structural and product/acceptance reviews.
- [`sample-run/`](sample-run) — one run's plan and product README (the plan exhibits the
  "initially Normal *naturally satisfies* the choice" pattern the reviews flag).
