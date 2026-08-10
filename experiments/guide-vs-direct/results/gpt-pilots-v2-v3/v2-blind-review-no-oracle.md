# Blinded software-evolution review: X vs. Y

## Scope and verification

This review uses only the anonymized stage snapshots, the four requirement files, and `review-rubric.md` in this review directory. I did not assign a composite numerical score.

All supplied tests pass:

| Repository | Stage 1 | Stage 2 | Stage 3 | Stage 4 |
|---|---:|---:|---:|---:|
| X | 9 passed | 19 passed | 27 passed | 34 passed |
| Y | 9 passed | 18 passed | 25 passed | 33 passed |

X was run with `PYTHONPATH=. python -m unittest discover -v`; Y was run with `PYTHONPATH=. python -m unittest discover -s tests -v`. Y's explicit `-s tests` is documented in its README and is needed because its `tests` directories are not packages. I also ran Y through pytest in an isolated temporary environment, with the same passing results. The available interpreter was Python 3.12.13, not exactly 3.11; both codebases appear to use Python 3.11-compatible language/library features.

## Behavior

### Stage 1

**X: satisfies the stage.** `TaskManager` creates JSON-persisted tasks, assigns a stable UUID, initializes `todo`, changes among the three allowed status strings, and lists assignee/status. Tests cover creation, every status, invalid status without mutation, missing IDs, persistence through fresh manager instances, and separate CLI invocations (`X/stage-1/tests/test_core.py`, `test_cli.py`). The main uncovered edge is input validation: empty or whitespace-only title, description, and assignee are accepted. Malformed/corrupt JSON handling is also untested.

**Y: satisfies the stage.** The SQLite `TaskRepository` supplies the same workflow with integer IDs, and the CLI includes descriptions as well as assignee/status. Its coverage is stronger around validation: whitespace-only required fields are rejected, common spellings of `in progress` are normalized, invalid status leaves the task unchanged, and missing IDs and reopen persistence are tested (`Y/stage-1/tests/test_storage.py`).

### Stage 2

**X: satisfies the stage.** `AIAssignee`, `AgentExecutor`, `ExecutionRequest`, and `LocalFakeAgentExecutor` add provider/model identity and a deterministic network-free execution boundary. `TaskManager.execute_task` rejects human tasks and persists an execution result. Tests cover request content, persistence across reload/CLI invocations, deterministic local output, human and unknown-task rejection without mutation, and compatibility with stage-1 string-assignee JSON (`X/stage-2/tests/test_core.py`, `test_cli.py`). It does not reject an empty executor result, although the requirement does not explicitly require non-empty output.

**Y: satisfies the stage.** `AIAgent` and `AgentExecutor` are separated from `TaskExecutionService`; the service rejects human tasks and empty results before saving. SQLite migration adds AI columns without losing a stage-1 human task. Tests cover a recording executor, deterministic fake, no call for human tasks, no persistence of an empty result, CLI assignment-shape errors, provider/model/result persistence, and migration (`Y/stage-2/tests/test_agents.py`, `test_cli.py`, `test_storage.py`).

### Stage 3

**X: satisfies the stage.** JSON remains the compatible default and SQLite is selectable in the CLI. Both implement the narrow `TaskStorage.load_tasks/save_tasks` capability (`X/stage-3/task_manager/storage.py:16-23`). A shared parity test executes the same human/AI/status/result workflow against both concrete backends, an in-memory implementation proves task rules are independent of JSON, and a failed SQLite snapshot is tested for rollback (`X/stage-3/tests/test_storage_boundary.py:36-142`). CLI tests also cover independent backend defaults, invalid selection, and equivalent multi-process workflows.

**Y: satisfies the stage.** SQLite remains the default and `JSONTaskRepository` is selectable. JSON uses atomic replacement and reports invalid JSON without overwriting it. Tests cover a full JSON CLI workflow, persistence/reopen, structured agent data, validation/error parity, and continued SQLite migration (`Y/stage-3/tests/test_cli.py`, `test_json_storage.py`, `test_storage.py`). Unlike X, it does not run one common repository contract suite over both backends; similar behavior is asserted in backend-specific tests and the CLI workflow.

### Stage 4

