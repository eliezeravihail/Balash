# Blind review — no oracle facts, final snapshots only

Judge: fresh Opus subagent, given only the anonymized final (post-stage-4) code for both
repositories, the four stage requirement texts, and an aggregate per-stage metrics table
(no per-stage trees, no ground-truth product-owner facts).

X = Guide condition. Y = Direct condition. (Revealed here for the record; the judge did not
know this mapping.)

---

# Blinded review: repo X vs repo Y

**Suites as run (from each repo root, `python3 -m unittest discover -s tests -v`):**

| | tests | time | result |
|---|---|---|---|
| X | 196 | 3.28 s | OK |
| Y | 152 | 0.56 s | OK |

Both green, no skips, no errors. Production LOC matches the supplied table exactly (X 1510 / Y 1048); test LOC is X 2020 / Y 1612.

**Module inventory**

- X: `domain.py` (246), `repository.py` (75, ABCs), `provider.py` (48), `service.py` (274), `json_repository.py` (223), `sqlite_repository.py` (333), `cli.py` (259).
- Y: `models.py` (131), `agents.py` (35), `service.py` (250), `storage.py` (317, both backends), `cli.py` (272).

---

## Behavior

### Stage 1 — create/assign/status/list/persist

**X** satisfies it. `TaskService.create_task/assign_task/set_status/list_tasks`, JSON file store with atomic temp-file + `os.replace` + `fsync`. Restart is tested for real: `tests/test_persistence.py::SeparateProcessTests` shells out to `python -m taskman` per command via `subprocess.run`, so no Python object survives between steps. `list` shows ID/STATUS/ASSIGNEE/TITLE and has a `--status` filter.

**Y** satisfies it. Same operations, same atomic-write technique in `JsonStorage.save`. Restart is tested by constructing a fresh `TaskService(JsonStorage(path))` (`tests/test_service.py::PersistenceTests`) — a simulated restart, never a separate OS process. Ids are a persisted monotonic `next_id`, and `test_ids_are_not_reused_after_restart` covers that.

Two concrete differences worth noting:

- **Ids.** Y hands out `1, 2, 3…`; X hands out `uuid4().hex[:8]`. At a CLI, `add-prerequisite 2 1` versus `depends 4caae9c8 --on af6ffe8f` is a real usability gap. More importantly, X never checks for collision — `create_task` builds a `Task` with a fresh id and calls `save`, which is an unconditional upsert. I forced the case: with a colliding id factory, the first task is silently destroyed and only `[('dup','second')]` remains. It is a 2⁻³² event, untested and unguarded.
- **Empty title.** X enforces it in `Task.__post_init__`, so *every* construction path including deserialisation is covered. Y enforces it only in `TaskService.create_task`; `Task(id=1, title="", …)` and `Task.from_dict({... "title": "" ...})` are both accepted.

### Stage 2 — AI agents

The requirement: *"An AI agent has a provider name and a model name… ask that agent to execute the task and store an execution result… simple testable local/fake implementation."*

**Y** takes the literal reading. `AiAgent` is a frozen value object of exactly `(provider, model)` stored on the task; `EchoAgentRunner` is the fake; `task.result: Optional[ExecutionResult]` is *an* execution result. `assign-agent 1 acme tiny-1`, `execute 1`. This is precisely what was asked and nothing more.

**X** builds an agent *registry*: `AiAgent(agent_id, provider, model, display_name)`, an `AgentRepository` seam, `agent create` / `agent list` CLI commands, `AgentAlreadyExists` / `AgentNotFound` / `InvalidAgent` errors, and an append-only `list[ExecutionRecord]` history rather than one result. None of that was requested. It buys genuine things (provider/model recorded once instead of per task; re-runs keep history; a place to hang future agent config) and costs an extra concept, an extra CLI namespace, an extra persistence seam and two adapter classes.

