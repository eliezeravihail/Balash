# Balash

**Balash is a Claude Code plugin that makes *design* the goal a coding agent is given — not a review
applied after the code is written.** It keeps agent work pointed at the most valuable engineering
objective as a product evolves, by separating *what to optimize now* (a **Guide**) from *how to build
it* (a **Worker**), and by refusing to let unresolved product decisions get silently guessed.

> This is a pivot. An earlier deterministic static-analysis CLI also lived under this name; it is no
> longer the subject of this repository and is not carried forward here.

---

## 1. The problem, and the one idea

An implementing agent optimizes toward whatever goal you hand it. Give it a feature ticket and it
optimizes for **the feature landing**; design quality becomes whatever happens to survive that. The
code works, the tests pass, and the structure quietly rots — an invariant enforced in three places, a
rule owned by nobody, an abstraction built for a future that never comes.

The idea behind Balash is a single move: **if you want good design out, design has to be the goal you
put in.** So Balash reframes each unit of work from *"build feature X"* into *"reach this design
outcome, with feature X as a constraint the design must satisfy."* Same code gets written — but the
agent is now spending its cognition on *"where should this truth live?"* instead of only *"how do I make
the feature pass?"*

Everything below is machinery in service of that one reframing.

---

## 2. The method

### 2.1 Two roles: Guide and Worker

- **The Guide** holds the product vision and decides, **one at a time**, what *design/quality outcome*
  the codebase most needs next for the change in front of it. It never writes implementation code. Its
  deliverable is the design quality of the codebase across the product's whole evolution — not features
  shipped or lines written.
- **The Worker** — a senior engineer as capable as the Guide — receives that outcome as its objective,
  with the feature behavior attached as a *constraint the design must satisfy*, and designs and builds
  it. The Guide then evaluates the design it returns and chooses the next objective.

The separation is hard: the Guide does not become the Worker just because it *can* edit code. It
inspects code to understand state or judge evidence, but the substantial implementation is the Worker's.

### 2.2 Design objectives and implementation objectives — the rhythm

The Guide feeds the Worker a *sequence* of objectives, agile-style, each scoped to a capability. Two
kinds, and **both are first-class goals**:

- **A design objective.** The deliverable *is* the design — the boundaries, interfaces, and domain
  shape for the capability, with reasoning, concrete enough to build against. A good design is a real
  goal on its own; it need not come bundled with working feature code. The first objective of any new
  product is a design objective.
- **An implementation objective.** *"Implement this capability, conforming to the design we already
  agreed."* Because a sound design was reached and judged as its own earlier goal, implementation fills
  in an already-sound shape instead of sliding into spaghetti.

So the rhythm is **design → implement → (next capability) design → implement**. The Guide does **not**
plan the whole sequence up front — that would be waterfall in an agile costume. Each next objective is
chosen by *evaluating the result of the previous one*. The one rule across the sequence: it must
actually progress to working, tested software — a run of nothing but design objectives that never ships
is as wrong as bundling everything into one "build the feature" goal.

### 2.3 No silent product decisions

Every unresolved choice is sorted into exactly one bucket:

- **Grounded product fact** — stated by the user, shown by repository behavior, or recorded from an
  earlier answer.
- **Open product decision** — anything that changes observable behavior, persistent data,
  identity/ownership, lifecycle, failure handling, or scope. **Ask the user; never guess.**
- **Technical freedom** — an implementation detail with no material product effect. The Worker just
  picks something sensible.

The cardinal sin is disguising an open product decision as a technical assumption. A plausible guess is
still a guess. Before the first delegation the Guide gets at least one concrete usage scenario; before
any material change it re-checks for newly opened product decisions.

### 2.4 The operating loop

Not mandatory phases — a control loop for deciding what to do next:

1. **Establish state** — read `.balash/state.md` and just enough of the repo; classify the request's
   implied choices into the three buckets above; resolve open product decisions with the user.
2. **Choose one objective** — the single objective that most reduces an important uncertainty or
   structural risk *now*, framed around design quality, with: *Objective, Why now, Exit criteria,
   Preserve, Do not optimize for.*
3. **Protect intent** — make sure no open product decision is being silently assumed, and unrelated
   concerns are parked explicitly rather than forgotten.