**X: satisfies the stage, with particularly strong invariant tests.** Prerequisite IDs are accepted for human and AI tasks, preserved by JSON and SQLite, shown on request in the CLI, and checked before either transition to `in-progress` or AI execution. The error reports every unfinished prerequisite's ID, title, and status. `test_both_start_paths_share_blockers_then_succeed_when_ready` runs against both backends and asserts identical blocker objects for the two start paths, no executor call, no in-memory or persisted mutation while blocked, and success after all prerequisites become done (`X/stage-4/tests/test_readiness.py:39-138`). Other tests cover unknown prerequisites without partial creation, ordered persistence, a pre-stage-4 SQLite database, both-backend CLI behavior, and previous no-prerequisite behavior.

**Y: satisfies the stage behaviorally.** Both repositories persist prerequisite IDs, reject unknown IDs, expose blockers, prevent `in progress`, and let `TaskExecutionService` prevent AI execution. The CLI reports blocker ID/status clearly, and stage-3 JSON without the new field remains readable. Tests exercise both start paths through both CLI backends (`Y/stage-4/tests/test_cli.py:160-209`), repository-specific readiness, no executor call/result while blocked, unknown prerequisites, SQLite migration, and JSON compatibility.

Important remaining edge cases in both are outside the stated requirement: neither supports adding/changing prerequisites after creation, and both deliberately allow an already-started dependent task to remain started if a prerequisite is reopened. X explicitly tests that latter behavior. Public creation only points backward to existing tasks, so cycles/self-dependencies cannot be created normally. X preserves duplicate prerequisite IDs rather than normalizing them; Y deduplicates them. X's readiness helper assumes every persisted prerequisite still exists, so hand-corrupted JSON can cause a `KeyError` rather than a domain/storage error; Y turns a dangling JSON reference encountered during readiness into `StorageError`.

**Behavior judgment:** both repositories meet every staged requirement. Y has somewhat stronger input/corruption validation; X has the stronger cross-backend, cross-entry-point stage-4 invariant test.

## Change locality

Production-only diff sizes are evidence about churn, not quality scores:

| Change | X production modules | X diff | Y production modules | Y diff |
|---|---|---:|---|---:|
| Stage 1 -> 2 | `__init__`, `cli`, `core` | +260/-13 | `__init__`, `cli`, `models`, `storage`; new `agents`, `service` | +199/-10 |
| Stage 2 -> 3 | `__init__`, `cli`, `core`; new `models`, `storage` | +330/-122 | `__init__`, `cli`, `storage`, `service`; new `json_storage` | +263/-10 |
| Stage 3 -> 4 | `__init__`, `cli`, `core`, `models`, `storage` | +221/-10 | `__init__`, `cli`, `models`, `service`, `storage`, `json_storage` | +267/-15 |

### Stage 1 locality

As greenfield baselines, neither repository needs a preparatory refactor or introduces a speculative interface. X puts the task model, lifecycle, and JSON persistence together in `core.py`, with CLI/composition in `cli.py`; this is compact but couples responsibilities that stage 3 later separates. Y starts with `models.py`, SQLite `storage.py`, and `cli.py`; the module split is cleaner, although `TaskRepository` already combines persistence with creation validation and status-transition behavior.

### Stage 2 locality

X changes only its existing composition/export, CLI, and monolithic core. Those changes are directly related to AI identity, execution, and serialization, but the monolith means model, lifecycle, executor, and JSON changes accumulate in `core.py`.

Y changes the model and SQLite schema, adds the AI executor/service, and wires the CLI. These are all related to the feature. The separate `agents.py` and `service.py` are product-driven rather than speculative: a fake/local executor is explicitly required, and tests supply another executor.

### Stage 3 corrective refactor and locality

X requires a visible corrective/preparatory refactor in the same stage as the feature. It extracts `Task`/assignee data into `models.py`, extracts JSON serialization from `core.py`, introduces the `TaskStorage` boundary, and adds SQLite. The 122 deletions largely reflect removing persistence from `core.py`. This is larger churn, but it is tightly tied to the requirement: selectable persistence is exactly the product force that justifies the separation. The result is materially better locality for later lifecycle changes: application behavior stays in `TaskManager` and each storage backend only loads/saves task state.

Y achieves smaller additive churn and does not need a large preparatory rewrite: it adds `TaskStore`, changes the service's annotation, adds the JSON repository, and selects it in the CLI. That is the strongest raw-locality evidence for Y. However, the avoided refactor leaves general behavior inside persistence implementations. `JSONTaskRepository` reimplements required-field validation, human and AI creation, ID allocation, status parsing/update, lookups, and result saving already present in the SQLite repository. The changed files are feature-related, but the extension point is too broad: it treats every application use case as a storage operation.

