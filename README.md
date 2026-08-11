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

**Install:** install as a Claude Code plugin. It self-activates — the `balash-guide` skill enters
automatically on any task that builds or materially changes software, no explicit command needed.

**The current goal lives in a file, not in the conversation.** A conversation drifts, gets
interrupted, gets summarized. So the durable target is `.balash/state.md` — the file holding the
active objective. A `UserPromptSubmit` hook (`hooks/inject-goal.py`) runs on every turn, reads that
file, and re-injects the current objective — so it survives side-conversations and context
compaction. On a project without `.balash/state.md`, the hook is silent.

**Two ways to run it**, tracked in that file's `Mode` field:

- **Automatic (default, `/balash-auto`)** — the Guide runs the whole loop by itself, stopping only
  at two legitimate points: an open product decision it must not guess, and receiving the next
  product change. A returning Worker auto-advances to the next step.
- **Stepped** — for close supervision. The loop stops at every phase boundary and advances only on
  an explicit command:
  - `/balash-plan` — chooses one design objective and drafts the handoff to the Worker; **stops
    before any code is written**.
  - `/balash-build` — executes the planned objective; stops when done.
  - `/balash-review` — checks the result against the exit criteria; stops with grounded findings and
    a direction for what's next (it reports, it does not gate). Also runs **standalone** on any
    diff, branch, or PR that Balash didn't build.

**No product decision gets made silently.** Every unclear point is sorted into one of three
buckets: a grounded product fact (stated, observed in the code's behavior, or settled earlier), an
open product decision (changes observable behavior, persistent data, ownership/identity,
lifecycle, or failure handling — **ask the user, never guess**), or technical freedom (an
implementation detail with no product impact — the Worker just picks something reasonable).

**Project layout:**

- [`skills/balash-guide/`](skills/balash-guide) — the method: `SKILL.md` and its references
  (objective selection, worker handoff, design principles, run modes, review panel).
- [`hooks/`](hooks) — the hook that re-injects the current goal on every turn.
- [`commands/`](commands) — the stepped-mode commands.
- [`experiments/`](experiments) — experimental evidence for the method (see
  `experiments/RESULTS.md`).

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
