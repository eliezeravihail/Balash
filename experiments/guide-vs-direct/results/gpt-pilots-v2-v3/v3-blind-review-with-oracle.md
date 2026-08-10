# Blinded software-evolution review: X vs Y

## Scope and method

I reviewed the four anonymized snapshots of X and Y against every staged requirement, the operator-only product facts, and `review-rubric.md`. I compared each adjacent production snapshot, inspected the tests and documentation, and ran every supplied test suite with Python bytecode generation disabled so the reviewed snapshots were not changed.

All supplied tests passed:

| Repository | Stage 1 | Stage 2 | Stage 3 | Stage 4 |
|---|---:|---:|---:|---:|
| X | 11 passed | 21 passed | 34 passed | 42 passed |
| Y | 5 passed | 9 passed | 14 passed | 17 passed |

Test count is not a quality score: X has many inherited unit tests run once per backend, while Y has fewer but denser end-to-end and cross-backend scenarios.

## Behavior

### Stage 1

**X:** Satisfies the stated CLI behavior: create, assign/reassign, status changes, list, and SQLite persistence are present and tested. It validates blank fields and invalid statuses and reports missing task IDs clearly. However, it is already out of alignment with the operator facts. `create` requires `--assignee` (`X/stage-1/team_tasks/cli.py:29`), `TaskRepository.create_task` rejects an empty assignee (`repository.py:80-83`), and an assignee is a single string (`repository.py:21`), not the available stable member ID plus display name. Thus an initially unassigned task—the intended product model—is impossible.

**Y:** Satisfies the stated behavior and matches the product facts more closely. Tasks are created unassigned (`Y/stage-1/task_cli.py:81-87`), then assigned using separate stable `member_id` and `display_name` values (`task_cli.py:93-103`). Stable task IDs, restart persistence, reopening, invalid statuses, unknown tasks, and blank titles are covered through actual subprocess restarts. Judgment: Y is behaviorally and product-model superior at stage 1; X meets the visible request but hard-codes a narrower assignee model.

### Stage 2

**X:** Adds an `AIAgent`, a testable `AgentExecutor` protocol and local fake, human/agent reassignment, persistence, migration of a stage-1 SQLite database, and rejection of human-task execution. This is enough for a literal reading of “store an execution result,” because one result string is stored on the task. It does not satisfy the more concrete operator facts: provider/model are embedded in every task (`X/stage-2/team_tasks/repository.py:26-32`) instead of belonging to a stable AI-agent entity, and the only durable result is `execution_result: str | None`. It has no agent ID or success/failure field and retains no history; a rerun overwrites the prior text, and reassignment to a human deliberately deletes it (`repository.py:208-216` in stage 3, retained later). The CLI also continues to require exactly one assignee at creation, contrary to the product facts.

**Y:** Adds persistent AI agents with stable IDs and provider/model configuration, task references to those agents, and append-only execution records containing task ID, agent ID, success/failure, and output. The tests demonstrate both success and failure, two retained history entries after restart, no task-status side effect, duplicate-agent rejection, and no partial result for invalid execution. Stage-1 JSON is upgraded compatibly. Judgment: both demonstrate local fake execution, but Y is decisively more faithful to the intended product and preserves information X discards.

### Stage 3

**X:** Keeps SQLite as the default, adds JSON selection at startup, and uses a genuinely different JSON file. The inherited repository test class runs most lifecycle behavior against both repositories, and a JSON CLI workflow is tested. Observable behavior is currently equivalent on the tested paths. The significant weakness is how parity is achieved: `JsonTaskRepository` reimplements creation, assignment, status change, AI validation/execution, and result updating already present in `TaskRepository` (`X/stage-3/team_tasks/json_repository.py:86-206` versus `repository.py:122-263`). It imports the domain model and private helpers from the module whose stated responsibility is SQLite. There is no shared lifecycle owner or common production interface, so parity depends on keeping two implementations synchronized.

**Y:** Stage 3 performs a product-driven refactor. `StateStore` is a narrow load/save boundary with two real implementations (`Y/stage-3/task_cli.py:66-299`), while `TaskService` owns the lifecycle once (`task_cli.py:302-432`). The JSON default and existing JSON format remain usable; SQLite is meaningfully different and transactional. Tests compare complete CLI output, loaded logical state, and failure atomicity across both backends, as well as SQLite rollback and backend-specific defaults. Judgment: both satisfy stage 3, but Y has much stronger structural and test evidence that product behavior is actually backend-independent.

### Stage 4

