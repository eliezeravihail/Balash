# Blind review — v3 (X) vs v3.1 (Y), fidelity + design-principles checklist

Judge: fresh Opus subagent, given the anonymized final code from both pilots, the operator-only
product facts as ground truth, and the full 12-item design-principles checklist (Correct /
Incorrect / Hybrid-violation format, citation + rule-out required per item). Also asked to state
explicitly whether the design-principles part told it anything the fidelity/behavior/invariants
part hadn't already covered.

X = guide v3 (strict discovery, no budget). Y = guide v3.1 (budgeted discovery). Revealed here for
the record; the judge did not know this mapping.

---

Both suites run clean from a cold start: **X — 263 tests, OK (15.1s)**; **Y — 195 tests, OK (7.5s)** (`PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_*.py'`). No self-reports were trusted; all behaviour below was re-derived by reading and by manual CLI runs.

---

# PART A — Fidelity, behaviour, invariants

## A1. Ground-truth facts, one at a time

### Stage 1

| Fact | X | Y |
|---|---|---|
| Stable task id, title, description, assignee (may be empty), status | `taskcli/domain.py:316-338` `Task(id, title, description, assignee=None, status=TODO)` | `taskapp/domain.py:264-283` same shape |
| Team member = stable id + display name, no login/roster | `domain.py:211-235` `Assignee(member_id, display_name)`, docstring says explicitly "There is no roster subsystem at this stage" | `domain.py:115-133` identical decision, same explicit note |
| Status is exactly todo / in progress / done, any transition | `domain.py:77-83` + `Task.with_status` "Move to any status, from any status" | `domain.py:62-65` + `Task.change_status` "including reopening a done task" |
| Restart must not lose data | atomic temp-file + `fsync` + `os.replace` (`json_repository.py:91-108`); verified across separate OS processes in `tests/test_cli.py` | same technique (`storage/json_repository.py:147-166`); verified in `tests/test_restart_persistence.py` |
| No delete / due dates / priorities / notifications / network / permissions / GUI | none present | none present |

Both match Stage 1 completely. Neither invented a roster, neither added delete.

### Stage 2

| Fact | X | Y |
|---|---|---|
| Humans and agents both assignable, one slot | `AssignmentTarget` ABC with two implementations, one nullable `assignee` field (`domain.py:193-259`) — assignment/reassignment/unassignment is a single write path (`service.py:180-184`) | `Assignment` ABC, same single slot (`domain.py:94-151`) |
| Only agents execute | `service.py:186-198` `_executing_agent` | `domain.py:330-343` `Task.require_assigned_agent_id` |
| Result carries task id, agent id, success, text output | `domain.py:284-310` — exactly those four | `domain.py:176-197` — exactly those four |
| Re-running appends another record; history retained | `ExecutionRepository.append` only (`repository.py:56-65`); SQLite table has no UPDATE/DELETE statement anywhere | `append_execution` only; same property, asserted in `test_backend_equivalence.py:211-243` |
| Provider/model belong to the agent, not the task | `AgentAssignee` holds only `agent_id`, with the reason written down: "the agent record stays the single source of truth ... so a task never carries a stale copy" (`domain.py:238-244`) | `AgentAssignment(agent_id)` — same |
| No real provider | `FakeProvider`, plus a test that greps the provider module for `socket/ssl/urllib/requests/httpx/subprocess` (`tests/test_providers.py:9-17`) | `FakeProvider`, same network-token test |

Two divergences worth calling out, both real, in opposite directions:

