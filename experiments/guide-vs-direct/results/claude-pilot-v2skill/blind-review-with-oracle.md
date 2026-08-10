# Blind review re-run — same X/Y code, oracle facts added as explicit ground truth

Judge: fresh Opus subagent, given the *same* anonymized final code as the first review, plus
the full operator-only product facts as ground truth, plus an explicit "Fidelity to product
facts" rubric section requiring the judge to distinguish a correct-but-unstated product
decision from genuine speculative scope.

This is a controlled before/after: identical code, identical judge model, only the review
input changed. The verdict flips from a split ("prefer Guide's tests, prefer Direct's
production code") to a decisive preference for Guide, once the judge can check fidelity to
the true (but unstated-in-the-four-paragraphs) product facts.

X = Guide condition. Y = Direct condition.

---

# Blind comparative review: repo X vs repo Y

**Test runs (executed by me, from each repo root):**
- X: `python3 -m unittest discover -s tests -v` → **196 tests, OK**, 3.13s
- Y: `python3 -m unittest discover -s tests -v` → **152 tests, OK**, 0.53s

Both are complete, runnable, and green. Neither has a README or any user-facing documentation — a shared gap.

**Shape at a glance**

| | X | Y |
|---|---|---|
| Production modules | `domain.py`, `repository.py`, `json_repository.py`, `sqlite_repository.py`, `provider.py`, `service.py`, `cli.py` (1173 LoC) | `models.py`, `storage.py`, `agents.py`, `service.py`, `cli.py` (748 LoC) |
| Test LoC | 2020 | 1512 |
| Task id | `uuid4().hex[:8]` | monotonic int + `next_id` in store |
| Assignee model | `Assignee(member_id, display_name, kind)` | `assignee: Optional[str]` (a bare name) |
| AI agent model | first-class `AiAgent` record in a store | `AiAgent(provider, model)` embedded on the task |
| Execution | append-only `list[ExecutionRecord]` | single `Optional[ExecutionResult]` |

---

## 1. Fidelity to product facts

I go fact by fact. "Correct product decision" below means: not stated in the four paragraphs, but matching a ground-truth fact — earned, not scope creep.

### Stage-1 facts

**"Team members can be represented by a stable ID plus a display name."**

- **X — matches.** `domain.Assignee` is exactly `member_id` + `display_name` (+ `kind`), with `display_name` defaulting to the id (`Assignee.__post_init__`). The CLI carries it through: `taskman assign <task> u-7 -n "Dana Levi"`, rendered `Dana Levi (u-7)`. Tests `test_assign_records_member_id_and_display_name` and `test_display_name_defaults_to_member_id` pin it. Note the four paragraphs only say "assign it to a team member" — X built id+name anyway, which is a **correct product decision**, not unrequested scope.
- **Y — fidelity defect.** `models.Task.assignee: Optional[str]` is a bare name; `service.assign_task(task_id, assignee: str)` stores `assignee.strip()`. There is no stable identity for a person anywhere in the system. This literally satisfies the paragraph and actively conflicts with the ground-truth fact. Consequences are real, not cosmetic: two team members named "dana" are the same assignee, and renaming a person orphans their history. Y's `test_assigns_task_to_team_member` asserts `assignee == "alice"` — the string *is* the model.

**"Login/authentication is not required."** Neither builds any. Both match.

**"Tasks need a stable ID, title, description, assignee (which may initially be empty), and status."**

- **X — matches.** `Task(id, title, description, assignee: Assignee | None = None, status=Status.TODO)`. Unassigned is representable and round-trips (`test_created_task_survives_a_fresh_store` asserts `assignee is None` after reload); `_assignee_text` renders `-`.
- **Y — matches.** `assignee=None, agent=None` by default; `describe_assignee` renders `-`; `test_list_shows_dash_for_unassigned_task`.

Both also support *clearing* an assignee (X: `unassign` command; Y: only by reassigning — there is no unassign in Y). Minor edge to X.

**"Deleting tasks, due dates, priorities, notifications, multi-user networking, permissions, GUI are not required."** Neither built any of these. Both clean — no scope creep here in either repo.

**"Normal application restart must not lose data."**

- **X — matches, and proves it hardest.** JSON writes go through a temp file + `os.fsync` + `os.replace` (`json_repository.JsonFileStore._write`). Crucially, `tests/test_persistence.py::SeparateProcessTests` and `test_backend_equivalence.py::test_data_written_by_one_process_is_read_by_a_later_process` shell out to `subprocess.run([sys.executable, "-m", "taskman", ...])` — a *real* OS-process restart, per backend.
- **Y — matches, tested slightly more weakly.** Same atomic temp-file + fsync + rename in `JsonStorage.save`; SQLite writes in one transaction. But Y's "restart" tests are always in-process (`self.make_service()` builds a new `TaskService`, or `main()` is called again). That is a good proxy — the service genuinely re-reads from disk — but it is not a process restart. No subprocess test exists in Y.

**"The owner does not have an opinion about architecture patterns or the concrete local persistence format."** Both chose JSON first, both hid it behind an interface. Neither over-reads this.

### Stage-2 facts

**"AI agents and humans are both things that can be assigned work, but only AI agents can execute through the application."**

- **X — matches, and models it as one concept.** There is a single `assign_task` path with an `AssigneeKind` discriminator; `AiAgent.as_assignee()` converts an agent into the same `Assignee` type. Execution is gated by `TaskService._require_executing_agent`, which rejects both unassigned and human-assigned tasks with distinct messages. `test_agent_is_assigned_through_the_same_assign_call_as_a_human` and `test_an_agent_task_can_be_reassigned_to_a_human_and_back` pin the "both are assignees" idea directly.
- **Y — matches behaviourally, models it as two concepts.** `assign_task` and `assign_agent` are separate methods writing two mutually-exclusive fields (`assign_task` sets `task.agent = None`; `assign_agent` sets `task.assignee = None`). Execution guarded by `if task.agent is None: raise ValidationError`. The mutual exclusion is maintained by hand in two places rather than by the type, but it is tested (`test_agent_replaces_a_human_assignee`, `test_human_replaces_an_agent`).

**"Provider/model configuration belongs to the AI agent, not to each task."**

- **X — matches, and it is the design's centrepiece.** `AiAgent(agent_id, provider, model, display_name)` lives in its own `AgentRepository`, created via `taskman agent create ag-1 -p fake -m tiny-1`. The task stores only `Assignee(member_id="ag-1", kind=AI_AGENT)`. `domain.Assignee`'s docstring says so explicitly, and `test_the_task_does_not_carry_provider_or_model` asserts `not hasattr(assignee, "provider")`. **The whole agent registry — agent ids, `agent create`/`agent list`, `AgentAlreadyExists` — is not in the stage-2 paragraph. It is a correct product decision driven by exactly this ground-truth fact, not speculative scope.**
- **Y — fidelity defect, direct conflict.** `Task.agent: Optional[AiAgent]` where `AiAgent = (provider, model)`. There is no agent identity and no agent record; provider/model is copied onto every task (`service.assign_agent` constructs `AiAgent(provider=..., model=...)` per task; SQLite stores them as `agent_provider`/`agent_model` columns *on the tasks table*). This is the fact the paragraphs did not state and Y did not discover. Practical cost: changing "acme/tiny-1" to "acme/tiny-2" means editing every task that used it, and there is no way to ask "what tasks does agent X hold" except by string-matching provider/model pairs.

**"An AI execution result only needs: task ID, agent ID, success/failure, and text output."**

- **X — exact match.** `domain.ExecutionRecord(task_id, agent_id, success: bool, output: str)` — the four named fields and nothing else, frozen. `.outcome` renders `"success"/"failure"`.
- **Y — fidelity defect on success/failure.** `models.ExecutionResult(provider, model, output)`. No task id, no agent id, and **no success/failure at all**. A failing runner cannot produce a result: `service.execute_task` calls `self._runner.run(...)` unguarded, so `AgentError` propagates, the CLI prints an error and exits 1, and **nothing is recorded**. Y's own test confirms this is intentional: `test_agent_failure_leaves_no_result` asserts `service.get_task(task.id).result is None`. So the product cannot answer "did the agent try and fail?" — the state after a failure is indistinguishable from never having run. X handles this deliberately: `execute_task` wraps the provider call in `try/except Exception` and converts a crash into `ProviderResult(success=False, output=f"provider error: {exc}")`, tested by `test_a_provider_that_raises_is_recorded_as_a_failure_not_a_crash` and `test_failed_execution_is_recorded_as_a_failure`.

**"Re-running an AI task may create another execution record; retaining execution history is acceptable."**

- **X — matches the stronger reading.** `Task.append_execution` is append-only ("Records are appended, never replaced"); `execution_history()` returns the list; `test_running_again_appends_a_second_record_and_keeps_the_first` and `test_history_mixes_failures_and_successes_in_order` pin ordering. SQLite persists it in an `executions` table keyed `(task_id, ordinal)`.
- **Y — permitted, but weaker.** `task.result = result` overwrites; `test_re_executing_replaces_the_previous_result` makes overwriting the specified behaviour. The fact says history is "acceptable", not mandatory, so I will not call this a defect — but combined with the missing success flag, Y's execution story retains strictly less than the ground truth says the result "needs".

**"No real provider authentication, billing, streaming, or network retry behavior is needed."** Both clean. X's `provider.py` docstring explicitly declines to build a provider registry; Y's `agents.py` is 35 lines. X even asserts it in a test (`test_execution_uses_no_network` greps `provider.py` for `import socket|http|urllib|requests`) — cute, and it does encode the constraint.

### Stage-3 facts

**"The user chooses storage when launching the CLI; runtime switching inside one process is not needed."**

- **X — matches, and tests the negative.** `--storage {json,sqlite}` chosen once in `cli.main`, `build_store` is the single construction site. `test_the_process_uses_one_store_object_for_the_whole_run` monkeypatches `build_store` with a spy and asserts it was called exactly once — a direct test that no runtime switching happens.
- **Y — matches.** `main` resolves `backend = args.storage or default_storage()` and constructs once. Also honours `TASKMAN_STORAGE`. No test of the "exactly once" property, but the code has one construction site.

**"Existing users should not lose the current storage option."** Both default to `json` with no flag (`DEFAULT_STORAGE = "json"` / `DEFAULT_BACKEND = "json"`), and both keep their stage-1/2 file layouts readable. Both match. X additionally tests it (`test_json_is_the_default_when_no_storage_option_is_given`, `test_the_default_and_an_explicit_json_choice_agree`), and tests that a stage-1 JSON file without the new keys still loads (`test_a_stage_one_file_without_the_new_keys_still_reads`). Y tests the equivalent for old records (`test_old_records_without_agent_fields_still_load`) and, nicely, for an old *SQLite* database missing the `task_prerequisites` table (`test_sqlite_database_written_before_this_feature_still_opens`) — X has the same `CREATE TABLE IF NOT EXISTS` resilience (I verified manually that an old X schema without `executions`/`prerequisites` loads fine) but no test for it.

**"The second backend should be meaningfully different from the first."** Both added real SQLite via stdlib `sqlite3`, normalized into tables. X's is more normalized (`tasks`, `executions`, `prerequisites`, `agents`, `meta`, with `seq` columns to preserve insertion order and per-row upsert). Y's is a full delete-and-reinsert of every task on every save. Both match the fact; X's is closer to what one would actually want from a relational backend.

**"Automatic migration between storage formats is not required."**

- **X — matches and enforces it explicitly.** `repository.StorageError` exists precisely so "this path was written by the other backend" is a plain user-facing error, not a guess. `NoAutomaticMigrationTests` asserts each backend refuses the other's file **and leaves the bytes untouched** (`self.assertEqual(path.read_bytes(), before)`), plus `test_the_flag_decides_the_format_not_the_file_name` (no sniffing).
- **Y — matches in behaviour.** I verified manually: `--storage sqlite --file tasks.json list` → `error: could not read task file ...: file is not a database`, exit 1, JSON file intact. Tested at the "corrupt file" level (`test_corrupt_data_file_reports_an_error_on_either_backend`) rather than as an explicit cross-format policy, and the "file is untouched" property is not asserted.

**"Equivalent observable task behavior across both backends is important."**

- **X — strongest single piece of engineering in either repo.** `tests/test_backend_equivalence.py` defines `BackendCases` (52 test methods) and *generates* a `TestCase` subclass per entry in `taskman.cli.STORAGE_BACKENDS`, so each case runs against both backends — that is 104 of X's 196 tests. On top of that, `CliTranscriptEquivalenceTests` runs two fixed multi-command scenarios through the CLI, captures **stdout + stderr + exit code for every command**, normalises the random ids, and asserts the two backends produce byte-identical transcripts. A formatting, ordering, error-message or exit-code divergence anywhere fails. `SuiteCoverageTests` then asserts every registered backend is enrolled and that the shared suite is not trivially small.
- **Y — good, materially smaller.** `ServiceBehaviourTests.exercise` runs one workload per backend and compares `to_dict()` records; `CliBehaviourTests` compares a 13-command CLI transcript (code/out/err) across backends; `PrerequisitesAcrossBackendsTests` adds a 12-step prerequisite transcript. That is real equivalence testing and it covers the important flows — but it is ~7 shared cases against X's 52, and it is hand-maintained rather than auto-enrolling.

### Stage-4 facts

**"Dependency graphs are expected to be small."** Both use naive traversal (X `_dependency_path` DFS over a graph built from `list_all()`; Y `_reaches` DFS over the in-memory list). Both appropriate. Neither over-engineered indexing. Both match.

**"Direct or indirect dependency cycles are invalid and should be rejected."**

- **X — matches, most thoroughly.** Rejected at *declaration* time in `service.add_prerequisites`; `PrerequisiteCycle` carries the actual path and the message prints it (`a -> c -> b -> a`). Because X accepts a batch (`depends T --on A B C`), it also makes the batch **all-or-nothing**: the running graph is updated with ids accepted so far, so a cycle hidden inside one batch is caught (`test_a_cycle_inside_one_batch_is_rejected`), and nothing is written if any entry fails (`test_a_batch_is_all_or_nothing_when_one_entry_would_cycle`). Self-dependency, 2-cycles, indirect cycles, a 12-link chain, and the diamond-is-not-a-cycle case are all tested.
- **Y — matches.** `add_prerequisite` rejects self-dependency and `self._reaches(prerequisite, task.id)`. Only one prerequisite per call so there is no batch atomicity problem. Self/direct/indirect/diamond all tested. The error message is arguably friendlier prose than X's, though it does not print the cycle path.

**"A blocked task stays in `todo`."**

- Both match: the guard runs *before* any mutation in both `set_status` implementations, so a refused start writes nothing. X: `test_status_change_to_in_progress_is_rejected_and_leaves_the_task_todo` plus the backend-level `test_a_stored_blocked_task_refuses_both_start_paths` ("a refused start must not be written"). Y: `test_blocked_task_cannot_be_moved_to_in_progress` asserts the status is still `TODO`.
- Both also allow a blocked task to be set directly to `done` (only `IN_PROGRESS` is gated). That is consistent with the literal requirement in both repos; neither is wrong, but neither surfaces it as a considered decision. X at least names it: `test_only_entering_in_progress_is_gated` ("The rule is about *starting*").

**"Changing a prerequisite back from `done` after a dependent has started does not need special handling."**

- **X — matches, and explicitly scopes it.** `ReopenedPrerequisiteTests` is docstringed "Out of scope: no auto re-blocking. In scope: no crash, no corruption" and verifies the dependent keeps its status and history, that starting *again* is blocked again by the same rule, and that re-finishing unblocks it. This is the right reading of the fact: don't special-case it, but don't corrupt either.
- **Y — matches by omission.** No re-blocking logic, no test of the scenario. Behaviourally identical; the deliberateness is undocumented.

**"The application should clearly report why a blocked task cannot start." (from the paragraph)**

This is the one requirement where **Y is clearly better**. Y's `show` proactively renders the dependency state and the block:

```
Prerequisites:
  1: Spec [todo]
Blocked:     waiting on task 1 (Spec) is todo
```

via `service.blocked_reason()` / `prerequisites_of()` and `cli.render_task_detail`. X's `show` prints only `waits for:   4fc2cb0a` — raw ids, no titles, no statuses, no blocked indicator. X reports beautifully *at the moment of refusal* (naming every blocker with title and status, identically from both paths), but you cannot inspect why a task is stuck without trying to start it. Y reports well in both places. `blocked_reason` is a query the four paragraphs did not ask for and the facts do not name — but it directly serves the stated "clearly report why", so I'd call it earned, not scope creep.

### Fidelity summary

| Fact | X | Y |
|---|---|---|
| Member = stable id + display name | ✅ correct product decision | ❌ **defect** (bare name string) |
| Task has id/title/desc/optional assignee/status | ✅ | ✅ |
| Restart preserves data | ✅ (subprocess-tested) | ✅ (in-process tested) |
| Humans + agents both assignable; only agents execute | ✅ (one assignment concept) | ✅ (two fields, hand-maintained) |
| Provider/model belongs to the agent, not the task | ✅ correct product decision (agent registry) | ❌ **defect** (per-task provider/model) |
| Result = task id, agent id, success/failure, output | ✅ exact | ❌ **defect** (no success/failure; failures unrecorded) |
| Re-run may append; history acceptable | ✅ append-only | ⚠️ overwrites (permitted, weaker) |
| Storage chosen at launch, no runtime switch | ✅ (tested negatively) | ✅ |
| Existing users keep current storage | ✅ | ✅ |
| Second backend meaningfully different | ✅ | ✅ |
| No automatic migration | ✅ explicit policy + no-touch assertion | ✅ behaviourally |
| Equivalent behaviour across backends | ✅ 52 shared cases × 2 + transcripts | ⚠️ ~7 shared cases + transcripts |
| Small graphs; cycles rejected | ✅ (+ batch atomicity) | ✅ |
| Blocked task stays in todo | ✅ | ✅ |
| Reopened prerequisite needs no handling | ✅ explicitly scoped | ✅ by omission |
| "Clearly report why blocked" | ⚠️ only on refusal; `show` prints bare ids | ✅ **better** — `show` explains proactively |

---

## 2. Behavior

**Do they satisfy the current (stage-4, cumulative) requirements?** Both yes, verified by manual CLI runs:

X:
```
$ taskman --db t.json depends 226c0d48 --on 4fc2cb0a
226c0d48 waits for 4fc2cb0a
$ taskman --db t.json status 226c0d48 "in progress"
error: task '226c0d48' cannot start: prerequisite not done: '4fc2cb0a' (Spec: todo)     [exit 2]
```
Y:
```
$ taskman --file t.json status 2 in-progress
error: task 2 cannot be moved to in progress: waiting on task 1 (Spec) is todo          [exit 1]
$ taskman --file t.json execute 2
error: task 2 cannot be executed: waiting on task 1 (Spec) is todo                      [exit 1]
```

**Edge/failure coverage — X's strengths:** provider raises → recorded failure not crash; provider returns failure → recorded; re-execution appends; unassigned vs human-assigned execution produce distinct messages; awkward text round-trips through both backends; update-in-place does not reorder or duplicate a task; dangling prerequisite id blocks instead of crashing; a cycle refused mid-batch writes nothing; each backend refuses the other's file without touching it; agent id uniqueness survives a restart; two backends produce byte-identical CLI transcripts.

**Edge/failure coverage — Y's strengths:** old-format JSON *and* old-format SQLite (missing table) both load; corrupt file on either backend; `TASKMAN_STORAGE` env var and flag-overrides-env; two `Task`s do not share one `prerequisites` list (a real mutable-default trap, explicitly tested); `list_tasks()` does not alias internal state; empty `result_output` round-trips through SQLite (a NULL-vs-`""` trap); dangling prerequisite blocks; removing a prerequisite unblocks and persists; `show` output for a task with no prerequisites is unchanged from before stage 4.

**Gaps in X:** no CLI test exercises `return 0 if record.success else 1` in `cli.run` (no test asserts a CLI exit code of 1 for a recorded failure — the default `FakeProvider` always succeeds and the CLI offers no way to inject another). `SqliteStore.schema_version()` is exercised by exactly one test and nothing else.

**Gaps in Y:** no true separate-process restart test. No test that a blocked task may be moved to `done`. No test asserting the JSON file is untouched when the wrong backend is pointed at it. And the failure-recording behaviour is not merely untested but unimplementable given the model.

---

## 3. Change locality

I have no git history in either repo, so this is inferred from module structure, docstrings and back-compat shims — which are unusually explicit in both.

### Stage 2 (AI agents)

**X:** `domain.py`, new `provider.py`, `repository.py` (added `AgentRepository` + `InMemoryAgentRepository`), `json_repository.py` (agent serialisation, `AgentView`), `service.py`, `cli.py`. Six touchpoints. All additive: the JSON format kept its stage-1 keys and only writes `agents`/`executions` when non-empty. No refactor was needed. One wart: `AgentView` is duplicated verbatim in `json_repository.py` and `sqlite_repository.py`.

**Y:** `models.py`, new `agents.py`, `service.py`, `cli.py`, `storage.py`. Four touchpoints, tighter than X's. Also purely additive, also no refactor.

### Stage 3 (second backend)

**X:** one new file (`sqlite_repository.py`) + `cli.py`. `domain.py` and `service.py` were not touched at all — and X *tests* that they cannot be. No preparatory refactor.

**Y:** `storage.py` + `cli.py`. `models.py` and `service.py` untouched, except `service.open_service` gained a `backend` parameter. Two touchpoints. No preparatory refactor.

Both are excellent here; Y is marginally tighter, X is marginally better isolated (enforced by test, not convention).

### Stage 4 (prerequisites)

**X:** `domain.py`, `service.py`, `json_repository.py`, `sqlite_repository.py`, `cli.py`. Five touchpoints — the price of X's per-backend serialisation.

**Y:** `models.py` (gets JSON for free), `storage.py`, `service.py`, `cli.py`. Four touchpoints.

Neither touched unrelated responsibilities in either stage. New extension points are tied to the product change in both — X's `PrerequisiteCycle.path` exists because it is printed; Y's `blocked_reason` exists because `show` prints it.

---

## 4. Responsibility and ownership

**Is there a clear owner of task lifecycle rules?** Yes in both, and in the same place: `TaskService`.

**Is assignee-specific behaviour separated where justified?**

- **X: yes, and the separation is principled.** The *general* fact lives in `Assignee`; the *specific* fact ("this one can execute") is one enum value plus `Assignee.is_ai_agent`; the agent's own configuration lives in `AiAgent` in its own repository. `AiAgent.as_assignee()` is the single bridge.
- **Y: partially.** The separation exists but is enforced by convention, not the type system: nothing prevents a `Task` with both `assignee` and `agent` set; `describe_assignee` silently resolves the ambiguity by preferring `agent`.

**Is persistence contained?**

- **X: yes, and provably.** `repository.py` is a 3-method ABC; `domain.py`/`service.py` are asserted by test to contain no storage import; the CLI is the only module naming a concrete store.
- **Y: mostly, with one leak.** Serialisation lives on the domain objects (`Task.to_dict`/`from_dict`), and `SqliteStorage._task_to_row` calls `task.to_dict()` and unpacks it into columns — the relational backend is defined in terms of the JSON-shaped dict. A second leak: `TaskService` eagerly loads and caches the whole task list; the storage interface is whole-collection rather than per-entity.

**At stage 4, is prerequisite eligibility enforced in one place?**

- **X: yes — and this is the most rigorously demonstrated claim in either repo.** `TaskService._require_startable` is the sole check, proven four ways including two runtime proofs (neutralise the guard → both paths open; make it always refuse → both paths close, even with no prerequisites).
- **Y: yes, less ceremoniously.** `TaskService._require_unblocked(task, action)` from both paths, sharing `_blocked_reason` with the public `blocked_reason()` query so the CLI's `show` and the refusal message cannot drift. The single-point property is asserted only implicitly.

---

## 5. Invariants

| # | Invariant | X | Y |
|---|---|---|---|
| 1 | A task may not enter `in progress` with an unfinished prerequisite | `_require_startable`, tested 6+ ways incl. mock proof. Bypass: `get_task` returns a detached copy, so a naive mutation does not persist. | `_require_unblocked`, well tested. Bypass wider: `get_task` returns the *live* internal object, so mutating it and later saving persists the smuggled state. |
| 2 | An AI agent may not execute a blocked task | Same guard from `execute_task`. Tested, incl. "records nothing". | Same guard from `execute_task`. Tested, incl. "the runner was never called". |
| 3 | A blocked task stays in `todo` | Guard precedes mutation; asserted at service and backend level. | Guard precedes mutation; asserted at service level. |
| 4 | The prerequisite graph is acyclic | Batch-atomic; direct/indirect/self/long-chain/mid-batch all tested. | Direct/indirect/self tested. |
| 5 | Only a task assigned to an AI agent can be executed | Distinguishes unassigned from human-assigned. Tested both ways, fires before the prerequisite check. | `if task.agent is None`. Tested both ways, fires before the prerequisite check. |
| 6 | Execution records are append-only history | `Task.append_execution`; frozen `ExecutionRecord`; order tested across restarts on both backends. | **Does not exist** — `task.result` is overwritten by design. |
| 7 | A task's assignee is exactly one of {nobody, human, agent} | Structural: one `assignee: Assignee \| None` field with a `kind`. Unrepresentable to be both. | By convention: two fields nulled by hand. Representable-but-invalid state exists. |
| 8 | Agent ids are unique | `AgentAlreadyExists`; tested across a restart on both backends. | N/A — no agent identity. |
| 9 | Task ids are unique and stable | `uuid4().hex[:8]`; no collision check. | `next_id` counter persisted; tested not to be reused after restart. |
| 10 | Data survives restart | Atomic temp+fsync+rename (JSON); per-op transaction (SQLite). Subprocess-tested. | Atomic temp+fsync+rename (JSON); single transaction (SQLite). In-process-tested. |

**On invariant 1, the bypass difference is concrete, not theoretical.** I reproduced both:

```python
# Y — the guard is bypassed and the bypass persists
s.add_prerequisite(b.id, a.id)
s.get_task(b.id).status = Status.IN_PROGRESS   # live internal object
s.assign_task(b.id, "alice")                   # any unrelated command saves it
TaskService(JsonStorage(d)).get_task(b.id).status
# -> Status.IN_PROGRESS      (and blocked_reason() still says it is blocked)
```
```python
# X — the same mutation does not persist
t = s.get_task(b.id); t.status = Status.IN_PROGRESS
s.assign_task(b.id, "alice")
TaskService(JsonFileStore(d)).get_task(b.id).status
# -> Status.TODO
```

Neither is reachable through the CLI. It matters for the "one more requirement" question: if a second front-end is written against `TaskService`, Y hands out mutable internal state and X does not. In fairness, X's containment is a *consequence* of re-reading from the store on every `get`, not an explicit defensive copy.

---

## 6. Accidental complexity

### Genuinely accidental (no current use, no ground-truth fact behind it)

**X:**
- `SqliteStore.schema_version()` and the `meta` table's `schema_version` row. The ground truth explicitly says migration is not required; there is no migration code. Small but genuinely speculative.
- `InMemoryAgentRepository`. Never used in any production path; a test convenience shipped as production code.
- `AgentView` duplicated identically in two storage modules.

**Y:**
- `service.open_service()` — defined and never called by anything, including tests. Dead code.
- An unreachable defensive branch in `default_filename` for a backend `create_storage` already rejects.

Both lists are short. Neither repo has a factory-factory, a plugin registry, an event system, a config layer, or an ORM.

### Earned complexity (looks like more than was asked; justified by a ground-truth fact)

**X — substantial, and correctly earned:** the whole `AiAgent` registry, `AssigneeKind` + `Assignee` with id and display name, `ExecutionRecord.success` and append-only history, `StorageError` and the cross-backend refusal policy, `Provider` ABC. Each is traceable to a specific ground-truth fact.

**Y — modest, and earned:** `blocked_reason()`/`blocking_prerequisites()`/`prerequisites_of()` and the `Blocked:` line in `show` — the most direct implementation of "clearly report why". `AgentRunner` ABC, same justification as X's `Provider`. `remove-prerequisite` — mild, defensible scope creep with no fact behind it, but cheap and useful given neither repo supports deleting tasks. `TASKMAN_STORAGE` env var — harmless, consistent with the pre-existing `TASKMAN_FILE`.

### Did earlier abstractions pay off later?

Both made the same bet at stage 1 (an interface with one implementation) and both were vindicated at stage 3, cheaply, in both.

---

## 7. Final judgment

### Strongest evidence favoring X

1. It matches three ground-truth facts that Y misses, and one of them is unrecoverable without a data migration: provider/model on the agent (not the task), member identity as id+name, and an execution result carrying success/failure. Y cannot answer "which tasks does agent X hold", cannot rename a person, and cannot record that an agent tried and failed.
2. The stage-4 single-enforcement-point evidence is exceptional — a runtime proof, not just a behavioural test.
3. Backend equivalence is systematically guaranteed (52 auto-enrolled shared cases + byte-identical transcripts), not sampled.
4. Storage isolation is enforced by test, not convention, and the no-migration policy is explicit including a byte-level "file untouched" assertion.
5. Real process-restart tests via `subprocess`.
6. Failure is a first-class recorded outcome, including a provider that raises being converted into a stored failure record rather than a crash.

### Strongest evidence favoring Y

1. It answers "clearly report why a blocked task cannot start" better — `show` proactively explains; X stays silent until you try to start the task.
2. Meaningfully smaller for the same behaviour (748 vs 1173 production lines), no loss of tested behaviour on what it does satisfy, ~6× faster suite.
3. Tighter change footprint at every stage — serialisation lives once on the model.
4. Sequential integer task ids are genuinely better ergonomics for a single-user CLI than X's 8-hex-char uuids.
5. A few sharp tests X lacks: old SQLite database missing a table still opening; two `Task`s not sharing one prerequisites list; `list_tasks()` not aliasing internal state; empty result round-tripping.
6. `remove-prerequisite` — X offers no way to undo a `depends` declaration.

### Important counterevidence

*Against X:* `show` is the weakest part of its stage-4 delivery. `AgentView` is copy-pasted between two modules. The "recorded failure → exit 1" CLI branch is untested because the CLI cannot inject a failing provider. Serialisation is duplicated per backend. Its stage-2 surface is more ceremony for the user than Y's — the ground-truth facts justify it, but a reviewer without those facts would reasonably call it heavier. `uuid` ids are user-hostile at the prompt.

*Against Y:* beyond the three fidelity defects, `get_task` returning live state means the prerequisite invariant is bypassable in-process. The `assignee`/`agent` mutual exclusion is a hand-maintained convention. A stale execution result continues to display on a task later reassigned to a human (reproduced). `open_service` is dead code. The default data file is `./tasks.json` relative to the *current directory*, so the same user gets a different task list depending on where they run the command — X's `~/.taskman/tasks.json` is the right default for "one person runs the CLI on one machine." Its cross-backend equivalence evidence, while real, is roughly an order of magnitude thinner than X's.

### Uncertainties that cannot be settled from static review

- No git history in either repo, so change-locality analysis is inference from module boundaries and back-compat shims.
- Whether either build process asked discovery questions — X's alignment with the ground-truth facts is exact enough that it either asked, or guessed remarkably well; the artifact does not distinguish those.
- Real-world durability under crash/concurrency was not fault-injected in either.

### Which I would rather extend with one more unknown requirement

**X**, though not unanimously.

The decisive consideration: the two repositories differ mainly in *what they modelled*, and modelling errors are the expensive kind to fix later. Y's three fidelity defects are all in the entity model, and each is a data migration plus a rewrite of the touching code — any requirement mentioning a person, an agent, or an execution outcome lands cleanly in X and requires inventing missing identity in Y.

X also gives the next contributor better safety rails: storage-agnosticism is asserted by test, backend equivalence is enforced automatically for whatever backends are registered, and the single-enforcement-point tests fail loudly if a third start path is added without routing through the guard.

The honest counterweight: if the next requirement is presentational or small-surface — better `list` output, filters, a "why is everything stuck" report — Y would be faster and pleasanter to work in. I would immediately steal two things from Y for X: the proactive `Blocked:`/prerequisite display in `show`, and `remove-prerequisite`.

But "smaller and pleasant" is recoverable by deleting code; "the wrong entities are persisted in two backends" is recoverable only by migration. On that asymmetry, X.