**X:** Adds an explicit `add-prerequisite` operation, persists dependency edges in a relational SQLite table or per-task JSON lists, rejects self-dependencies and direct/indirect cycles, makes duplicate addition idempotent, and guards both entering `in progress` and AI execution. Errors include blocking task ID, title, and status. The same inherited tests exercise these cases for both backends, including persistence, cycle rejection, no executor call/no result while blocked, and old-store compatibility. The literal stage text is met well. One operator fact is not: because `change_status` guards only the exact target `in progress` (`X/stage-4/team_tasks/repository.py:250-252` and `json_repository.py:159-163`), a `todo` task with unfinished prerequisites can be moved directly to `done` rather than staying `todo`. The architectural cost is that graph traversal and readiness rules are implemented twice: `_require_no_dependency_cycle` and `_require_prerequisites_done` appear in both `repository.py:311-333` and `json_repository.py:212-234`.

**Y:** Adds prerequisites at task creation. Every prerequisite must already exist, so all edges point from a newly created task to an older task; direct and indirect cycles are impossible through the application API. `_require_prerequisites_ready` in `TaskService` (`Y/stage-4/task_cli.py:355-369`) is the one guard used by both AI execution (`:450-467`) and transition to `in progress` (`:487-496`), independent of storage. Tests show identical blockers in both paths and backends, all unfinished IDs/statuses, no result-ID gap on blocked execution, duplicate prerequisite collapse, partial completion, reopening behavior, atomic rejection of unknown/self IDs, and both migrations. Y has the same operator-fact defect as X: `transition_task` guards only `in progress`, and the parity test explicitly moves a still-blocked task directly to `done` (`Y/stage-4/tests/test_backend_parity.py:283-285`). The other limitation is usability: there is no way to add or change a prerequisite on an already-created task, so a valid dependency whose prerequisite was created later cannot be represented. The requirements do not explicitly demand mutable dependency edges, but X supports the broader natural interpretation.

**Behavior judgment:** Both final snapshots satisfy the explicit stage-4 guard wording and all supplied tests, but both violate the additional product fact that a blocked task stays `todo` by permitting a direct change to `done`. Y is substantially more faithful to the product facts across stages 1–3. X has the stronger stage-4 dependency-management surface because dependencies can be added in arbitrary creation order and cycles are explicitly detected.

## Important failure and edge-case coverage

X covers blank required text, status aliases and rejection, missing tasks, restart persistence, stage-1 SQLite migration, human/AI reassignment, human execution rejection, deterministic fake output, backend repetition of repository tests, stage-3 JSON migration, blocked `in progress`/execution, executor non-invocation, duplicate edges, self-dependency, indirect cycles, and prerequisite persistence. Important omissions are exactly the product behaviors its model lacks: unassigned tasks, stable human and AI identity, explicit success/failure results, repeat-execution history, and result-history preservation. It also does not test that a blocked task cannot jump directly to `done`—the implementation permits the jump—and has no deliberate malformed-store or nested-path test.

Y covers subprocess-level restart persistence; unassigned/human/AI paths; stable IDs; duplicate agents; success, failure and durable history; invalid operations without partial writes; stage-1/stage-2 JSON compatibility; exact success and failure parity across JSON/SQLite; SQLite rollback; blocked dependency behavior in both explicitly guarded paths; no result gaps; duplicate prerequisite input; partial completion; reopened prerequisites; unknown/self references; and stage-3 SQLite migration. It does not exercise an explicit multi-node cycle attempt because its append-only task-creation API makes such a request inexpressible. Its test that permits a blocked task to jump to `done` confirms backend parity but codifies behavior contrary to the operator fact. Neither repository has crash-injection, concurrent-writer, or corrupted dependency-graph tests; those are lower priority for the stated one-operator/small-team product.

## Change locality

| Stage change | X production change surface | Y production change surface | Judgment |
|---|---|---|---|
| 1 baseline | Package with CLI and SQLite repository | One script containing CLI and JSON store | X has cleaner physical packaging; Y begins closer to the product model. |
| 2 AI agents | New `agents.py`; changes to `repository.py`, `cli.py`, and exports | `task_cli.py` only | X’s module split is sensible, but repository schema/behavior and CLI legitimately had to change. Y’s changes remain in one file, within its then-existing store and CLI sections; no unrelated module was touched. |
| 3 second backend | New `json_repository.py`; changes to `cli.py`, exports, and a SQLite-repository alias | `task_cli.py`: splits persistence from a new shared service and adds SQLite | X avoids a preparatory refactor but pays by copying product logic. Y requires a larger preparatory refactor, but every new seam is directly tied to the storage-selection force and immediately has two implementations. |
| 4 prerequisites | `repository.py`, `json_repository.py`, `cli.py`, and exports | `task_cli.py`, conceptually the service, both persistence adapters, and CLI sections | Both storage schemas and the CLI necessarily change. Only X must change two copies of lifecycle/graph rules; Y changes lifecycle once and each adapter only for representation. |