4. **Delegate** — a bounded Worker handoff framed as a design outcome (never a feature ticket), giving
   the behavior as a constraint and the design principles as the target. A good handoff is one two strong
   engineers could satisfy with *genuinely different, equally good* designs — if it only permits the one
   design you already pictured, it's over-specified.
5. **Evaluate evidence** — verify the exit criteria were actually demonstrated (run the tests, read the
   code); never accept "done" on the Worker's word. For high-stakes work, escalate to the **review
   panel** (§2.7). Outcome: met / partially_met / invalidated / blocked.
6. **Choose again** — from the updated state; re-evaluate from evidence, no fixed phase order.

### 2.5 The durable goal: state file + hook

The loop runs inside an ordinary conversation, which drifts, gets interrupted, and is summarized. So
**the goal does not live in the chat — it lives in `.balash/state.md`.** That file is the authority on
what's being built. Two mechanisms keep it working:

- **The `balash-guide` skill is model-invoked** — Claude enters it on its own whenever you build or
  materially evolve software (no slash command needed), the way a UI-design skill triggers on a UI
  request.
- **A `UserPromptSubmit` hook** (`hooks/inject-goal.py`) fires every turn, reads `.balash/state.md`, and
  re-injects the current objective (and, in stepped mode, the stop-policy) — so the goal survives
  side-conversations and context compaction even on a turn where the skill body isn't loaded. On any
  project without a `.balash/state.md`, the hook is silent.

The discipline that makes this work: **whenever about to act as the Guide, re-read `state.md` first**,
and update it the moment the loop's position changes. Awareness of the goal isn't sustained in the
model's head — it is *reloaded* from disk.

### 2.6 What "good" aims at — and the subtractive pass