X's assignment modelling is better: one `assignee: Assignee | None` field carrying an `AssigneeKind`, so "human or AI, never both" is *structurally* impossible to violate. Y uses two parallel fields and enforces mutual exclusion procedurally in two setters (`assign_task` sets `agent = None`; `assign_agent` sets `assignee = None`). I loaded a record with both set:

```python
Task.from_dict({"id":1,...,"assignee":"alice","agent":{"provider":"acme","model":"tiny-1"}})
# -> assignee='alice' agent=AiAgent(provider='acme', model='tiny-1')
# describe_assignee(t) -> 'ai:acme/tiny-1'   (the human silently disappears)
```

Neither the invariant nor this case is tested in Y.

Failure handling differs: X catches any provider exception and records it as `ExecutionRecord(success=False, output="provider error: …")`; Y lets `AgentError` propagate and stores nothing (`test_agent_failure_leaves_no_result`). Both are defensible and both are tested.

### Stage 3 — pluggable storage

Both satisfy it. Both default to JSON, both add SQLite via stdlib `sqlite3`, both select at startup (`--storage {json,sqlite}`), both keep behaviour identical.

- X: new module `sqlite_repository.py` implementing the same two ABCs; `STORAGE_BACKENDS = {"json": JsonFileStore, "sqlite": SqliteStore}` in `cli.py`; `build_store()` is the one place a concrete class is named.
- Y: `SqliteStorage` added inside the existing `storage.py`; `BACKENDS`/`create_storage()`/`default_filename()` in the same module.

Y additionally honours `TASKMAN_STORAGE`/`TASKMAN_FILE` env vars with flag-overrides-env, tested. X honours `TASKMAN_DB` only.

X goes considerably further on the "same behaviour either way" promise — see Change locality below.

### Stage 4 — prerequisites

Both satisfy it, including the "existing tasks with no prerequisites behave as before" clause (X: `NoPrerequisitesRegressionTests`; Y: `test_a_task_without_prerequisites_behaves_as_before`, `test_show_of_a_task_without_prerequisites_is_unchanged`).

On *"clearly report why"*, Y is better. Compare the same scenario:

```
# Y
$ taskman show 2
Task 2: Build it
Status:      todo
Prerequisites:
  1: Write spec [todo]
Blocked:     waiting on task 1 (Write spec) is todo
$ taskman status 2 in-progress
error: task 2 cannot be moved to in progress: waiting on task 1 (Write spec) is todo

# X
$ taskman show <build>
waits for:   af6ffe8f
$ taskman status <build> "in progress"
error: task '4caae9c8' cannot start: prerequisite not done: 'af6ffe8f' (Write spec: todo)
```

X's *error* is equally informative, but X's `show` prints bare ids with no titles, no statuses and no blocked line — you have to attempt the transition to learn anything. Y surfaces it proactively, and `render_task_detail` reuses `service.blocked_reason()` so the wording is written once.

Both reject cycles at declaration time and both terminate on already-cyclic stored data. X's cycle handling is stronger in two respects: it accepts a *batch* (`depends T --on A B C`) and validates the whole batch against a graph that accumulates the ids accepted so far, so a cycle cannot be smuggled in across one call (`test_a_cycle_inside_one_batch_is_rejected`, `test_a_batch_is_all_or_nothing_when_one_entry_would_cycle`); and its `PrerequisiteCycle` carries the actual `path` (`assertEqual(ctx.exception.path, [a.id, c.id, b.id, a.id])`). Y accepts one prerequisite per call, so the batch question does not arise.

Y adds `remove-prerequisite` (service method + CLI command). No stage asked for it. It's a reasonable companion, but it is scope beyond the requirement.

### Failure / edge cases in tests

Well covered in **both**: unknown task, unknown status, empty title, empty assignee/provider/model, executing an unassigned task, executing a human-assigned task, corrupt data file, unknown storage backend, missing file reads as empty, atomic save leaves no temp files, self-cycle / direct cycle / indirect cycle, diamond is not a cycle, dangling prerequisite id blocks rather than crashes (X: `test_an_unresolvable_prerequisite_blocks_instead_of_crashing`; Y: `DanglingPrerequisiteTests`), "not assigned to an agent" is reported before "blocked" (both).