Both stage-3 extension points are non-speculative. X has JSON, SQLite, and an in-memory test implementation of `TaskStorage`; Y has JSON and SQLite implementations of `TaskStore`.

### Stage 4 locality

For either repository, changes to the task model, both storage formats, and CLI are expected: prerequisites are new persisted/domain data with user-facing declaration and errors.

X additionally changes `core.py`, the existing lifecycle owner. Its storage changes are representation-only (JSON field plus SQLite relation/migration); the readiness rule is not copied into storage. Stage 4 therefore validates the stage-3 refactor.

Y changes both storage implementations not only for representation but also for prerequisite normalization/validation, readiness lookup, and status-transition blocking. `service.py` separately adds AI-execution blocking. This is broader rule-related churn and is a direct consequence of the stage-3 boundary shape.

**Locality judgment:** Y is more locally additive at stage 3 in a diff-count sense. X pays a justified corrective-refactor cost, then has better semantic locality: lifecycle changes have one behavior owner and persistence changes remain persistence-specific.

## Responsibility and ownership

### X

- **Task lifecycle:** clear from stage 3 onward. `TaskManager` owns create, status change, AI execution, and, at stage 4, readiness (`X/stage-4/task_manager/core.py:112-225`). In stages 1-2 it also owns lifecycle but is mixed with JSON mechanics.
- **Assignee-specific behavior:** justified and compact. `AIAssignee` distinguishes AI from human names; only the AI branch constructs an `ExecutionRequest` and crosses `AgentExecutor`. Human task behavior remains the general `TaskManager` path.
- **Persistence containment:** strong after the stage-3 extraction. The application depends on only `load_tasks` and `save_tasks`; JSON/SQLite format details remain in `storage.py`. The CLI is the composition root that selects a concrete backend.
- **Stage-4 readiness:** coherent. Both `change_status(..., "in-progress")` and `execute_task` call the same `_require_prerequisites_done` method (`core.py:153`, `core.py:180`, implementation at `core.py:207`). That method creates the single blocker representation/error.

### Y

- **Task lifecycle:** fragmented. Status parsing is in `TaskStatus`, creation/status mutation/field validation are implemented independently in both repositories, and AI execution is in `TaskExecutionService`.
- **Assignee-specific behavior:** the service/executor separation is justified and makes the AI path easy to test. The model's simultaneous `assignee: str` plus optional `agent` is redundant, though: an AI task stores both a display-like assignee string and structured identity, permitting inconsistent hand-constructed state.
- **Persistence containment:** format mechanics are in storage modules, but storage choices leak into application responsibility because the `TaskStore` protocol contains high-level use cases (`create_task`, `create_agent_task`, `update_status`, `incomplete_prerequisites`) rather than persistence primitives (`Y/stage-4/task_manager/storage.py:35-63`). Consequently each backend owns and duplicates general task rules.
- **Stage-4 readiness:** behavior is correct but ownership is not coherent. SQLite and JSON each implement `incomplete_prerequisites` (`storage.py:305`, `json_storage.py:222`). Each repository's `update_status` queries blockers and raises `TaskBlockedError` (`storage.py:315`, `json_storage.py:239`), while `TaskExecutionService.execute_task` independently performs the same query-and-raise sequence (`service.py:19-34`). The protocol shares a method name, not one policy implementation. A third backend would have to reproduce readiness calculation and remember to enforce it in `update_status`, while the service separately enforces execution.

**Ownership judgment:** X is stronger. Y's AI-specific separation is good, but general lifecycle behavior and the readiness invariant are coupled to storage and duplicated across status-change and AI-execution paths.

## Product invariants

### 1. Created tasks are stable, persisted, and initially `todo`

- **X enforcement:** `TaskManager.create_task`; `_save` through the selected storage. **Tests:** core creation/reload and CLI multi-invocation tests at every stage; stage-3 concrete parity test. **Bypass:** a caller can hand a `TaskStorage` arbitrary `Task` values; the boundary intentionally trusts loaded domain objects.
- **Y enforcement:** both repository `create_task`/`create_agent_task` methods. **Tests:** repository and CLI workflow/reopen tests for SQLite and JSON. **Bypass:** hand-edited storage or hand-constructed `Task` values; normal repository APIs preserve it.

### 2. Status is one of `todo`, `in progress`, and `done`