No evidence suggests either repository changed unrelated responsibilities merely to inflate architecture. The key distinction is conceptual locality: X’s separate files look local in a tree, but a lifecycle change fans out across backend-owned repositories. Y’s one physical file looks broad, but the change is localized to coherent internal sections.

## Responsibility and ownership

### Task lifecycle

X has no storage-independent lifecycle owner. `TaskRepository` mixes domain validation, lifecycle, AI execution, migrations, and SQLite SQL; `JsonTaskRepository` mixes the same domain behavior with JSON serialization. The shared `Task` dataclass and helper imports reduce some duplication but do not own the operations. In particular, JSON imports private `_required` and `_blocked_task_error` from the nominal SQLite repository, which is an ownership smell.

Y has a clear owner: `TaskService` owns creation, assignment, agent creation, execution, status changes, prerequisite readiness, and listing. `JsonStateStore` and `SQLiteStateStore` translate one logical state to durable formats. The 668-line stage-4 file does not erase those boundaries: the file is organized into validation/state helpers, a `StateStore` protocol, two storage implementations, `TaskService`, presentation helpers/parser, and command dispatch. The concern is navigation and loose `dict[str, Any]` data, not absence of boundaries.

### Assignee-specific behavior

X does separate fake execution mechanics into `agents.py`, and `execute_task` rejects non-agent tasks. But agent identity/configuration is still task fields, human identity is one string, and general task persistence is cluttered with nullable agent columns and conditionals. Y represents human assignees and AI assignees differently only where justified, keeps agent configuration in persistent agent records, and centralizes the execution-only-for-AI rule.

### Persistence containment

X contains file/SQL mechanics in repository modules, but those modules also duplicate product behavior. Storage does not leak heavily into CLI beyond repository construction, yet the domain imports flow from the SQLite repository into JSON. Y’s CLI constructs a selected `StateStore`, then deals with `TaskService`; storage format does not affect lifecycle logic. Y’s boundary is coarse—it loads and rewrites the complete state—and SQLite serializes an assignee as JSON, but for 3–10 users and one local operator this is proportionate and explicitly transactional.

### Stage-4 eligibility ownership

Within each X backend, both status and AI execution call one `_require_prerequisites_done` helper, so there is no duplication between the two paths in a single repository. Across the application, however, that helper and its traversal are copied into both backend repositories. A third backend or changed readiness rule creates another synchronization point.

Y enforces readiness in exactly one `TaskService._require_prerequisites_ready` method, used from both guarded paths before saving or invoking the fake. This is the clearest ownership result in either repository.

## Product invariants