Covered by **X only**:
- Real cross-process restart (`subprocess`), for *both* backends.
- Cross-backend file confusion: pointing `--storage sqlite` at a JSON file and vice-versa errors out **and provably does not touch the bytes** (`assertEqual(path.read_bytes(), before)`). Y tests "gibberish file → error" but never that one real backend refuses the other's real file, nor that the file survives.
- Awkward text round-trip: `"Fix \"quoted\" 'stuff', 100% — עברית 😀"` and `"…DROP TABLE tasks;--"` through both backends.
- Update-in-place semantics: an update must not reorder or duplicate a task (`test_updating_a_task_replaces_it_in_place_and_keeps_its_position`) — a real SQLite hazard that X's `seq` column exists to prevent.
- A reopened prerequisite (`ReopenedPrerequisiteTests`, 3 tests): the dependent's status and history survive, starting again is blocked again, finishing again unblocks. Y has no test for reopening.
- Immutability of returned execution records.
- Structural tests that the enforcement point is singular (discussed below).

Covered by **Y only**:
- Old-format SQLite database (pre-prerequisites schema) opens and gains an empty `task_prerequisites` table — a genuine forward-compat test with a hand-built legacy DB (`test_sqlite_database_written_before_this_feature_still_opens`). X has the equivalent for JSON only (`test_a_stage_one_file_without_the_new_keys_still_reads`), not for SQLite.
- `list_tasks()` does not alias internal state.
- Two `Task`s do not share one prerequisite list (the classic mutable-default trap).
- Env-var backend selection and flag-overrides-env.

One test-suite defect in Y: `tests/test_prerequisites.py` does `from test_backends import BACKEND_NAMES, SameBehaviourAcrossBackendsTestCase`, a sibling import that only resolves when `discover -s tests` puts `tests/` on `sys.path`. `python3 -m unittest tests.test_prerequisites` fails with an import error; the equivalent works fine in X.

---

## Change locality

I only have the stage snapshots as metrics, not as trees, so I read the churn numbers together with what the code shape corroborates.

| stage | X files / +/− | Y files / +/− | X prod Δ | Y prod Δ |
|---|---|---|---|---|
| 1 | 18 / +1310 −0 | 10 / +779 −0 | — | — |
| 2 | 10 / +1044 −73 | 7 / +452 −16 | +476 | +169 |
| 3 | 8 / +1053 −84 | 7 / +640 −21 | +354 (+1 file) | +242 (+0 files) |
| 4 | 9 / +955 −105 | 7 / +873 −25 | +233 | +261 |

**Stage 2.** Y's change is narrow and additive: new `agents.py` (35 lines), two fields on `Task` plus their `to_dict`/`from_dict` handling, two service methods, two CLI subcommands. 16 lines deleted. X's is much broader: `Assignee` gained a `kind`, `domain.py` gained `AiAgent`/`ExecutionRecord`/`AssigneeKind` and four exception types, `repository.py` gained a second ABC plus `InMemoryAgentRepository`, `json_repository.py` gained agent serialisation *and* an `AgentView` adapter, `provider.py` appeared, `cli.py` gained a subcommand namespace. 73 lines deleted, i.e. existing stage-1 code was reshaped, not just extended. Both changes stayed inside modules whose responsibilities are related to the requirement — neither touched anything genuinely unrelated — but X's blast radius was roughly 2.7× larger for the same product ask, and a good part of that is the un-asked-for agent registry.

**Stage 3.** This is where X's stage-1 investment pays. X's `repository.py` seam (`TaskRepository` ABC) existed from stage 1; adding SQLite meant writing one new module and adding one entry to a dict in `cli.py`. Neither `domain.py` nor `service.py` needed to change for the feature (X has a test asserting exactly this: `test_domain_and_service_do_not_import_a_storage_format` checks the sources for `import json` / `import sqlite3`). Y's `Storage` base also pre-existed, and Y's change was similarly local — `storage.py` and `cli.py`. Neither repo needed a preparatory refactor. X added a file, Y added a class to an existing file; both are legitimate.