- **X enforcement:** `TaskManager.change_status` checks `ALLOWED_STATUSES`. **Tests:** all allowed transitions, invalid status, and no mutation. **Bypass:** X's JSON loader and SQLite schema do not independently validate status, so corrupt/directly written storage can expose another value.
- **Y enforcement:** `TaskStatus.parse`, SQLite's `CHECK`, and JSON deserialization through `TaskStatus`. **Tests:** common spellings, invalid status, and no mutation in both repositories. **Bypass:** normal APIs do not; directly constructed Python `Task` objects are not runtime-validated.

### 3. AI execution applies only to AI-assigned tasks, uses provider/model identity, and stores a result

- **X enforcement:** `TaskManager.execute_task` checks `AIAssignee`, constructs `ExecutionRequest`, calls the executor, then saves. **Tests:** recording fake/request assertions, human/unknown rejection, persisted result, CLI restart. **Bypass:** directly invoking an executor or a storage implementation is below/outside the manager API.
- **Y enforcement:** `TaskExecutionService` checks `task.agent`, calls `AgentExecutor`, rejects empty output, and calls `save_execution_result`. **Tests:** recording executor, human no-call, empty no-save, persistence, CLI. **Bypass:** repositories publicly expose `save_execution_result`, so a caller can store a result without going through the AI-only service; that method is best understood as the persistence port, not the product operation.

### 4. Storage selection does not change task behavior

- **X enforcement:** all lifecycle behavior executes once in `TaskManager` over the narrow storage interface. **Tests:** one complete concrete-backend parity test plus an in-memory boundary test. **Bypass/drift risk:** low for a correctly functioning storage implementation; corrupt/stale data can still violate assumptions.
- **Y enforcement:** the `TaskStore` protocol and similar code in both repositories. **Tests:** backend-specific repository tests and cross-backend CLI workflows. **Bypass/drift risk:** higher because new rules must be repeated in each repository; structural conformance to `TaskStore` does not guarantee equivalent behavior.

### 5. Prerequisite references must exist when a task is created

- **X enforcement:** `TaskManager.create_task` validates all IDs before appending/saving; SQLite also uses foreign keys. **Tests:** unknown mixed with known IDs creates no partial task on both backends; persistence tests. **Bypass:** direct storage/hand-edited JSON can introduce dangling references; readiness then assumes existence and can raise `KeyError`.
- **Y enforcement:** duplicated validation in both repository creation paths; SQLite additionally uses foreign keys. **Tests:** both repositories and CLI reject unknown prerequisites without creation. **Bypass:** hand-edited JSON can contain a dangling reference, although readiness reports it as `StorageError` rather than silently starting.

### 6. A task cannot start or be AI-executed until every prerequisite is done

- **X enforcement:** one `_require_prerequisites_done` method called by both product paths. **Tests:** the same blocker tuple/error is asserted for both paths against JSON and SQLite; no executor call and no state/result mutation are also asserted. **Bypass:** direct lower-level storage/executor access, or stale state in a long-lived manager in a concurrent-process scenario.
- **Y enforcement:** blocker calculation in each backend; query-and-raise logic in each backend's status update and separately in `TaskExecutionService`. **Tests:** both paths and both backends, plus no executor call/result while blocked. **Bypass:** direct `save_execution_result`; a future `TaskStore` implementation can also forget the status rule while still satisfying the protocol signature.

### 7. Existing no-prerequisite data keeps its prior behavior

- **X enforcement:** `Task.prerequisites` defaults to `()`, JSON reads a missing field as `[]`, and the SQLite relation can be absent/empty. **Tests:** pre-stage-4 SQLite compatibility, earlier core suites, and both-backend no-prerequisite workflows.
- **Y enforcement:** the model default, JSON's missing-field default, and the new SQLite dependency table. **Tests:** stage-3 JSON compatibility, stage-1 SQLite migration, and retained earlier suites.

## Accidental complexity

### X

- `AgentExecutor` exists for replaceability, but that flexibility is required by the fake/local-agent requirement. It has one production implementation and multiple test implementations; it remains useful unchanged through stages 3 and 4.
- `TaskStorage` is introduced only when two formats are required. It has two production implementations and an in-memory test implementation. Stage 4 demonstrates its value: the readiness policy is added once above both backends.
- `TaskStorageSource` plus `resolve_task_storage` is a small compatibility adapter allowing the old path-based constructor and the new explicit storage object. It is a minor pass-through layer, but it protects existing callers rather than speculating about future behavior.
- `ExecutionRequest` is an extra DTO, but it makes the agent boundary explicit and prevents the executor from depending on the whole persistence/domain object.
- The chief historical complexity is the stage-1/2 `core.py` monolith, which forces the stage-3 corrective extraction. After that extraction, tracing a use case is straightforward: CLI -> `TaskManager` -> storage/executor boundary.