| Invariant | X enforcement and tests | Y enforcement and tests | Bypass assessment |
|---|---|---|---|
| Task IDs are stable and data survives restart | SQLite autoincrement/JSON `next_id`; repository reopen tests | `next_id` in shared logical state; cross-process and cross-backend tests | Direct external store edits can violate either; normal application paths cannot. |
| Title/description are nonblank | Shared `_required`; repository tests on each backend | `_required_text` in `TaskService`; CLI tests | Both normal creation paths enforce it. Y’s raw `StateStore.save`, and X’s direct SQL/JSON edits, are lower-level bypasses. |
| Status is one of three values | Shared `normalize_status`; SQLite `CHECK`; inherited backend tests | CLI choices plus `TaskService.transition_task`; tests on invalid and direct transitions | Public lifecycle paths are safe. Y’s adapter layer deliberately trusts logical state; X JSON deserialization also trusts stored status. |
| A task may be unassigned | Not supported: creation requires a human or embedded AI assignee | `create_task` writes `assignee: None`; tested and displayed | This is a product-fidelity failure in X, not merely a bypass risk. |
| Human identity has stable ID plus display name | Not modeled; one assignee string | Human assignment stores both and tests display both | X cannot enforce identity stability. |
| Provider/model belong to an AI agent | Stored on every X task; no stable agent entity | Stored once on a persistent agent record, task stores agent ID | X’s model violates the stated ownership fact. |
| Only AI-assigned tasks execute | Both repositories check `is_assigned_to_agent`; human rejection tests | `TaskService.execute_task` distinguishes unassigned/human/AI and resolves an existing agent; tests | No normal CLI path bypasses this. |
| Results identify task, agent, outcome, and output | Only one text field on task; reruns overwrite and reassignment clears | Append-only record has all four facts; success/failure/history and restart tested | X does not establish the intended invariant. Y’s normal path does. |
| Both storage choices have equivalent observable behavior | Similar methods are implemented twice; inherited tests run most repository cases twice and one JSON CLI flow | One shared service plus exact output/state/failure parity tests | X has no current tested divergence, but future changes can bypass parity by updating one repository. Y structurally prevents most lifecycle drift. |
| Prerequisite IDs exist and duplicates are harmless | `add_prerequisite` resolves both tasks and uses insert-ignore/set-like replacement; tested twice | Creation resolves every ID and de-duplicates in first-seen order; tested across backends | Normal paths enforce this. Raw state edits can bypass both. |
| Dependency graph is acyclic | Explicit DFS before adding an edge in both repositories; direct/indirect/self tests | Edges can only be created from a new task to already-existing tasks, so cycles are unrepresentable; unknown/self attempts are atomic | X supports mutable edges with explicit validation. Y’s invariant is stronger by construction but restricts valid editing workflows; neither validates a manually corrupted pre-existing cycle on load. |
| A blocked task cannot enter `in progress` and stays `todo` | Per-backend shared readiness helper guards only `in progress`; no direct-`done` test | One service readiness helper guards only `in progress`; parity test deliberately allows direct `done` | The `in progress` half is enforced, but direct `todo` -> `done` is a normal CLI bypass in both and violates the operator fact that the task stays `todo`. |
| A blocked AI task does not execute or store a result | Readiness checked before executor in both repositories; executor-call/result tests | Readiness checked before outcome/result creation; no-result-gap tests | Normal execution paths are safe. X duplicates the rule by backend; Y has one owner. |
| Old tasks default to no prerequisites | SQLite prerequisite table and JSON default field; migration tests | JSON state default plus SQLite column migration; migration tests | Covered for supplied prior formats in both. |

## Accidental complexity

### X

- `AgentExecutor` has one production implementation, but a second recording implementation in tests. It is justified by the explicit need for a testable local/fake execution seam rather than speculative provider infrastructure.
- `AIAgent` and the immutable `Task` dataclass make data and execution inputs easy to understand. The installable package and `__main__` entry point are useful, not accidental.
- `SQLiteTaskRepository = TaskRepository` is only a naming alias, not a meaningful abstraction. More importantly, there is no common lifecycle abstraction above the two real repositories.
- The largest accidental complexity is duplicated product logic. At stage 3, creation, assignment, status and AI execution are repeated across repositories; at stage 4, graph traversal and eligibility are repeated too. Separate files therefore hide, rather than solve, shared ownership.
- The cross-import from JSON into private helpers in `repository.py` couples the new backend to a module named and documented as SQLite persistence. A future extraction to a domain/service module is now more difficult than it would have been at stage 3.

### Y

- `StateStore` is the principal interface and has exactly two production implementations as soon as it appears. It is tied directly to stage 3, not speculative flexibility.
- `TaskService` is not pass-through layering: it protects lifecycle invariants and became immediately valuable at stage 4, when one readiness rule covered both backends and both start paths.
- The single 668-line stage-4 file is a maintainability concern, but size alone is misleading here. Its internal class/function boundaries are coherent and behavior tracing is linear: CLI -> `TaskService` -> selected `StateStore`. Splitting those sections into modules would improve navigation without changing ownership.
- The loose complete-state `dict[str, Any]` model gives weaker compiler/type assistance than X’s dataclass and risks key-shape mistakes. SQLite rewrites all tables on each mutation, and one column contains JSON. Those are real technical compromises, though they are bounded by the product facts (one process, small team, small graphs) and transaction-tested.
- The parser/dispatch block is long, but it does not duplicate lifecycle rules. No abstraction in Y appears to exist solely for hypothetical flexibility.

**Accidental-complexity judgment:** X has better physical packaging and stronger typed records, but materially more behavioral duplication. Y’s large file is visually intimidating yet conceptually simpler; its main accidental complexity is representation looseness and coarse persistence, not duplicated product policy.

## Separate judgments requested

### 1. Fidelity to product facts

**Prefer Y, clearly, though neither is fully faithful at stage 4.** Y supports initially unassigned tasks; stable human IDs plus display names; persistent stable AI-agent IDs with provider/model owned by agents; durable success/failure execution history containing task ID, agent ID, outcome and output; runtime backend selection; retained JSON behavior; equivalent backends; small-graph prerequisite checks; and backward compatibility. Like X, it nevertheless lets a blocked task jump directly from `todo` to `done`.