There is a coupling in Y's stage-3 approach: `SqliteStorage._task_to_row` and `_row_to_dict` translate to and from the *JSON-shaped dict* produced by `Task.to_dict()`. The SQLite backend is implemented parasitically on the model's serialisation vocabulary. Upside: the two backends physically cannot disagree about field semantics. Downside: `models.py` owns a persistence format, and the second backend inherits it rather than being independent. X keeps serialisation entirely inside each store, at the cost of duplicating the field mapping twice — kept honest only by test discipline (which X has, extensively).

**Stage 4.** Comparable. X: `Task.prerequisites` + `add_prerequisite`, `_dependency_path` + `add_prerequisites` + `_require_startable` in the service, both stores gained a prerequisites table/key, `depends` in the CLI. Y: `Task.prerequisites`, `add_prerequisite`/`remove_prerequisite`/`_require_unblocked`/`_blocked_reason`/`_reaches` + three public queries, `task_prerequisites` table, two CLI commands and a `show` rendering change. Neither touched unrelated modules.

**Speculative vs product-driven extension points.** X's `TaskRepository` was speculative at stage 1 and vindicated at stage 3. X's `AgentRepository` was introduced at stage 2 and has exactly one *shape* of use — a per-store `AgentView` adapter — plus an unused-in-production `InMemoryAgentRepository`. `SCHEMA_VERSION` + the `meta` table exist for a migration that does not exist. `SqliteTaskRepository` is a dead alias (grep: zero references). `schema_version()` is called only from a test. Y's `Storage` base was likewise speculative at stage 1 and vindicated at stage 3. Y's `open_service()` is dead — nothing imports it, it isn't in `__all__` — and it is the sole reason `service.py` imports `create_storage`, `default_filename` and `DEFAULT_BACKEND` from `storage`, i.e. Y's service layer names the concrete storage registry for no live reason. `blocking_prerequisites()` is public and used only by tests.

---

## Responsibility and ownership

**A clear owner for lifecycle rules.** Both: `TaskService`. X's is slightly purer — `domain.Task` has only dumb mutators (`assign_to`, `set_status`, `add_prerequisite`, `append_execution`) and an explicit comment that the eligibility rule lives in the service because the domain cannot fetch anything. Y's `models.Task` is a plain dataclass with no behaviour except serialisation. Both are coherent.

**Assignee-specific behaviour.** X separates it properly: `AssigneeKind` decides *only* whether a task is executable; everything else (status, listing, persistence) is kind-agnostic, and `test_status_logic_is_identical_for_an_agent_assigned_task` pins that. Provider/model deliberately live on the `AiAgent` record, not on the task, and `test_the_task_does_not_carry_provider_or_model` asserts it. Y separates it by giving the task two nullable fields; the AI-specific data (provider, model, result) lives on the task itself. Y's separation is thinner and, as shown above, its mutual-exclusion invariant is not structural.

**Persistence containment.** X: strictly contained. `service.py` imports `repository` (ABCs) and `provider` only; nothing above the seam names JSON or SQLite; the CLI is the only place a concrete class is chosen, and there is a test forbidding regression. Y: mostly contained, with the `open_service` leak noted above and the `to_dict`/`from_dict`-in-the-model coupling. Neither leaks storage choice into task logic in any way a user could observe.

**Stage 4: one coherent enforcement place.** Both do it — but X *proves* it and Y merely does it.