The target is the standard in [`references/design-principles.md`](skills/balash-guide/references/design-principles.md)
(ownership, boundaries, invariants, "duplication is cheaper than the wrong abstraction") — used as a
direction, not a checklist. The experiments surfaced a specific, recurring failure of a design objective:
it reliably produces a domain that is **sound at the core and over-built at the seams** (a value object
that owns no rule, a guard against callers that can't exist, a method nothing calls). So the review step
now runs a **mandatory subtractive pass**: for every type/guard/wrapper/abstraction, name the *present
product force* that requires it, and delete the ones whose removal wouldn't damage a current
rule/invariant/boundary. It's counter-architecture critique, not a line-count rule.

### 2.7 Reviewing: scrutiny, not scoring

A plain "is this good?" LLM judgment is weak — with nothing to contrast against, it drifts to vague
praise and invented grades. The **review panel** ([`references/review-panel.md`](skills/balash-guide/references/review-panel.md))
rebuilds what made the experiment judges trustworthy: an adversarial contrast (against the *exit
criteria*, in place of a second implementation) plus reproduction of every claim. Its core rule:

> **Every finding carries a reproduction (a failing probe / a concrete input → wrong output) or a
> precise `file:line` citation. No scores, no percentages.** A finding that can't be reproduced or
> cited does not exist.

Escalating roles, spawned to fit the task: a **verification reviewer** that writes adversarial probes
against the exit criteria (the role that catches real bugs), a **fidelity reviewer** (claims/comments vs
code), a **subtractive reviewer** (the pass above), and an **opposite-disposition second reviewer** for
genuine taste calls. The reviewer is *scrutinized, not trusted* — before acting on a decisive finding,
the Guide reproduces it itself.

---

## 3. Running it: automatic, or phase by phase

The same loop runs two ways, recorded in the `Mode` field of `.balash/state.md`
([`references/modes.md`](skills/balash-guide/references/modes.md)):

- **Automatic** (default) — the Guide drives the whole loop end to end, pausing only at the two
  legitimate human moments: an *open product decision* it must not guess, and *receiving the next product
  change*. A returning Worker auto-advances the loop. Command: **`/balash-auto`**.
- **Stepped** — for hands-on supervision. The loop stops at **every** phase boundary and advances only
  on an explicit command, so you can inspect and edit between phases:
  - **`/balash-plan`** — choose one design objective and draft the Worker handoff; **stops before any
    code is written**, so you can approve or edit the objective first.
  - **`/balash-build`** — execute the planned objective; stops when done.
  - **`/balash-review`** — evaluate the result with the review panel; stops with reproduced findings, a
    verdict, and a recommendation.

  In stepped mode a returning Worker **parks** at `executed:awaiting-review` instead of auto-advancing.

**Explicit phase commands run inline in your session, on the model you selected — no subagent.** You
chose that model and you're watching the phase, so the work stays visible and runs on your model rather
than being delegated behind an agent boundary. (Only automatic mode delegates to Worker subagents, where
autonomous delegation and context isolation are the point.) The Guide/Worker separation is preserved
because the design objective was produced first, as its own `plan` step — `build` *conforms to* it.

**`/balash-review` also runs standalone** on any diff, branch, or PR that Balash didn't build — the same
roles, the same reproduce-or-cite rule — as a general review tool. (In pilot #4, this panel is exactly
what caught the shipped bugs a design-only judgment missed.)

---

## 4. Install & layout

Install as a Claude Code plugin (it self-activates on software work via the model-invoked skill; the
hook and commands come with it).

- [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) — the plugin manifest.
- [`skills/balash-guide/`](skills/balash-guide) — the method: `SKILL.md`, its `references/` (discovery,
  objective selection, worker handoff, reviewing evidence, design principles, **modes**, **review
  panel**), and the `.balash/state.md` template it maintains per project.
- [`hooks/`](hooks) — `hooks.json` and the `UserPromptSubmit` script that re-injects the objective (and
  stepped-mode stop-policy) each turn.
- [`commands/`](commands) — the stepped-mode phase commands: `/balash-plan`, `/balash-build`,
  `/balash-review` (also the standalone reviewer), `/balash-auto`.
- [`experiments/`](experiments) — the evidence (see below).

---

## 5. The experiments

**The question:** does *making design the goal* — a Guide that hands a capable Worker a design/quality
objective (feature as constraint), then verifies and iterates — produce better-designed software than a
plain session handed the product goal directly?

### 5.1 How a pilot is run

Two arms build the **same** product: the **Balash** arm (Guide + Worker) and a **Direct** arm (a
competent session handed the feature directly — not a strawman). Then:

- **Blind judging.** The two final codebases are judged anonymized by a reviewer told to judge *design*
  (Martin/Fowler/Metz), not to hunt bugs.
- **Opposite dispositions.** A second reviewer with the **opposite** bias (pro-simplicity/YAGNI vs
  pure-OO) re-judges, to test whether a verdict is an artifact of taste — the failure mode we most
  worried about.
- **The judge is scrutinized, not trusted.** Every load-bearing claim is verified against the source;
  LLM judges demonstrably miss defects and can't tell "correct-but-unstated" from "over-engineered"
  without ground-truth product facts.
- **Separate verdicts (from pilot #4 on).** Design quality and *product* quality are judged separately
  and never merged into one score — because they can disagree.

### 5.2 The four pilots

| Pilot | Product (domain) | Executor | Result |
|---|---|---|---|
| **#1** | Task-manager CLI, 4 evolving stages (Python) | strong | **Balash** (both dispositions) |
| **#2** | Printable bingo-card generator (static web) | strong | **Balash** (both dispositions) |
| **#3** | Printable Sudoku generator (static web) | **Sonnet Worker** | **Balash** (both dispositions) |
| **#4** | RoomBook booking core, 4 evolving stages, **isolated operators** | strong | **split — design → Balash, product → Direct** |

Read pilots #1–#3 as **three experimental units with robustness-checked verdicts**, not six independent
wins: the two opposite-disposition judges in a pilot read the *same* two codebases, so they test taste,
not replication. The honest strength is less the tally than **the sequence** — three different faces of
one mechanism:

- **#1 — needed *less* mechanism.** The Direct arm built a cycle-detector; Balash reasoned cycles were
  impossible and enforced one existence rule instead. Balash *removed* machinery.
  ([`design-first-vs-direct/`](experiments/design-first-vs-direct))
- **#2 — needed *more* guarantee.** The Direct arm generated batch cards that could silently collide;
  Balash made within-batch distinctness an enforced guarantee. Balash *added* a guarantee. (Honest
  caveat: the Balash handoff *asked* "what uniqueness do you guarantee?", so part of the win is
  design-level discovery, not "same info, better design.") ([`pilot2-bingo-web/`](experiments/pilot2-bingo-web))
- **#3 — same guarantee, *better owner*.** Both arms enforced the one-solution invariant; Balash made it
  true *by construction* (`Puzzle.tryCreate`) where the Direct arm held it by convention. It also showed
  a **Sonnet Worker is good enough** to realize a strong design objective — with one verified conformance
  failure (a dead `isSatisfiedBy`) that a follow-up **strong-model fidelity review** then caught and
  fixed at review cost (validating the *mixed-tier* policy: cheap Worker + strong review).
  ([`pilot3-sudoku-sonnet/`](experiments/pilot3-sudoku-sonnet))
- **#4 — the split.** Under **isolated operators**, an **evolving product**, and **separate verdicts**:
  design-first produced the deepest design of the set (it saw a Stage-4 cross-room person-rule *falsify*
  the "rooms are independent" assumption, fused two conflict rules into one owned predicate, and
  **deleted** the now-false partition) — and *both* opposite-disposition judges scored its design a clear
  win. **But** a separate product assessor scored the **Direct** arm the better product: the same
  minimalism cut a waitlist-inspection affordance and shipped two real bugs (a cross-room promotion that
  never fires; a series that books backwards on a negative stride). ([`pilot4-roombook-evolving/`](experiments/pilot4-roombook-evolving))

### 5.3 What the pilots establish

- **The core effect held under the harder conditions.** With isolated operators and product evolution,
  design-as-goal still produced the deeper design — to the point of deleting a structural assumption a
  new invariant had outgrown.
- **"Win design, lose product" is real — demonstrated, not hypothesized (pilot #4).** The very discipline
  that wins design can cut an affordance and leave behavioral bugs. This is *why* the design and product
  verdicts must be scored separately.
- **A cheap executor can realize a strong design, and a strong review closes the gap (pilot #3).** The
  mixed-tier policy — cheap Worker + strong fidelity review — caught and fixed the exact conformance slip
  a weaker executor left.
- **The subtractive pass may be working (pilot #4).** It was the first run after the pass was added, and
  the edge-over-engineering that recurred in #1–#3 *reversed*: the blind auditor found the Direct arm
  carried the ceremony this time and Balash was leaner (n=1, suggestive).

### 5.4 Honest limits

- **Small N.** Four pilots; two of them (#1, #4) exercise an *evolving* product, which is Balash's real
  claim ("preserves quality as the product changes").
- **Operator confound: reduced, not removed.** Pilots #1–#3 had one operator run both arms. Pilot #4 ran
  the arms as isolated agent contexts, but one orchestrator still authored both arms' prompts from
  identical spec text. Genuinely independent operators remain the stronger control.
- **Role separation not enacted in #4.** One agent played both Guide and Worker there.
- **Balash is not strictly better.** It over-built at the seams in #1–#3 and lost on readability/size,
  and lost *product* in #4. Design quality ≠ product quality.
- **The judges are LLMs**, trusted only because their specific claims were source-verified each time.

### 5.5 Read more

**[`experiments/RESULTS.md`](experiments/RESULTS.md)** is the at-a-glance summary of all pilots. Each
pilot folder has a `FINDINGS.md` with the full evidence and caveats. Two earlier, differently-framed
pilots ([`guide-vs-direct/`](experiments/guide-vs-direct), [`discovery-tuning-v3-vs-v3.1/`](experiments/discovery-tuning-v3-vs-v3.1))
produced the lesson — *a blind LLM judge can't tell "correct-but-unstated" from "over-engineered"
without ground-truth product facts* — that shaped the judging method used throughout.

---

## 6. Status

A meaningfully stronger signal than a single result, **not** a validated one. The core reframing holds
across four pilots and survives isolation and evolution; pilot #4 also drew the honest boundary of the
method (it can win design and lose product) and hinted that the subtractive pass addresses the one
recurring weakness. Next: genuinely independent operators, restoring the Guide→Worker delegation inside
the Balash arm, confirming the subtractive-pass reversal on more than one run, and a cost comparison of
`strong-direct` vs `strong-Guide + cheap-Worker + strong review`.