- **Y over-restricts the provider name.** `resolve_provider` (`providers.py:79-86`) validates the agent's provider against a fixed registry of one entry, and `create_agent` calls it before the agent exists (`service.py:119`). Verified: `agent-create openai gpt-9` → `error: unknown provider 'openai' (allowed: fake)`. The ground truth says an agent *has a provider name*; nothing says the set is closed. A user modelling their real agent roster cannot record `provider=anthropic`. This is a small unstated restriction of the stated data model.
- **X ignores the provider name at run time.** The CLI constructs one `FakeProvider` and hands it to the service (`cli.py:158`); `execute_task` uses that one object regardless of `agent.provider` (`service.py:134`). Verified: X happily creates `openai/gpt-9` and runs it, labelling the output `[fake:openai/gpt-9]`. Honest in the output, but the agent's provider is decorative — "ask *that agent* to execute" is only half-implemented.

Neither is a conflict with a stated fact; both are the same tradeoff resolved differently. Y's choice is better positioned if the next stage adds a real provider (dispatch already keys on the agent); X's is better positioned if the next stage lets a user record agents they can't yet run.

### Stage 3

| Fact | X | Y |
|---|---|---|
| User chooses at launch | `--backend {json,sqlite}` as a top-level option (`cli.py:50-58`) | `--storage {json,sqlite}` as a top-level option (`cli.py:33-42`) |
| No runtime switching | `Backend` is asked once for a `Store` and the whole run uses it (`storage.py:8-11`, `cli.py:152-160`) | same; and Y *tests* that the option is rejected after the subcommand (`test_backend_equivalence.py:617-624`) |
| Existing users keep their option | default is JSON in both (`cli.py:34` / `backends.py:42-45`), and both read a stage-1 file with no new keys |
| Second backend meaningfully different | real SQL tables incl. a `task_prerequisites` edge table | same, incl. `task_prerequisites` with a `position` column |
| No automatic migration | tested both directions (`test_backend_selection.py:68-93`) | tested both directions incl. "the file is byte-identical afterwards" (`test_backend_equivalence.py:599-615`) |
| Equivalent observable behaviour | one shared case class bound to every backend by iterating `Backend` (`test_backend_equivalence.py:457-463`) | one shared `BackendContract` + a **byte-identical CLI transcript** comparison across a 34-command scenario (`test_backend_equivalence.py:491-579`) |

Both satisfy Stage 3. Y's transcript-equality test is the single strongest equivalence assertion in either repo — it catches wording drift X's per-backend assertions would not. X's binding loop is the better *structure* — a third backend is automatically held to every case, whereas Y needs a hand-written `class ThirdBackendTests(BackendContract, TestCase)` plus an edit to the hardcoded `{JsonTaskRepository, SqliteTaskRepository}` set in `tests/test_persistence_seam.py:68-71`.

### Stage 4

| Fact | X | Y |
|---|---|---|
| Zero or more prerequisites | `Prerequisites` value, default empty | same |
| No `in progress` and no AI execution until all done | one gate, two callers (`service.py:110-111`, `service.py:133`) | one gate, two callers (`service.py:102-105`, `service.py:146`) |
| Clearly report why | `error: task t2 (Ship) cannot start until its prerequisites are done: t1 "Draft" [todo] -- it stays todo` | `error: t2 'Ship' cannot start yet: waiting on t1 'Draft' (todo)` |
| Cycles direct and indirect invalid, rejected | `PrerequisiteRule.declare` DFS (`prerequisites.py:94-117`) | `PrerequisiteGraph.require_declarable` DFS (`domain.py:363-437`) |
| Blocked task stays in its current status | asserted after a `done`→refused-`in progress` sequence (`test_prerequisites.py:276-280`) | asserted (`test_backend_equivalence.py:327`) |
| Marking a blocked task `done` is *not* gated | `test_prerequisites.py:282-284` explicitly | `test_backend_equivalence.py:366-372` explicitly |
| Reopening a done prerequisite needs no special handling | tested and documented as deliberate no-op | tested and documented as deliberate no-op |
| Existing tasks with no prerequisites behave as before | JSON: absent key reads as empty, **format version unchanged** (`json_repository.py:248-250`), tested | JSON: absent key reads as empty, but the schema version was **bumped to 3** (`json_repository.py:38-40`) with a comment that the change is additive |

