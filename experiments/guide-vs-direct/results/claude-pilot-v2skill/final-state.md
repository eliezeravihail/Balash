# Balash Guide State

## Product purpose

A small team (roughly 3-10 people) tracks and manages tasks together.

## Core scenarios

A team member creates a task, assigns it to someone, moves it through todo -> in progress -> done,
and lists tasks to see current assignee and status. Data must survive an application restart.

## Product forces

### Likely change axes

- Assignee: **confirmed as of stage 2.** Two real kinds — human team member and AI agent — only AI
  agents can execute. The assignment concept accommodates both without duplicating logic per kind.
- Execution: a capability distinct from assignment. Only AI-agent-assigned tasks can be executed;
  re-running keeps history (append, not overwrite).
- Persistence backend: **confirmed as of stage 3.** A second local storage format (SQLite) exists
  alongside JSON, selectable at startup, behaviorally equivalent, proven by a shared test suite.
- Task ordering/eligibility: **confirmed as of stage 4.** Tasks can have prerequisites; entering
  `in progress` (by either status-change or AI execution) requires all prerequisites `done`.

### Invariants

- A task always has a stable ID, title, description, assignee (may be empty), and status.
- Status is one of: todo, in progress, done.
- Data written before a restart must be readable after a restart, under whichever backend is
  selected at startup.
- An assignee is either a human team member or an AI agent, never both, never a third kind so far.
- Only a task assigned to an AI agent may be executed; execution is rejected for human/unassigned.
- An execution record is immutable history: task id, agent id, success/failure, text output.
  Running again adds a new record; it does not replace the previous one.
- Provider/model configuration is a property of the AI agent, not of each task.
- Task/agent behavior must be equivalent regardless of which storage backend is selected.
- A task must not enter `in progress` while any prerequisite is not `done`, regardless of which of
  the two entry paths (status change, AI execution) is used — enforced through one shared check.
- Prerequisite cycles (direct or indirect) are invalid and rejected at declaration time.

### Constraints

- Single user, single machine, CLI only (discovery Q1).
- No auth/login required (team members identified by stable ID + display name).
- No real external AI service; execution goes through a fake/testable local provider. No auth,
  billing, streaming, or network retry semantics needed (oracle-confirmed, not inferred).
- Storage backend is chosen once, at startup; no runtime switching inside one process.
- No automatic migration between storage formats (discovery Q3).

### Explicit non-goals

- Deletion, due dates, priorities, notifications, multi-user networking, permissions, GUI.
- A pluggable/registered set of real AI providers, concurrent execution, an execution queue.
- Auto-triggering execution as a side effect of assignment (stays a separate explicit action).
- Automatic migration tooling, concurrent multi-backend access, runtime backend switching, an ORM
  or extra dependency, a third storage backend "just in case".
- Prerequisite editing/removal UI, dependency-graph visualization, auto re-blocking a dependent
  when a done prerequisite is reopened (discovery Q2 — explicitly not needed this experiment).

## Durable decisions

- Persistence seam: `TaskRepository`/`AgentRepository` (`get/save/list_all`-shaped) over
  `Task`/`AiAgent`. Domain/service code contains no storage-format import — verified independently
  each stage, not just claimed.
- Assignee stored inline on the task (member_id + display_name); no member registry yet. Deferred
  deliberately; flagged as the first thing that changes if display-name drift becomes a real issue.
- Assign and execute are two separate explicit CLI actions (discovery Q2 of stage 2).
- Agents are a first-class stored entity (their own repository seam); human assignees stay inline.
- `SCHEMA_VERSION` stays 1 across both backends — it numbers the data shape, which has grown only
  additively; the storage *format* (JSON vs SQLite) is treated as a separate axis.
- SQLite: one connection per operation with commit, no WAL/concurrency — matches the single-user
  constraint. Cross-backend file usage is rejected with a clear error, not auto-converted.

## Open Guide TODO

- [ ] Member registry / display-name drift — still open, still not required by any stage so far.
- [ ] Execution history surviving a reassignment-to-human — flagged, not yet a real product
      question that has come up.
- [ ] (new, stage 4) Confirm prerequisite eligibility is enforced through one shared function
      called by both the status-change path and the execute path — this is the exit criterion the
      whole stage exists to prove; verify by reading the code, not only by tests passing.

## Current objective

**Objective:** Establish one invariant-enforcement point for prerequisite eligibility: a task must
not enter `in progress` — whether by manual status change or by AI-agent execution — while any of
its prerequisites is not `done`, enforced through exactly one shared check that BOTH paths call,
not duplicated logic. Cycles are rejected at declaration time, not discovered later.

**Why now:** This is the entire stage-4 request, and the review rubric this whole experiment will
be judged against explicitly names this concern: "is prerequisite eligibility enforced in one
coherent place rather than duplicated across status-change and AI-execution paths?" There are now
exactly two paths that can start a task — this is the first stage where that duplication risk
actually exists.

**Exit criteria:**
- [ ] A task can declare zero or more prerequisite task IDs.
- [ ] Direct or indirect prerequisite cycles are rejected at the point a dependency is declared
      (discovery Q1), not later.
- [ ] Moving a task to `in progress` while a prerequisite is not `done` is rejected with a clear
      reason naming the blocking prerequisite(s); the task stays in `todo`.
- [ ] Executing an AI-agent task while a prerequisite is not `done` is rejected the same way,
      through the SAME check used by the status-change path — verify by reading the code (one
      function/method called from both call sites), not only by both paths' tests passing.
- [ ] Tasks with no prerequisites behave exactly as before (regression).
- [ ] Reopening a done prerequisite after a dependent already started does not need special
      handling (discovery Q2) but must not crash or corrupt data.
- [ ] Both storage backends (JSON, SQLite) persist prerequisites and stay behaviorally equivalent —
      extend the stage-3 shared/parametrized equivalence suite, do not fork it.
- [ ] All stage 1-3 tests still pass unmodified.

**Preserve:**
- All stage 1-3 CLI commands and behavior.
- The persistence seam and backend equivalence guarantee established in stage 3.
- Provider/model-on-agent, execution-history-is-append-only, human/AI assignment symmetry.

**Do not optimize for:**
- Prerequisite editing/removal UI, dependency-graph visualization, priority ordering by dependency
  depth, an event/notification system, automatic status transitions when a prerequisite completes.

## Last evaluated result

**stage 4: met.** Independently re-verified, not accepted on the Worker's word alone:
- Re-ran the full suite myself: 196/196 pass.
- `grep _require_startable taskman/service.py`: exactly two call sites (inside `set_status`, guarded
  by `IN_PROGRESS`, and inside `execute_task`) plus the definition — the single-enforcement-point
  exit criterion is a code fact I checked myself, not just an assertion in the report.
- `git diff stage-3` on `test_cli.py`/`test_service.py`/`test_agents.py`/`test_persistence.py`:
  **empty**. `test_backend_equivalence.py` diff is 205 added / 0 deleted — purely additive, matching
  the claim that prerequisites extended the shared suite instead of forking a second one.
- Full suite run covers both backends (196 = 140 prior + 56 new, shared cases run per-backend).
- Did not independently re-run the Worker's mutation tests (guard-removal, inlined-duplicate,
  cycle-disabled) — those were transient probes on a since-reverted tree, not something to redo
  after the fact. Treated as supporting method, not as the basis for "met" on its own; the code
  inspection and full suite above are what "met" rests on.

stage 3: met (recorded in prior state; superseded, preserved in git history at this file's
stage-3 commit).