X, `service.py`:
```python
if status is Status.IN_PROGRESS:
    self._require_startable(task)      # entry path 1 of 2
...
self._require_startable(task)          # entry path 2 of 2 (execute_task)
```
and `SingleEnforcementPointTests` asserts five separate things:
1. both `set_status` and `execute_task` contain the literal `self._require_startable(` in their source;
2. `def _require_startable(` appears exactly once across every `.py` in the package;
3. the rule fragments `is not Status.DONE` and `PrerequisitesNotMet(` appear *nowhere* outside the guard's own source;
4. monkey-patching the guard to a no-op lets **both** paths through (if either carried a private copy, it would still refuse — and the test would fail);
5. monkey-patching it to always refuse blocks **both** paths even for a task with no prerequisites.

Points 4 and 5 are the interesting ones: they are runtime proofs of singularity, not string matching, and they would catch a future duplication.

Y, `service.py`, is structurally just as single-pointed — `_require_unblocked(task, action)` called from `set_status` and `execute_task`, with `_blocked_reason` shared with the public `blocked_reason()` that the CLI's `show` uses, so the *wording* is also written once. Arguably Y's factoring is the more useful one for a UI. But Y has no test that would fail if someone later inlined a second copy of the rule into `execute_task`.

---

## Invariants

| # | Invariant | X: enforced / tested / bypassable | Y: enforced / tested / bypassable |
|---|---|---|---|
| 1 | Non-empty title | `Task.__post_init__` — every construction incl. deserialisation / tested / no | `TaskService.create_task` only / tested at service level / **yes** — `Task(…, title="")` and `Task.from_dict` both accept it |
| 2 | Status ∈ {todo, in progress, done} | `Status` enum + `parse`, argparse `choices` / tested / no | `Status.parse` in `set_status` and `from_dict` / tested / direct `task.status = …` |
| 3 | Exactly one assignee, human **or** AI | structural (one field + `kind`) / tested / **no** | two fields, mutual exclusion in two setters / **untested** / **yes** — demonstrated above |
| 4 | Only agent-assigned tasks execute | `_require_executing_agent`, one call site / tested per-backend / no | inline check in `execute_task`, one call site / tested / no |
| 5 | A task's agent id names a real agent | `_require_agent` at assign and at execute / tested / hand-edited store degrades to `AgentNotFound` | n/a — Y has no registry, so no dangling-reference class of bug exists |
| 6 | Agent ids unique | `create_agent` checks first / tested / **yes** — `store.agents.save()` bypasses it, and X's own test uses that to rename an agent | n/a |
| 7 | Prerequisite graph acyclic | `add_prerequisites` only, batch-atomic / 7 tests + per-backend / hand-edit only; `_dependency_path` and `_require_startable` both degrade safely | `add_prerequisite` only / 4 tests / hand-edit or direct `task.prerequisites.append` (Y's own test does this); `_reaches` degrades safely |
| 8 | No `in progress` and no agent execution until all prerequisites `done` | `_require_startable`, both paths / behavioural **and structural** tests, per-backend, per-process / see below | `_require_unblocked`, both paths / behavioural tests, per-backend, CLI / see below |
| 9 | Ids unique / not reused | random 8-hex, **no check**; a collision silently overwrites (demonstrated) / untested | persisted `next_id` / tested on both backends / no |
| 10 | Data survives restart | tested with real `subprocess`, both backends | tested with a fresh in-process service object only |

**Invariant 8 bypass, in detail.** Both services hand out mutable `Task` objects. In Y, `get_task` returns the *live* object from `self._tasks`, and `_save()` writes that list wholesale, so a mutation persists:

```python
t = s.get_task(b.id); t.status = Status.IN_PROGRESS
s.assign_task(b.id, "alice")            # any later command triggers _save()
# after restart: Status.IN_PROGRESS, while blocked_reason() still says
# "waiting on task 1 (prereq) is todo"
```

The stored state ends up self-contradictory. In X the same sequence leaves the task in `TODO`, because every service call re-reads from the store and the stray mutation is simply discarded.

**But this is not a design win for X, and I want to be explicit about that.** X's protection is an artifact of the *store*, not of encapsulation. Running X against an in-memory `TaskRepository` — exactly what X's own tests use — the bypass works identically:

```python
s = TaskService(FakeRepository(), …)
s.get_task(b.id).status = Status.IN_PROGRESS
# -> Status.IN_PROGRESS, blocked task now "started"
```

Neither repo defends invariant 8 against direct mutation. X happens to be safe in its shipping configuration; Y is not.

**Concurrency, a further consequence of Y's snapshot design.** Because `TaskService.__init__` loads the whole list once and `_save()` writes that same snapshot, a second session's work is silently destroyed:

```
Y: session A starts → A creates "from A" → session B starts → B creates "from B"
   → A creates "second from A"
   final file: ['from A', 'second from A']        # "from B" is gone
X: same sequence
   final file: ['from A', 'from B', 'second from A']
```

X survives because `JsonFileStore.save` re-reads, merges the one task, and rewrites. Neither repo locks, so X can still lose a concurrent edit *to the same task*; but Y loses entire unrelated tasks. For a one-command-per-process CLI this never fires. It would fire immediately behind anything long-lived.

---

## Accidental complexity

**X.**

- `TaskRepository` (ABC) — 2 production implementations (`JsonFileStore`, `SqliteStore`) plus test doubles. **Earned at stage 3.**
- `Provider` (ABC) + `FakeProvider` — 1 production implementation, 5 test doubles. Justified directly by the stage-2 requirement ("simple testable local/fake implementation").
- `AgentRepository` (ABC) — 3 implementations, but two of them (`json_repository.AgentView`, `sqlite_repository.AgentView`) are ~14-line pure pass-throughs that exist *only* because `TaskRepository.get` and `AgentRepository.get` collide on one object. This is genuine pass-through layering: `service._agents.get(id)` → `AgentView.get` → `JsonFileStore.get_agent` → `self._read()[1].get(id)`. Three hops for a dict lookup, duplicated verbatim across two modules. Y's single `Storage` interface with distinct method names has no analogue.
- `InMemoryAgentRepository` — production code used only as a default the CLI never takes.
- `SqliteTaskRepository` — dead alias, zero references, created purely for symmetry with a name the tests do use.
- `schema_version()` + the `meta` table + `SCHEMA_VERSION = 1` in both stores — speculative groundwork for a migration that does not exist; cheap, and the docstring reasons about it honestly.
- `AssigneeKind.parse` tolerating `"ai-agent"`/`"ai_agent"` — only ever fed canonical values written by the stores.
- Read amplification, a direct consequence of the fine-grained repository seam: I instrumented `JsonFileStore._read` and one guarded status change on a task with 3 prerequisites costs **5 whole-file JSON parses** (1 for `_require`, 3 for the guard's per-prerequisite `get`, 1 for `save`'s read-modify-write). Y does 1 load and 1 write per process. Irrelevant at this scale; it is the price of the seam, and it is why X's suite runs 6× slower.

**Y.**

- `Storage` base + `JsonStorage`/`SqliteStorage` — 2 implementations. **Earned at stage 3.** Not an ABC (`raise NotImplementedError`), which is slightly weaker but adequate.
- `AgentRunner` + `EchoAgentRunner` — 1 production implementation, 2 test doubles. Same justification as X's `Provider`.
- `open_service()` — dead, and the cause of a concrete-storage import in the service layer.
- `blocking_prerequisites()` — public API used only by tests.
- `remove_prerequisite` (service + CLI) — unrequested scope.
- `Task.to_dict`/`from_dict` — not flexibility complexity, but a layering choice with a real cost (the model owns a persistence shape and the SQLite backend routes through it).

**Did earlier abstractions become useful later?** Yes in both, and symmetrically: each repo's stage-1 storage interface was the thing that made stage 3 a local change. X's stage-2 `Provider` and `AgentRepository` did *not* acquire a second production implementation at stages 3 or 4; `AgentRepository` acquired only its two mechanical adapters.

**Pass-through layering that obscures behaviour without protecting a product force:** X's duplicated `AgentView` is the clearest instance in either repo. Y has none of comparable weight.

---

## Final judgment

### Strongest evidence favoring X

1. **Stage 4 is not just implemented once, it is proven once.** `SingleEnforcementPointTests` includes two runtime proofs — neutralise the single guard and *both* start paths open; make it always refuse and *both* close, even for a task with no prerequisites. Plus a package-wide assertion that `def _require_startable(` appears exactly once and that `is not Status.DONE` / `PrerequisitesNotMet(` appear nowhere else. That is a test that will still be catching duplication in a year.
2. **Stage 3 equivalence is enforced structurally, not sampled.** `BackendCases` holds ~40 behavioural cases written once; a `TestCase` subclass is *generated* per entry in `taskman.cli.STORAGE_BACKENDS`, and `SuiteCoverageTests` fails if any selectable backend is not enrolled. On top of that, two full CLI *transcripts* (a general one and a prerequisite one, ~20 commands each including error cases) are captured per backend and compared string-for-string, so any divergence in ordering, formatting, exit code or error wording fails. A third backend would be enrolled automatically. Y's cross-backend tests hard-code `BACKEND_NAMES = ("json", "sqlite")`.
3. **Harder-edged persistence testing.** Real `subprocess` restarts for both backends; cross-backend file confusion errors out *and* provably leaves the bytes untouched; unicode/quote/`DROP TABLE` round-trips; explicit "an update must not reorder or duplicate the row" (a real SQLite hazard, which the `seq` column exists to prevent).
4. **Better assignment modelling.** One assignment concept with a `kind` makes "human or AI, never both" unrepresentable, and provider/model live on the agent record rather than being copied onto every task.
5. **Cleaner layering, with a test that enforces it** — `domain.py` and `service.py` provably never import a storage format.
6. **Better invariant coverage at the edges**: reopened prerequisites, batch-atomic cycle rejection, immutable execution records, defensive handling of already-cyclic stored data.

### Strongest evidence favoring Y

1. **Consistently smaller change per requirement**, at every stage, on both files-touched and lines-deleted (16/21/25 deleted vs 73/84/105). Stage 2 in particular: +452/−16 across 7 files versus +1044/−73 across 10, for the same product ask. Y solved each stage close to the size of the stage.
2. **It built what was asked and little else.** An AI agent really is just `(provider, model)`; "store an execution result" really is one result. X's agent registry, agent ids, display names, uniqueness rules, `agent create`/`agent list` commands and append-only history were all invented, and every one of them had to be carried through stages 3 and 4 — into the SQLite schema, into the equivalence suite, into the CLI surface.
3. **Better "clearly report why".** `show` proactively lists each prerequisite with its title and status and prints a `Blocked:` line, reusing `service.blocked_reason()` so the explanation is written once and appears in both the error and the display. X's `show` prints bare hex ids.
4. **Better ids.** A persisted monotonic counter, tested against restart, with no collision hazard. X's random 8-hex ids are both harder to type and — unguarded and untested — capable of silently destroying a task.
5. **Simpler storage interface with no adapter tax.** `load()`/`save()` on one object; no `AgentView`, no duplicated pass-through, and the two backends cannot drift on field semantics because they share `to_dict`/`from_dict`.
6. **Forward-compat test X lacks**: a hand-built pre-prerequisites SQLite database that opens and gains an empty `task_prerequisites` table.
7. **More conventional exit codes** (1 = error, 2 = usage). X returns 2 for domain errors, colliding with argparse's usage code, and 1 for a *recorded execution failure* — a tri-state that is documented and tested but odd.

### Important counterevidence

- **Against X:** the extra machinery is not free and some of it is inert — `SqliteTaskRepository` is dead, `InMemoryAgentRepository` is never used in production, `schema_version()` is test-only, the `meta` table serves a migration that doesn't exist, and the two `AgentView` classes are duplicated pass-through. X's much larger test suite partly measures its own larger surface: a good share of the 196 tests exist to cover the agent registry and history that nobody requested. And X's protection of invariant 8 against direct mutation is accidental — I reproduced the bypass under an in-memory repository.
- **Against Y:** three real defects, not stylistic ones. (a) The stage-2 mutual-exclusion invariant is violable and untested — `from_dict` loads a task with both a human and an agent and the human vanishes from the display. (b) `get_task` hands out live state that `_save()` will persist, so a blocked task can be moved to `in progress` and *stored* while `blocked_reason()` still reports it as blocked. (c) The load-once/save-whole-snapshot design silently destroys another session's tasks, which I demonstrated. Also `open_service` is dead code that drags the concrete storage registry into the service layer, and `tests/test_prerequisites.py` can only be run through `discover`.
- **On churn:** X's larger diffs at stages 2–4 are only partly "worse locality". A meaningful fraction is the equivalence and enforcement test infrastructure (`test_backend_equivalence.py` alone is 782 lines), which is investment rather than thrash. The 73/84/105 deleted lines are the more honest signal that X reworked existing code each stage, and Y did not.

### Uncertainties that cannot be settled from static review

- I have per-stage *metrics* but not per-stage *trees*, so "did this stage require a preparatory refactor?" is inferred from deletion counts plus the shape of the final code. I can say X reshaped existing code more at each stage; I cannot say whether any specific refactor preceded a feature or accompanied it.
- Whether X's agent registry and execution history are prescient or wasteful depends entirely on requirement 5. If it is "let an agent be reconfigured across all its tasks" or "audit what an agent did", X is already there and Y needs a data migration. If it is anything else, X carried the weight for nothing.
- Real durability under interruption. Both do temp-file+`fsync`+`replace` for JSON; neither fsyncs the directory. SQLite behaviour under `kill -9` mid-transaction is untested in both. I did not attempt fault injection.
- Performance at any realistic scale. X's read amplification (5 file parses for one guarded status change) and Y's whole-database rewrite on every save are both O(n)-per-operation; which degrades worse first is not answerable statically.
- Neither repo has a README, packaging, type-check config or lint config, so I cannot judge whether `from __future__ import annotations` and the type hints (present and consistent in both) actually pass a checker.

### Which I would rather extend with one more unknown requirement

**X**, with reservations — and the reason is narrow and specific: *the tests*, not the production code.

If the next requirement touches the storage layer or the start-eligibility rule (a third backend, task deletion with dependency cleanup, "a task may not be marked done until its prerequisites are done", "an agent may not execute a task that is already in progress"), X gives me two things Y does not. First, a generated-per-backend equivalence suite plus transcript comparison that automatically holds a new backend to the existing contract, and a `SuiteCoverageTests` that fails if I forget to enrol it. Second, an enforcement-point test that will *fail* if I add a second start path and forget to route it through the guard, or if I inline a copy of the rule — which is exactly the mistake this codebase is most likely to make next. Both of those turn a class of future regression into a test failure rather than a review question.

I would rather extend X's **tests**; I would rather have inherited Y's **production code**, which is roughly two-thirds the size, has no pass-through adapters, and solves each stated problem at the size of the problem. Y's `service.py` is easier to read end-to-end than X's `service.py` + `domain.py` + `repository.py` + `provider.py`.

Three things temper the recommendation. Y's three concrete defects (dual-assignee load, persisted invariant bypass via live `get_task` objects, lost-update on concurrent sessions) are each a contained fix — make `Task` a single tagged assignment, return copies or make `get_task` read-through, and re-read-merge on save — perhaps a day's work, after which Y's core is arguably the better base. X's excess, by contrast, is structural and already load-bearing across four stages: removing the agent registry now means a schema change, a CLI break and rewriting a large part of the equivalence suite. And on the one requirement where the two most directly disagree — *"clearly report why a blocked task cannot start"* — Y is simply better.

So: X for the safety net it has already built, and because the cost of its excess is sunk while the value of its tests is prospective. Not because its production code is better.
