# Balash

*(עברית: [README.he.md](README.he.md))*

## What this is

Balash is a Claude Code plugin that makes **design** itself the goal handed to a coding agent —
instead of a review applied after the code is already written.

The plugin splits the work into two roles:

- **The Guide** — holds the product vision and decides, one at a time, what design/quality outcome
  the codebase most needs right now. It never writes implementation code itself. Its deliverable is
  the design quality of the codebase across the product's whole evolution — not features shipped or
  lines written.
- **The Worker** — a senior engineer, as capable as the Guide — receives that outcome as its
  objective, with the requested feature behavior attached as a **constraint** the design must
  satisfy, and builds accordingly. The Guide then evaluates what came back and sets the next
  objective.

This separation is enforced: the Guide does not become the Worker just because it *can* edit code.
It inspects code to understand state or judge evidence, but the substantial implementation work is
the Worker's.

## How to work with it

**Install** as a Claude Code plugin, then engage it **explicitly** through its commands — nothing runs
in the background and nothing auto-activates on unrelated turns:

- `/balash-plan` — choose one design objective and draft the handoff to the Worker; **stops before any
  code is written** and presents a **plan report** — an executive summary of the round's dependencies,
  decisions, and chosen architecture, compiled from the design docs — for you to read and comment on
  before you build.
- `/balash-build` — execute the planned objective; stop when done.
- `/balash-review` — measure the result against the exit criteria; stop with grounded findings and a
  direction for what's next (it reports, it does not gate). Also runs **standalone** on any diff,
  branch, or PR that Balash didn't build.
- `/balash-plan-and-build` — the same loop run end to end: choose an objective, delegate, measure, and
  continue until the change is delivered, pausing only for an open product decision.

**The durable target lives in files, not the conversation.** A conversation drifts, gets interrupted,
gets summarized — so Balash keeps its memory on disk, and each command reloads it when it runs:

- **`.balash/state.md`** — loop status only: the active objective, the loop cursor, the mode. Every
  command re-reads it to re-orient.
- **The product's own design docs** — the durable design record, living *with the product's code*:
  `GOALS.md` (goal, scenarios, non-goals), `BASE-DEPENDENCIES.md` (the foundational substrate only),
  and `ARCHITECTURE.md` (seams, structural decisions, invariants) — each fact recorded *with its
  rationale in proximity*. Facts kept next to the code they govern — not session-recovery logs. The plan
  report `/balash-plan` shows you is compiled from these, not a separate file.

