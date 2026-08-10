# Guide (v3.1 skill) question log

| Stage | # | Question | Operator answer | Classification |
|---:|---:|---|---|---|
| 1 | 1 | Give one concrete example of a user using this product from start to a useful result. | A team lead uses the CLI on one machine to create "Prepare weekly report" with a description, assigns it to team member u1 (display name Dana), moves it todo→in progress→done, and lists tasks to see Dana and the status. After restart, the task is still there. | Grounded scenario |
| 1 | 2 | How is a team member identified — a managed roster, or an ID + name entered at assignment time? | The lead enters a stable member ID and display name at assignment time; no separate roster-management command, no login. | Open product decision (persistent identity) |
| 1 | 3 | May a task be created without an assignee and assigned later, or must every task be assigned at creation? | A task may start unassigned and be assigned later. | Open product decision (persistent data / lifecycle) |

Stopped at the 3-question soft budget. Remaining stage-1 unknowns handled without a question,
per the stop-rule and the "never ask about blank-field policy absent a stated invariant" rule:

- **Status transition freedom** (any-to-any vs. fixed sequence): stage-1 exit criteria ("change
  status between todo/in progress/done") do not require knowing whether *every* pair is legal to
  write a working vertical slice — recorded as **provisional product default**: allow any direct
  transition including reopening `done`; cheap to restrict later if a workflow rule ever surfaces.
- **Empty title/description**: no stated invariant makes this a "never ask" item under v3.1.
  **Provisional product default**: reject an empty title (a task needs a name to be useful in a
  list), allow an empty description.
- **Reassignment after initial assignment**: not required to write stage-1 exit criteria.
  **Provisional product default**: allow reassignment — restricting it later is cheap; forbidding
  it now would contradict "assignee may initially be empty" (which already implies assignment is
  a distinct, presumably repeatable action).

| 2 | 1 | Is an AI agent a separate persisted entity with its own id and config, or just fields on the task? | Create and persist an AI agent separately with its provider and model, then assign tasks to it by agent id. Provider/model belong to the agent, not each task. | Open product decision (identity/ownership) — stop-rule: yes, changes persistent representation and the exit criteria for "assign an agent" |
| 2 | 2 | Does the stored execution result need a success/failure flag, or is text output enough? | Yes — each stored result must contain task id, agent id, success/failure, and text output. | Open product decision (persistent data) — stop-rule: yes, changes the result schema |
| 2 | 3 | On repeated execution, should each run keep its own record, or does a new run replace the previous result? | Keep each execution as another persisted record; retaining history is acceptable. | Open product decision (persistent representation) — stop-rule: yes, changes whether result is a list or a single value |

Stopped at the 3-question budget. Remaining stage-2 unknowns handled without a question:

- **Auto-trigger execution on assignment vs. separate action**: not required to write concrete
  exit criteria for "an agent can be assigned and asked to execute" — either reading satisfies the
  literal stage-2 request. **Provisional product default**: execute stays a separate explicit
  action (consistent with stage-1's principle that assignment is a pure data change with no side
  effects). Revisit if the user ever asks for auto-run.
- **Fake-outcome control mechanism**: explicitly on the v3.1 "never ask" list (implementation of a
  required fake/stub). **Provisional product default**: the Worker chooses a simple, testable way
  to exercise both outcomes (e.g. an injectable fake in tests); not a CLI-level decision.
- **Agent id uniqueness / updatability**: not required to write stage-2 exit criteria (create-once
  is the obviously simpler starting point and nothing in the request suggests otherwise).
  **Provisional product default**: agent ids are unique, created once, not updatable this stage.

| 3 | 1 | When selecting SQLite after JSON, should data migrate/share automatically or remain independent? | JSON and SQLite may remain separate stores with independent data. Automatic migration or synchronization is not required. | Open product decision (persistent representation) — stop-rule: yes, changes whether a migration path is in scope for this objective at all |

Nothing else asked at stage 3 — "second backend meaningfully different" and "existing users keep
their current option" are already fully specified by the request text itself (JSON stays default,
add SQLite), so neither is a genuinely open decision requiring a question.

| 4 | 1 | Should the system prevent creating a cycle of prerequisites (directly or indirectly), or is that not a concern yet? | Direct or indirect dependency cycles are invalid and should be rejected. | Open product decision (validation timing/scope) — stop-rule: yes, decides whether validation is needed at all |
| 4 | 2 | Should prerequisites be supplied only at task creation, or can they be added/changed on an existing task? | I don't know yet. Supporting prerequisites at creation is sufficient for this version; don't make later editing unnecessarily difficult. | Open product decision (persistent API surface) — stop-rule: yes, decides the exit criteria's API shape |
| 4 | 3 | If a prerequisite that was already done gets reopened after a dependent task has already started, should the dependent automatically become blocked again? | No automatic change is needed; keep the dependent's current status. | Open product decision (lifecycle rule) — stop-rule: yes, decides whether a re-blocking mechanism is in scope |

Stopped at the 3-question budget. Remaining stage-4 unknowns handled without a question:

- **Blocked-explanation detail (ids only vs. ids+titles+statuses)**: on the v3.1 "never ask about
  error-message wording" list. **Provisional product default**: include title and status for every
  blocking prerequisite — cheap, and directly serves the stage-4 text's own "clearly report why".
- **Does the block apply only to entering in-progress and AI execution, or also to moving directly
  to done?**: the stage-4 request text names only those two actions explicitly — this is already
  a grounded fact from the request, not an open decision requiring a question.
