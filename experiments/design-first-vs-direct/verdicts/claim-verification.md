# Scrutiny of the blind judge — claim verification against source

The blind judge (verdict: **Y better designed, ~70–75% confidence**) makes concrete, checkable
claims. Per the charter, a verdict is not a result until its load-bearing claims are verified against
the actual code — the earlier pilots caught a judge asserting a false "one-line fix." Every claim
below was checked directly in the anonymized sources.

Key (private): X = direct-arm (plain session), Y = architect-clean (Balash, design-first).

| # | Judge claim | Direction | Verified in source? | Evidence |
|---|---|---|---|---|
| 1 | X's `TaskManager` is a multi-job hub (task+agent CRUD, cycle detection, readiness, execution, persistence, **display**) | against X | **YES** | `manager.py`: `_reaches` (DFS, l.39), `assignee_label` (l.109, display), `create_task`, `unmet_prerequisites`, `is_ready`, `execute` all on the one class |
| 2 | X's `Task` is a plain dataclass with public mutable fields (`task.status = …` possible) | against X | **YES** | `models.py` l.167 `@dataclass` (NOT frozen; contrast `Assignee`/`Agent` frozen at l.60/80), public `status`/`assignee`/`prerequisites` fields |
| 3 | X's domain owns its JSON serialization and the SQLite store reuses that dict shape (storage↔domain leak) | against X | **YES** | `models.py` `Task.to_dict/from_dict`; `sqlite_store.py` l.148 `json.dumps(task.assignee.to_dict())` into an `assignee_json` column |
| 4 | X built full transitive cycle-detection (`_reaches`/DFS) for a state that cannot occur | against X (Metz) | **YES** | `_reaches` exists (l.39) and X's own return note concedes the graph "is structurally a DAG and cycles can't arise through normal API use" |
| 5 | Y's `Task` is fully encapsulated — private fields, read-only properties, behavior-only mutation | for Y | **YES** | `domain/task.py`: `self._id…self._prerequisites`; `@property` accessors; mutation only via `assign_to`/`unassign`/`change_status` |
| 6 | Y reasoned cycles away and enforced a single existence-at-creation rule instead of building DFS | for Y (Metz) | **YES** | `domain/prerequisites.py` documents the argument and enforces only `require_all_known`; no graph traversal exists |
| 7 | Y rebuilds an execution service per call for `execute`/`history` (ceremony wart) | **against Y** | **YES** | `cli.py` l.226 `build_execution_service(data_dir, backend).execute(...)`, l.231 same for `.history(...)` |

## Reading

**All seven load-bearing claims verify — in both directions.** The judge's criticisms of Y (claim 7)
and of X (1–4) and its praise of Y (5–6) all check out against the source. This judge did not
confabulate a weakness or invent a strength, and its decisive Metz point (claim 4 vs 6) rests on a
real, verified asymmetry: X genuinely built machinery for an unreachable state; Y genuinely reasoned
it away. This is the opposite of the earlier pilot's false "one-line fix" claim — here the instrument
survived source verification.

## Oracle reconciliation

Checked whether any praise/penalty is actually contradicted by a ground-truth product fact (the
distinction a blind judge cannot make alone):

- **Y's three id value objects** (`MemberId`/`AgentId`/`TaskId`) — the judge called them "at the edge
  of paying off." The oracle says members and agents are *distinct persisted entities with their own
  ids*, and a task is assigned to one **or** the other. So distinguishing member-id from agent-id has
  a genuine product basis; if anything the oracle supports Y's typing slightly more than the judge
  credited. Not a reason to move the verdict toward X.
- **"Execution does not change status"** (both arms) — matches the oracle (a result is recorded, not a
  status transition). Neither arm was penalized for it. No contradiction.
- No claim the judge scored as "over-engineering" turns out to be a product-mandated behavior, and no
  claim it scored as "simple/clean" turns out to be a silent product guess. Oracle reconciliation does
  not overturn the verdict.

## What remains

Claim verification and oracle reconciliation both leave the verdict standing. The one open question is
**disposition dependence**: the judge weighted pure-OO-quality over proportion-to-problem and conceded
"weighted toward proportion, the two draw closer." A second reviewer with the opposite prior
(pro-simplicity / YAGNI) is being run to test whether the Y verdict is robust or an artifact of the
judge's philosophy. Result recorded in `FINDINGS.md`.
