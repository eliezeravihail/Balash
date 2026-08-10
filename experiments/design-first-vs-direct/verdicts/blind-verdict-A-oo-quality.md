# Blind design review: Codebase X vs Codebase Y

Both are the same product — a CLI task manager that grew through CRUD+persistence,
AI-agent assignees with execution history, a SQLite backend, and task prerequisites.

- **Codebase X** (`tasktool`): 5 source modules — `models.py`, `manager.py`,
  `store.py`, `sqlite_store.py`, `cli.py`. Compact and flat.
- **Codebase Y** (`taskcli`): ~25 source modules across four packages — `domain/`
  (task, status, readiness, prerequisites, assignee, member, agent, execution_result,
  ids, errors), `storage/` (ports + parallel `json/` and `sqlite/` trees, each with
  four repositories, a backend aggregate, and — for sqlite — a schema), `execution/`
  (provider seam + service), plus a top-level `service.py` and `cli.py`. Layered.

The headline: X is a clean, proportionate, lightly-object-oriented design; Y is a
rigorously object-oriented, domain-driven design that is heavier than the problem
strictly needs. The review below judges each on the eight questions.

---

## 1. Does each class have one clear job?

**Codebase X — moderate.** The small value types (`Status`, `HumanAssignee`,
`AgentAssignee`, `Agent`, `ExecutionResult`) are each cohesive. The weak spot is
`TaskManager` (`manager.py`): it is the single hub for task CRUD, agent CRUD,
prerequisite validation *and* transitive cycle detection, the readiness rule
(`unmet_prerequisites`/`is_ready`), execution, persistence orchestration, *and*
display rendering (`assignee_label`). Those are several different reasons to change
living in one class. It is still readable and internally coherent, but it is doing a
lot. A second smudge: the domain dataclasses in `models.py` also carry their own
`to_dict`/`from_dict`, so each of them has a persistence-serialization job in addition
to its modeling job.

**Codebase Y — strong.** Responsibilities are split cleanly and deliberately. `Task`
owns task rules; `Prerequisites` owns the prerequisite rules; `Status`/`Readiness` own
their vocabularies; `Team`/`AgentRegistry` own membership authority; each repository
owns one entity's persistence; `TaskService` and `ExecutionService` are split by
reason-to-change (roster/task orchestration vs. run-and-record), which the docstrings
call out explicitly. The risk here is the opposite of X's: the split is fine-grained
enough that some classes (e.g. `Readiness`) carry very little, but each still has
exactly one job.

---

## 2. Are the interfaces real?

**Codebase X — strong.** `TaskStore` (an `abc.ABC` in `store.py`) is a genuine
boundary: two real, independent implementations — `JsonTaskStore` and
`SqliteTaskStore` — sit behind an identical load-all / save-all `State` contract, and
the manager never learns which one backs it. The `AgentRunner` `Callable` seam in
`manager.py` is also real: a live provider integration would drop straight in for the
default stub. Nothing is bolted-on.

**Codebase Y — strong, and broader.** The storage contract in `storage/ports.py` is
four narrow per-entity `Protocol`s (`TaskRepository`, `MemberRepository`,
`AgentRepository`, `ResultRepository`) plus a `StorageBackend` aggregate, each with two
real implementations (`json/` and `sqlite/`). The `Provider` `Protocol` in
`execution/provider.py` is a genuine seam whose plausible second implementation (an
HTTP call to a real model API) is described but correctly left unbuilt. Using
structural `Protocol`s means the concrete repos satisfy the ports without inheritance
or import coupling, and the per-entity split honors interface-segregation (each service
depends only on the repos it calls). Both codebases pass this test; Y's interfaces are
more finely segregated, X's are simpler and equally real.

---

## 3. Do the core objects do things, or are they data bags?

**Codebase X — mixed.** `Task` in `models.py` has real behavior (`advance`,
`assign_human`, `assign_agent`, `record_execution`) and `Status` is genuinely rich
(`next`, `is_terminal`). But `Task` is a plain `@dataclass` with public mutable fields:
any code can write `task.status = Status.DONE` directly, and the readiness/prerequisite
rule does not live on the task — it lives in `TaskManager`, which reaches into
`task.prerequisites` and other tasks' `.status`. So the task half-protects itself.