X is faithful on local persistence, no-network fake execution, backend selection, small dependency graphs, cycle rejection, and the two explicit stage-4 guarded actions. Its central model conflicts with several explicit facts: assignee cannot be empty, a human has no stable ID separate from display text, AI configuration is stored per task, an execution is only one mutable text field with no outcome/agent identity/history, and a blocked task can be marked `done`.

### 2. Change locality and ownership

**Prefer Y conceptually, X physically.** X’s files are smaller and named by concern, but stages 3 and 4 expose that storage repositories own lifecycle policy: one product change must be made in both. Y keeps all source in one file, yet `TaskService` gives lifecycle changes one owner while only representation changes touch both adapters. The stage-4 diff is the strongest evidence: X duplicates the new graph and readiness methods; Y adds one readiness helper and only necessary schema serialization to each store.

### 3. Accidental complexity

**Prefer Y overall, with a qualification.** Y’s storage protocol and service earn their keep and no speculative framework is present. X’s package structure, dataclass, SQL prerequisite relation and executor protocol are good, but the paired repositories create repeated policy and private cross-module dependencies. Y should eventually split its coherent sections into modules and replace loose dictionaries with typed records, but those are localized refactors; removing X’s duplication requires moving ownership while preserving two mature implementations.

### 4. Likely ease of extending one more unknown requirement

**Prefer Y for an unknown product requirement.** Most plausible next requirements—new task lifecycle restrictions, assignment rules, execution behavior, or fields that must behave identically across storage—have one service owner and existing backend-parity tests. Stage 4 is direct evolutionary evidence that the stage-3 seam works.

There are cases where X would be easier: a requirement for library/package consumption benefits from its installable package and typed `Task`; mutable dependency editing is already present; backend-specific SQL behavior may fit its repository API. Conversely, a new Y field must be threaded through its logical dictionaries and both serializers, and the monolith is harder to navigate. Those counterexamples do not outweigh the risk that an unknown lifecycle rule in X must be implemented and kept identical in two repositories.

## Final judgment

### Strongest evidence favoring X

- The stage-4 dependency feature is richer: arbitrary existing tasks can be connected after creation, duplicate adds are harmless, and explicit DFS rejects direct and indirect cycles.
- Its immutable typed `Task`, installable package, focused `agents.py`, and repository-level unit API are easier to consume and inspect than Y’s untyped state dictionaries.
- SQLite prerequisites use a relational table with foreign keys, and JSON replacement is flushed/fsynced before atomic replace.
- Its inherited test suite exercises the complete repository behavior against both storage implementations, so the current duplication has meaningful regression protection.

### Strongest evidence favoring Y

- It models the operator’s product rather than only the short prompts: unassigned tasks, stable human/agent identity, agent-owned configuration, explicit success/failure execution records, and retained history.
- The stage-3 `StateStore`/`TaskService` separation has two concrete backends and pays off immediately at stage 4; readiness is enforced once for both storage choices and both guarded actions.
- Its parity tests compare outputs, logical state, error paths, and transaction atomicity, not merely similar method results.
- The large single file contains coherent internal boundaries; it does not duplicate product rules across repositories.

### Important counterevidence

- Y’s one-file layout, pervasive `dict[str, Any]`, and rewrite-the-whole-state persistence will become awkward if the product grows substantially beyond the stated scale.
- Y cannot add a prerequisite to an existing task or express a valid dependency on a later-created task. Its acyclicity comes partly from this restrictive API.
- X passes every supplied test and handles the explicitly guarded stage-4 paths and cycle creation; its behavioral duplication has not produced an observed backend mismatch in these snapshots. It does not enforce the separate “stays todo” fact.
- X’s executor protocol and typed domain record provide cleaner seams for certain implementation-focused changes than Y’s hard-coded local-fake behavior.

### Uncertainties

- Static review and supplied tests cannot establish crash durability under power loss, multi-process contention, large-state performance, or behavior with manually corrupted stores.
- There is no commit history, so preparatory intent is inferred from adjacent snapshot diffs.
- The unknown next requirement matters: package/API evolution favors some X traits, while almost any cross-backend product rule favors Y’s service ownership.
- The requirements do not explicitly say whether prerequisites must be editable after task creation, so Y’s restricted dependency workflow is a limitation but not a definite stage-4 failure.

### Preference

I would extend **Y**. Its product fidelity is much higher, and its evolution from stage 3 to stage 4 demonstrates the most valuable property for unknown change: product policy has one owner and storage parity is both structural and directly tested. I would first split the existing coherent sections into modules only when navigation warrants it, without changing the service/store boundary. X is polished and well tested, but its smaller files obscure a more consequential problem: the same product logic is owned by multiple repositories, while several explicit product facts never entered its model.