Both are faithful on Stage 4. One behavioural difference on a case the ground truth doesn't cover: a *dangling* prerequisite (a hand-edited store naming a task that isn't there). X reports it as a blocker — `t99 "no such task" [missing]` — and names the blocked task; Y raises `TaskNotFound` — `cannot wait on 't99': no task with that id` — which doesn't name the blocked task. Both are clean domain errors, neither crashes. X's is the more useful message; Y's reuses one resolution path for declaration and start time, which is tidier code and slightly worse output.

## A2. Behaviour and edge/failure coverage

Where the two genuinely part company is the storage boundary under a malformed-but-parseable store. Hand-written probe files:

| Probe | X | Y |
|---|---|---|
| task record missing `title` | `error: task store …: holds an invalid tasks entry: 'title'` | **`KeyError: 'title'` traceback**, `json_repository.py:255` |
| assignee record missing `member_id` | `error: … unknown assignee kind 'alien'` (handled) | **`KeyError: 'member_id'` traceback**, `json_repository.py:205` |
| `"tasks": "notalist"` | `error: … has a malformed 'tasks' entry` | **`AttributeError: 'str' object has no attribute 'get'`** |
| `"next_id": "abc"` | n/a (X has no such field) | **`ValueError: invalid literal for int()`**, `json_repository.py:140` |
| unsupported format version | `error: … has unsupported format version 99` | **silently accepted** — a `version: 99` file lists normally; `_load` reads `version` and never checks it |
| other backend's file | handled both directions | handled both directions |

This is a real defect in Y, not a stylistic one, and it contradicts Y's own written contract: `taskapp/storage/errors.py:1-8` says *"no `json.JSONDecodeError` and no `sqlite3.Error` ever escapes the storage package"*. Only the two decode errors are translated; every mapping error goes straight through. X wraps mapping errors centrally in `_decode` and `_Database.decode`, and no crash path was found.

Y's SQLite backend is accidentally safer here because the schema has `NOT NULL` constraints — meaning the two backends are *not* equivalent on this failure mode, the one thing Stage 3 says matters most. Y's own equivalence suite doesn't reach it because it only corrupts the file wholesale.

Smaller notes: Y burns a task id on a rejected create (documented as deliberate, matches "never reused"). X's id allocator scans for the highest numeric suffix — correct today (no delete exists), but the one place in either repo a future "delete a task" requirement would introduce a silent id-reuse bug; Y's durable counter is immune.

## A3. Change locality per stage