**Codebase Y — strong.** `Task` (`domain/task.py`) is fully encapsulated: private
fields, read-only properties, and behavior-only mutation (`assign_to`, `unassign`,
`change_status`, `readiness`). The title invariant is enforced in the one constructor
every construction path funnels through. `Prerequisites`, `AssigneeRef`, `Team`, and
`AgentRegistry` are all real objects that answer questions and enforce rules rather than
exposing raw state. `ExecutionResult` is deliberately a plain record, which is the
right call — it is a historical fact, and inventing behavior on it would be artificial.
This is the sharpest difference between the two codebases.

---

## 4. Does the core logic stay clean of storage/file details?

**Codebase X — weak (a real leak).** The domain in `models.py` owns its own
JSON-shaped serialization: every model has `to_dict`/`from_dict`, and the module
docstring frames this as a feature ("dataclasses carry their own JSON-friendly
(de)serialization"). The SQLite store then *reuses* that same dict shape for its
`assignee_json` column, so the domain's serialization format is effectively the
persistence format. That is a storage concern living in the objects that should only
know about tasks and rules.

**Codebase Y — strong.** The `domain/` package contains zero serialization. Each
repository owns its own `_to_row`/`_from_row` mapping, and no path, table, column, or
SQL string ever crosses out of `storage/`. The domain speaks only in domain terms; the
translation to disk is sealed entirely in the storage backends. This is textbook
separation and Y gets it right.

---

## 5. Tell-don't-ask?

**Codebase X — mixed.** Task commands are tell-style (`task.advance()`). But several
places pull data out and decide externally: `TaskManager.unmet_prerequisites` reaches
into `self._state.tasks[p].status`; `assignee_label` pulls the assignee out and
`isinstance`-branches on its concrete type; and `cli._cmd_execute` reaches into
`task.assignee` and `isinstance`-checks `AgentAssignee` to find the default agent.

**Codebase Y — strong.** Callers tell objects what to do: `task.change_status(...)`,
`registry.require_executable(task.assignee)` (the executability gate lives on the
registry, not in a caller's `if`), `task.readiness(completed)`. `AssigneeRef` exposes
`is_agent` and typed `as_member_id`/`as_agent_id` accessors so callers ask a small
named question instead of pulling `.kind` out and comparing. The one residual ask is
`TaskService._assignee_label` branching on `is_agent` for display — but that is a
presentation concern reading through the typed accessor, which is defensible.

---

## 6. Do the important concepts get their own types?

**Codebase X — weak.** A task id is a bare `int`, an agent id a bare `str`, and
prerequisites a bare `List[int]`. `Status` is a proper enum and the assignees are typed
value objects, which is good — but ids and the prerequisite set are primitives that
every call site has to remember how to handle, and a task id and an agent id are just
integers/strings with nothing stopping them being confused.

**Codebase Y — strong.** `MemberId`, `AgentId`, and `TaskId` are distinct value
objects (`domain/ids.py`) that each enforce the non-blank rule in one place and cannot
be mistaken for each other; `TaskId.new()` is the single id source. `Prerequisites` is
a first-class type owning its rules, `Status` and `Readiness` are enums, and
`AssigneeRef` is a typed reference whose accessors refuse to hand back an id of the
wrong kind. This is the difference the books keep pointing at, and Y is on the right
side of it. (A Metz caveat: for a tool this small, splitting the three id types is at
the edge of paying for itself — but the `as_member_id`/`as_agent_id` guards against
mixing member and agent ids are a concrete payoff, so it earns its keep.)

---

## 7. One conceptual change — one place, or many?

**Codebase X — usually localized, occasionally scattered.** A new status: edit the
`Status` enum and `_SEQUENCE`. The prerequisite/readiness rule: `TaskManager` only.
*But* introducing a new assignee kind ripples across `models.py`,
`assignee_from_dict`, `TaskManager.assignee_label`, and `cli._cmd_execute`. On the
other hand, because X has fewer layers, adding a plain field to a task is genuinely
*fewer* edits than in Y — `Task.to_dict`/`from_dict`, the SQLite columns, and the CLI —
roughly three sites.

**Codebase Y — predictable, but more sites per change.** Concepts are typed, so changes
land where you expect: a new status is `Status` only; a readiness/prerequisite rule is
`Prerequisites` only; a new backend is one branch in `build_backend` plus a new
subpackage. The cost of the layering shows up on a simple field addition: `Task`, both
`_to_row`/`_from_row` pairs (JSON and SQLite), the SQLite `schema.py` DDL, `TaskView`,
and the CLI formatter — around six sites across two backends. So Y localizes
*conceptual/rule* changes better but pays more for *shape* changes because there are
two full mapping layers to keep in sync. Call this roughly even, for different reasons.

---

## 8. Duplication vs. abstraction (the Metz question)

**Codebase X — one clear wrong abstraction.** `manager.py` builds a full transitive
cycle-detection routine (`_reaches`, a DFS over the whole prerequisite graph). Given
that X validates every prerequisite as an already-existing task and fixes prerequisites
at creation time only, every edge points from a newer task back to an older one, so a
cycle can never form — the DFS guards a state the structure already makes unreachable.
This is machinery built for a future that cannot arrive; a one-line self-reference
check would have covered the only real case. Elsewhere X is sensibly DRY (the SQLite
store reuses the model's assignee dict rather than re-deriving it).

**Codebase Y — mostly principled, and it explicitly avoided X's mistake.**
`domain/prerequisites.py` carries a long docstring reasoning out *why no cycle-detection
machinery is built* — the same acyclicity-by-construction argument — and enforces the
single existence-at-creation rule instead. That is exactly the Metz call: refuse the
wrong abstraction. Y also *accepts* duplication where abstracting would be wrong: the
JSON member and agent repositories are near-identical scan-upsert code, but Y did not
hoist a generic "JSON table repository," which would have been the wrong abstraction.
Y's own over-reach risks are milder and cheaper: `Readiness` as a two-value enum rather
than a bool, and the three separate id types for a small tool. These are defensible and
low-cost, and each is argued in a comment. On this question Y is clearly stronger —
X built the one piece of speculative machinery in either codebase.

---

## Best and worst single decision

**Codebase X**
- **Best:** the `TaskStore` boundary — a single small load-all / save-all `State`
  contract with two genuinely independent backends behind it, keeping the manager
  ignorant of storage. It is simple, real, and proportionate.
- **Worst:** letting persistence bleed into the domain — the `models.py` dataclasses
  own their JSON serialization and that dict shape becomes the storage format across
  both backends. (Runner-up: the unnecessary transitive cycle-detection machinery.)

**Codebase Y**
- **Best:** the rich, fully-encapsulated domain with single-owner rules — `Task`,
  `Prerequisites`, `Team`, and `AgentRegistry` each protect their own invariants, and
  the `domain/` package is kept completely free of storage. This is the design's spine
  and it is excellent.
- **Worst:** ceremony out of proportion to the product — ~25 files, four parallel
  repository classes with near-duplicate scan/upsert logic, two full object-to-row
  mapping layers to keep in lockstep, and several `build_*` composition helpers with
  overlapping defaulting logic (`execute`/`history` even rebuild an `ExecutionService`
  per invocation inside `_run`). None of it is wrong, but a reviewer feels the weight.

---

## Overall verdict

**Codebase Y is the better-designed of the two, on the axes this review weighs most:
single responsibility, rich self-protecting objects, first-class types for the core
concepts, a domain kept clean of storage, tell-don't-ask, and genuinely segregated
interfaces. Y is stronger on six of the eight questions (1, 3, 4, 5, 6, 8), roughly
even on two (2, 7).** Decisively, Y also avoided the single speculative abstraction
that X built (transitive cycle detection) and reasoned it away in prose — precisely the
Metz discipline of preferring a little structure-enforced simplicity over machinery for
an impossible state.

This is not a rout, and X is a good codebase, not a bad one. X is clean, cohesive, easy
to read end-to-end, and well-matched in size to the problem; its storage interface and
`Status` behavior are genuinely well done, and its lighter layering makes some ordinary
changes *cheaper* than in Y. A Metz-minded reviewer would dock Y for ceremony and praise
X's restraint. But the same panel would find X's two real weaknesses — anemic primitive
ids/prerequisites and a domain that carries its own serialization — to be exactly the
things the books warn against, and would find Y strong precisely where X is weak.

**Confidence: moderately high (~70–75%).** The gap is real but it is a gap of degree and
philosophy, not of one codebase being sound and the other broken. Weighted toward pure
OO design quality as the prompt asks, Y wins; weighted toward proportion-to-problem and
avoiding over-abstraction, the two draw closer — but even there Y comes out slightly
ahead because most of its abstractions pay for themselves and it declined the one that
would not have.