**No product decision gets made silently.** Every unclear point is sorted into one of three buckets: a
grounded product fact (stated, observed in the code's behavior, or settled earlier), an open product
decision (changes observable behavior, persistent data, ownership/identity, lifecycle, or failure
handling — **ask the user, never guess**), or a technical freedom (an implementation detail with no
product impact — the Worker just picks something reasonable).

**Project layout:**

- [`skills/balash-guide/`](skills/balash-guide) — the method: `SKILL.md`, its references (objective
  selection, worker handoff, design principles, run modes, review panel), and the doc templates.
- [`skills/balash-sharpen-prompt/`](skills/balash-sharpen-prompt) — the general-purpose companion:
  framing any task before doing it (see below).
- [`commands/`](commands) — the commands that engage the method.
- [`experiments/`](experiments) — the evidence (see [Does it work?](#does-it-work) below and
  [`experiments/RESULTS.md`](experiments/RESULTS.md)).

## A general companion — `balash-sharpen-prompt`

Balash's core insight — *the goal, and how you phrase it, decide the result* — is not only about
software. The plugin ships a second, general-purpose skill, **`balash-sharpen-prompt`**, that applies
the same discipline to **any** task you hand a capable agent ("plan a pension", "find the bugs", "write
the report"). Before executing, it sharpens the vague ask into a real brief: the true outcome (not a
proxy), the hard judgment the ask hides, what only the person can decide (ask, don't guess), what
"done" checkably means, what to protect, and what evidence must back the claims — written as a way of
thinking, not a checklist to tick. Invoke it with `/balash-sharpen-prompt`, or let it engage when a
substantial task's framing matters. Where `balash-guide` is Balash for software design,
`balash-sharpen-prompt` is Balash for framing anything.

## The principles

The method rests on two principles. They combine: the first sets *what* goal you give the agent;
the second sets *the form* it must take for that goal to actually steer it.

### 1. The agent aims at the goal it was shown — not at what you quietly wanted

An implementing agent optimizes toward whatever goal is placed in front of it, not toward anything
left unsaid. Hand it a feature ticket ("implement X") and it optimizes for *the feature landing* —
tests pass, behavior works — and design quality becomes whatever happens to survive along the way:
an invariant enforced in three different places instead of one, a rule owned by nobody, an
abstraction built for a future that never arrives. This isn't because the agent doesn't know how to
design well — it's because the goal it was given never asked for that.

The practical consequence: **if you want quality design out, design itself has to be the goal you
put in** — not a side effect you hope emerges on its own. So every unit of work in Balash is
reframed: not "build feature X" but "reach this design outcome, with feature X as a constraint the
design must satisfy." The same code gets written in the end — but the agent's cognition is now
pointed at "where should this fact live in the system?" instead of only "how do I get the feature
through?". This is why the Guide in Balash explicitly picks a separate *design* objective (e.g.:
establish ownership, prove out an abstraction, establish an invariant) before asking for the
matching implementation — instead of trusting that good design will just "happen" while the feature
gets built.

### 2. An understood goal means concrete usage scenarios and explanations — not general hand-waving

Not every "design objective" phrasing works. A general goal like "write quality code" sounds right,
and the knowledge of how to do that is already embedded in the agent — but in practice, a phrasing
like that **escapes to shallow performance metrics**: test-coverage percentages, line counts, file
layout, generic scores — because without concretization the agent has nothing real to ground a
judgment call in, so it falls back to the easiest thing to measure. Knowledge the agent already has
isn't enough if the goal it's given doesn't activate that knowledge against the specific case in
front of it.

So every handoff in Balash must include not just the name of the desired outcome, but also:
**concrete usage scenarios** (how the system will actually be called/used), an explanation of *why*
this outcome matters right now (not just *what* it is), and a checkable exit criterion (not a
score — a question with a testable yes/no answer). The practical test: a good handoff is one two
strong engineers could satisfy with two different, equally good designs — if it only allows the one
design you'd already pictured, it's over-specified; if it's as vague as "write good code," it will
escape to metrics. For exactly the same reason, *checking* the result in Balash was built against
the same trap: every review finding must carry a concrete reproduction (an input that produces the
wrong output, a failing test) or a precise `file:line` citation — not a general verdict on "is this
good?". An abstract judgment, even when it happens to be correct, doesn't count as a measurement.

## Does it work?

Balash is a claim — *making design the goal produces better-designed software* — so it was tested, not
just asserted. Each pilot builds the **same product two ways** (Balash vs. a plain session handed the
product goal directly), with **product information held constant**, so any difference is attributable
to process, not knowledge. The two codebases are judged **blind**, by reviewers told to judge design
like Martin/Fowler/Metz; then the judge is **scrutinized, not trusted** — every load-bearing claim is
verified against the source, and a second reviewer with the **opposite** disposition (pro-simplicity /
YAGNI) re-judges, to catch a verdict that is only a matter of taste.

- **Pilots #1–#3** (a task-manager CLI, a printable bingo generator, a printable Sudoku generator):
  both opposite-disposition judges preferred the **Balash** arm in every one.
- **Pilot #4** — isolated operators, an evolving product, and *separate* design and product verdicts —
  is the honest one, and it **split**: the two judges chose Balash for **design** (clear), while a
  blind product assessor chose the direct arm for **product** (clear). Design-first produced the deeper
  design *and*, by the same minimalist discipline, shipped two real bugs. That "win the design, lose
  the product" outcome is real — now demonstrated rather than hypothesized, which is exactly why the
  two verdicts are never merged into one score.

Full method, scoreboard, and per-pilot findings: **[`experiments/RESULTS.md`](experiments/RESULTS.md)**.
