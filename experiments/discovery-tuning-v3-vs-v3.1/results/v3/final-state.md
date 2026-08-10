# Balash Guide State (skill version: v3, strict discovery gate, no budget)

## Product purpose

A small team (3-10 people) tracks tasks together via a CLI, one person on one machine for now.

## Core scenario

A team lead creates "Prepare weekly report" with a description, assigns it to team member u1
(display name Dana), moves it todo -> in progress -> done, lists tasks to see Dana and the
status. Data survives a restart.

## Grounded product facts

- Small team, single user, single machine, CLI only.
- Team member = stable ID + display name, entered at assignment time, no roster command, no login.
- A task has: stable ID, title, description, assignee (may start empty), status.
- No delete/due-dates/priorities/notifications/networking/permissions/GUI this stage.
- Restart must not lose data.

## Open product decisions (resolved)

- A task may be created unassigned and assigned later. — grounds a persistent nullable assignee.
- Status may change directly between any pair, including reopening `done`. — no fixed sequence.
- Empty title/description: operator deferred ("choose something simple") -> Guide decision:
  reject empty title (a nameless task is not useful in a list), allow empty description.
- Reassignment after initial assignment: operator deferred -> Guide decision: allowed.

## Invariants

- Task always has stable ID, title (non-empty), description, assignee (nullable), status.
- Status in {todo, in progress, done}; any direct transition permitted.
- Data written before a restart is readable after a restart.

## Constraints

- Single user, single machine, CLI only.
- No auth/login.

## Explicit non-goals (this stage)

- Deletion, due dates, priorities, notifications, multi-user networking, permissions, GUI.

## Durable decisions

- Persistence seam: `TaskRepository.{list_all,get,save}`; one JSON implementation; domain/service
  verified (test + my own re-read) to import no storage format.
- IDs `t1, t2, ...` allocated by scanning existing tasks (fine for single-user/single-machine;
  flagged by the Worker as the first thing that breaks under concurrency — noted, not acted on,
  concurrency is out of scope).
- Assignee captured per-assignment, no roster; the same member_id could get two display names
  across tasks — accepted risk, flagged for a later roster decision if it ever matters.

## Open Guide TODO

- [ ] Watch whether AI-agent identity (stage 2) reuses or duplicates the `Assignee` pattern from
      stage 1.

## Current objective (stage 2)

**Objective:** Localize the known extension: let a task be assigned to an AI agent (a separate
persisted entity with provider/model) as well as a human, and add execution via a fake/test
provider that records success/failure + text output, retaining history across re-runs — without
touching stage-1 human-assignee behavior.

**Why now:** Entire stage-2 request; discovery resolved every material open decision (agent
identity, execute-vs-auto-trigger, result schema, history-vs-overwrite, fake-outcome control,
agent-id policy) before delegation.

**Exit criteria:**
- [ ] An AI agent is created as its own record (id + provider + model), separate from any task.
- [ ] A task can be assigned to a human (as in stage 1) or to an AI agent, through a coherent
      assignment concept (not two disconnected code paths for "human task" vs "AI task").
- [ ] Executing an AI-agent-assigned task runs a fake/test provider (no network) and appends a
      record: task id, agent id, success/failure, text output. Re-running appends, not overwrites.
- [ ] Executing a task that is unassigned or human-assigned is rejected with a clear error.
- [ ] All stage-1 CLI commands/behavior/tests still pass unmodified.
- [ ] New tests cover: agent creation, success and failure outcomes, repeated execution keeping
      history, rejection of execution on non-AI assignees.

**Preserve:** Stage-1 CLI commands and behavior; the persistence seam contract.

**Do not optimize for:** Real provider integration/auth/network, a provider plugin registry,
auto-triggering execution on assignment (resolved: stays separate), agent update/rename (resolved:
create-once this stage).

## Standing requirement (all objectives from here on)

Both build (Worker, before returning) and review (Guide, when evaluating) check the design
against `references/design-principles.md` — comprehension questions grounded in established
literature (Tell-Don't-Ask/Law of Demeter, program-to-an-interface, Interface Segregation,
Primitive Obsession, Anemic Domain Model, Feature Envy/Shotgun Surgery, Leaky Abstractions,
Single Responsibility, Sandi Metz's rules), not code-measured thresholds. Applies identically to
both the v3 and v3.1 pilot arms.

## Current objective (stage 3)

**Objective:** Prove the persistence seam under a second implementation: add a SQLite-backed
repository alongside the existing JSON one, selectable at startup, with equivalent observable task
and agent behavior across both backends — without changing domain/service logic.

**Why now:** Entire stage-3 request; the one open decision (no automatic migration between
formats) was resolved by discovery.

**Exit criteria:**
- [ ] User selects the storage backend via a startup option; JSON stays the default.
- [ ] SQLite implements the same repository shape(s) used by JSON (tasks, agents, executions) —
      domain/service files do not change.
- [ ] Task and agent behavior is equivalent under both backends, demonstrated by running the same
      behavioral test cases against both implementations (shared/parametrized), not two
      independently-written test files.
- [ ] No runtime switching mid-process; no automatic migration between formats.
- [ ] All stage 1-2 tests still pass unmodified.

**Preserve:** Stage 1-2 CLI/behavior; the persistence seam; agent identity model.

**Do not optimize for:** Automatic migration, concurrent multi-backend access, runtime switching,
an ORM, a third backend.

## Current objective (stage 4)

**Objective:** Establish one invariant-enforcement point for prerequisite eligibility: a task must
not enter `in progress` — by status change or AI execution — while any prerequisite is not `done`,
enforced through one shared check both paths call. Cycles rejected at declaration time.

**Why now:** Entire stage-4 request; discovery resolved cycle handling, creation-only-vs-editable
prerequisites, and reopen behavior — the three highest-impact decisions.

**Exit criteria:**
- [ ] A task can declare zero or more prerequisites at creation (editing deferred, per decision).
- [ ] Direct/indirect cycles rejected at declaration time.
- [ ] Moving to `in progress` while a prerequisite is not `done` is rejected, naming every
      blocking prerequisite's id, title, and status; task stays in its current status.
- [ ] Executing an AI-agent task under the same condition is rejected the same way, through the
      SAME check as the status-change path — verify by reading the code, not just by tests passing.
- [ ] Tasks with no prerequisites behave exactly as before.
- [ ] Reopening a done prerequisite after a dependent started needs no special handling but must
      not crash or corrupt data.
- [ ] Both backends persist prerequisites and stay behaviorally equivalent — extend the stage-3
      shared contract, don't fork it.
- [ ] All stage 1-3 tests still pass unmodified.

**Preserve:** Stage 1-3 CLI/behavior; the persistence seam and backend-equivalence guarantee;
the design-principles standing requirement.

**Do not optimize for:** Prerequisite editing/removal UI (deferred per decision), dependency
visualization, auto re-blocking on reopen (deferred per decision).

## Last evaluated result

**stage 3: met.** Independently re-verified: 185/185 tests pass on my own re-run; `git diff
stage-2` on domain/service/providers empty; confirmed exactly one `Backend.open(` call site
(`cli.py:142`) by grep, matching the Worker's "chosen once" claim.