### Y

- `AgentExecutor` has a production fake and test recorder and is justified. `TaskExecutionService` is thin but not merely pass-through: it protects human-task execution, empty results, and now readiness.
- `TaskStore` has two real implementations and is therefore not speculative, but its broad shape creates substantial duplication. Both repositories implement not just persistence but input validation, task creation, AI creation, ID policy, status rules, prerequisite rules, and result mutation. This is the largest accidental complexity and makes behavior harder to trace and keep aligned.
- `SQLiteTaskRepository = TaskRepository` is a compatibility/name alias rather than an abstraction with separate behavior. It adds two public names for one implementation.
- `StorageError` meaningfully wraps JSON read/write failures, but SQLite failures generally remain raw `sqlite3` errors; the common error abstraction is only partially realized.
- The `assignee` string plus optional structured `agent` duplicates identity state for AI tasks.
- Earlier abstractions do become useful: the stage-2 executor/service are reused at stage 4, and stage-3 `TaskStore` allows the service to accept either backend. The cost is that stage 4 extends the broad port with `incomplete_prerequisites` instead of locating the product policy above storage.

**Accidental-complexity judgment:** neither repository is dominated by speculative interfaces. X's abstractions are narrower and gain clear later-stage value. Y's abstractions also have real uses, but its broad repository interface produces pass-through coordination and duplicated product logic.

## Final judgment

### Strongest evidence favoring X

Stage 4 is a direct architecture test, and X passes it cleanly: one lifecycle owner and one readiness helper govern both status change and AI execution for both storage formats. The tests prove identical blockers and non-mutation at both entry points. The stage-3 storage abstraction is narrow, has multiple implementations, and demonstrably reduces later policy duplication.

### Strongest evidence favoring Y

Y evolves stage 3 with less corrective churn: +263/-10 production lines versus X's +330/-122, and it already has separate model, persistence, and AI service/executor modules. It also has stronger defensive behavior: nonblank field validation from stage 1, empty AI-result rejection, explicit SQLite migrations, SQLite status constraints/foreign keys, JSON corruption errors, and `fsync` before atomic replacement. Its stage-4 behavior and tests are fully functional.

### Important counterevidence

Against X, the stage-1/2 monolith was not ready for selectable storage, so stage 3 requires a substantial extraction. X accepts blank fields, does not validate persisted status at the storage boundary, and can surface a low-level `KeyError` for a corrupt dangling prerequisite. Its in-memory full-snapshot manager can also become stale across multiple long-lived/concurrent instances.

Against Y, its smaller stage-3 diff hides duplicated application behavior. Stage 4 makes the cost concrete: two readiness calculations, two repository status checks, and a separate service execution check. The broad `TaskStore` protocol does not centralize invariants, and the dual assignee representation can drift.

### Uncertainties not settled by static review and supplied tests

- Concurrent writers are not stress-tested. X's cached full snapshot and both JSON implementations' load/modify/replace flows may lose concurrent updates; Y's SQLite path is likely stronger here, but that was not benchmarked or raced.
- Scale/performance is unknown. X rewrites a complete snapshot; Y's stage-4 SQLite listing/readiness performs repeated queries.
- Crash behavior is partly but not comprehensively tested. X tests SQLite rollback; Y explicitly `fsync`s JSON, but no fault-injection suite covers all write phases.
- Exact Python 3.11 execution was not available; testing used 3.12.13.
- Real provider integration is intentionally absent, so executor timeout/failure semantics are unknown and outside the current requirement.
- The next requirement is deliberately unknown; a persistence-heavy next change could favor Y's mature SQLite implementation, while a lifecycle-heavy change more clearly favors X.

### Repository I would extend with one more unknown requirement

**I would choose X.** The preference is not based on a composite score or on current behavior—both are correct. It is based on change-risk containment. After the justified stage-3 correction, X has one place for lifecycle invariants, one narrow persistence port with multiple proven implementations, and one executor port. Stage 4 shows the practical payoff: the new readiness rule is expressed once and applies to both status change and AI execution, while storage changes only encode prerequisite data. An unknown product rule is therefore more likely to require one coherent change and one shared contract test.

Y is the credible alternative when defensive storage engineering and minimal immediate churn dominate. For an unknown requirement, however, its duplicated repository behavior creates more places to discover, edit, and keep consistent, which is the larger software-evolution risk.