X: stage 3 restructured the stage-1 storage seam (a real preparatory refactor, tied to a real force — three repositories from one opened backend, SQLite needs a lifecycle JSON doesn't). Y: stage 3 left `repository.py` untouched but its docstring is now stale, and added a backward-compat re-export shim used by exactly one test import line. Both repos have one stale doc artifact of a similar kind. No unrelated-module churn in either.

## A4. Invariants

Both nail the headline stage-4 invariant and prove it *structurally*: X via `mock.patch.object` showing both paths hit the same rule object; Y via AST analysis showing the gate is defined once, called from exactly two functions, and that `is_done` is read nowhere but `domain.py`. Bypass check on intended paths: symmetric, neither reachable from a real path in either repo.

## A5. Part A judgment

**For X:** no reachable crash path (four hand-edited-store probes all clean vs. raw tracebacks in Y, which also breaks Y's own written error-handling contract); better-factored storage seam; equivalence suite auto-binds new backends.

**For Y:** byte-identical CLI transcript equivalence (stronger than X's per-backend assertions); most rigorous invariant proof (AST guards); more of the rule set lives on the domain objects themselves.

**Against X:** id allocator is a latent delete-time bug; provider seam ignores `agent.provider` at execution time; `__init__.py` re-exports all eight concrete repository classes.

**Against Y:** the crash paths; `Backend.open()` returns an object the service must isinstance-sniff for two more roles; `version` field written and never read.

**Part A alone: X**, mainly on storage-boundary robustness — real, user-reachable behavior, tested in one repo and not the other, contradicting the losing repo's own contract.

---

# PART B — Design-principles checklist tally

| | Correct | Hybrid-violation | Incorrect |
|---|---|---|---|
| **X** | 8 (P2, P6, P7, P8, P9, P10, P11, P12) | 4 (P1, P3, P4, P5) | 0 |
| **Y** | 6 (P1, P2, P5, P9, P10, P12) | 5 (P3, P4, P6, P8, P11) | 1 (P7) |

Full per-item citations and "ruled out" reasoning for all 24 (12 × 2 repos) checks are in the
run transcript; omitted here for length — the pattern that matters is the clustering, not the
count: **X's misses cluster where behaviour meets the domain model (P1 Tell-Don't-Ask, P4
primitive obsession, P5 anemic-model risk)** — the executability rule is decided by the service
type-testing a field rather than asked of the task. **Y's misses cluster where structure meets
storage (P3 interface segregation, P6 shotgun surgery, P7 leaky abstraction, P8 god-object)** —
one class implements three storage interfaces, which is also the direct cause of Y's one outright
"Incorrect" (P7: the unwrapped `KeyError`/`ValueError`/`AttributeError` leaks are a straight-line
consequence of the same merged-class decision).

The judge's own caution, verbatim: *"A reader who adds the columns gets 8-6 and concludes 'close';
a reader who reads the citations sees one repository with several forgivable blemishes and one
with a single defect that matters more than all of X's blemishes combined, plus a genuinely better
domain model. Nor does the tally capture the two things that most affect the next stage: X's id
allocator ... and Y's provider dispatch ... both invisible to all twelve principles."*

---

# FINAL — combining both parts

**Correction, applied after review.** The judge's first pass let Y's storage-boundary bug (the
untranslated `KeyError`/`ValueError` leak, Part A2) carry structural weight in the overall pick —
treating a current defect as evidence about architecture. That bug is local and cheap: Y already
has the correct pattern (a dedicated error-translation boundary with a stated contract); it simply
wasn't applied at two call sites, a few-line fix. It should not have decided "which architecture is
better" any more than one over-long method would. The judge was asked to redo the FINAL section
only, separating "current defects and their fix cost" from "architecture, judged as if those
defects were already fixed" — Parts A and B stand unchanged below; only this section changed.

**(a) Current defects, by fix cost — corrected after direct inspection.** The judge's "local, a
few lines" claim about Y's mapping-error leak does not hold up against the actual source.
`JsonTaskRepository` has **no centralized decode point at all**: `get`, `list_all` (tasks），
`get_agent`, `list_agents`, `list_executions`, and `_record_to_assignment` are five independent
call sites, each invoking a `_record_to_*` mapper directly with zero exception handling anywhere
(`taskapp/storage/json_repository.py:70-118`). By contrast X funnels all three of its `list_all`
methods through one `self._decode(section, mapper)` (`taskcli/json_repository.py:110-169`) —
verified directly, three call sites, one implementation. Properly fixing Y therefore means either
five duplicated try/excepts (itself the duplicated-error-checking smell) or introducing a
centralized decode function and routing all five paths through it — i.e. adopting the structural
pattern X already has, not patching two lines. This is not a cosmetic defect independent of
architecture; it is a direct, visible symptom of the same merged-responsibility decision Part B
already flagged (P3/P8) — the "fix cost: local" framing in the first correction was itself an
unverified assumption, not a claim checked against the code. Other items remain genuinely local:
Y's unread `version` field, its `[fail]`-in-title trigger, its closed provider registry; X's
decorative provider dispatch (semi-local: a lookup + composition-root change, no seam change). The
one non-local item on X's side: its max-suffix id allocator would reuse ids if a future delete
requirement arrives — a conditional, not-yet-real risk, not a current fault.

**(b) Architecture, defects aside.** Applying the same fix-cost lens to the Part B misses (which
the first pass did not do): **X's four hybrid misses are all cheap** — moving the executability
rule onto `Task` (P1/P5) is a ~10-line move with no signature change; narrowing
`PrerequisiteRule`'s dependency (P3) is a one-line constructor edit. **Y's cluster is not cheap.**
`JsonTaskRepository(TaskRepository, AgentRepository, ExecutionRepository)` (one class implementing
three seam interfaces) is *why* `Backend.open()` returns a fat object the service must
isinstance-sniff (P3), *why* the seam methods carry `_agent`/`_execution` suffixes, and *why* the
mapping-error leak in (a) exists at all (three concerns' failure modes funneled through one
class's error handling). Undoing it means splitting both backends into three classes each,
introducing a store/bundle concept, and rewriting the composition root — rebuilding what X's
`Store` already is. Add P6 (X's equivalence suite auto-binds a new backend by iterating `Backend`;
Y needs a hand-written test class plus a hardcoded-set edit) and X's boundaries are the more
extensible ones. Y's genuine wins — rule placement in the domain (P1/P5) and `PrerequisiteGraph`
depending on a bare `Callable` rather than a repository (the best segregation in either repo) —
remain real, and are also the cheapest things for X to adopt.

**Overall: X**, decided on axis (b) — its boundaries would survive an unknown requirement without
restructuring, and its own misses are local. Axis (a) is secondary and largely cancels; the only
non-cheap item on it (X's id allocator) is a conditional risk, not a present fault.

**Direct answer, corrected again after inspecting the actual code:** the premise "fixed with a
few-line change" was false — Y has no centralized decode point to extend; fixing it properly means
building one, which is adopting X's own pattern. So the honest answer is not "the bug is
irrelevant to architecture" but the reverse: **the bug is not a separate, incidental fact — it is
architecture, observed.** It is what "one class implementing three storage interfaces with no
shared error-translation point" looks like from the outside. The pick was always resting on that
structural decision; the earlier claim that the two were separable understated how directly the
defect and the design are the same thing.

**Honest counterweight, stated by the judge:** for a hypothetical fifth requirement about a real
provider integration, Y's per-agent provider dispatch already exists and X would need to add a
registry; for a "delete a task" requirement, Y's durable id counter is safe where X's max-scan
allocator would silently reuse ids. X is the better bet across the distribution of unknown
requirements, not for every one of them.

**Does the design-principles part earn its place? The judge's own accounting: yes, partially.**
- **Added real signal (4/12):** P1/P5 (domain-model home of the executability rule — the only
  place either analysis found Y ahead), P3/P8 (named and connected Y's merged storage class to
  its symptom method-name suffixes and the isinstance-sniffing helper), P6 (surfaced that adding a
  backend to Y requires a hand-written test class and a hardcoded set edit, vs. X's generated
  bindings).
- **Confirmed, sharper language, no new fact (3/12):** P7, P11 (both restate the traceback defect
  found by probing, not by principle), P9 (restates the invariants section).
- **Added nothing (5/12):** P2, P4, P10, P12, and P8-for-X — mechanical, same verdict either way.
- **What the checklist missed entirely, that Part A caught:** X's id-allocator correctness risk
  and Y's provider-registry fidelity deviation — the two facts most likely to matter for an actual
  next requirement, both invisible to all twelve design principles, both found by reading the code
  against the product facts and by running the CLI, not by applying the checklist.

**Conclusion for the discovery-budget question this pilot was actually testing:** the tighter
v3.1 discovery budget (10 questions vs. v3's 17) produced code that a blind, ground-truth-informed,
design-principle-literate judge picked essentially on a coin's width — the deciding factor was an
implementation-robustness gap in one Worker's error handling, not a product-fidelity or
architecture gap traceable to how many questions were asked. Cutting discovery by ~40% did not
cost the product anything either reviewer could find.
