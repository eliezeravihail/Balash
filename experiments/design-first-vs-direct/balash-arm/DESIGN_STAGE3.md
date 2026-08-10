# Stage 3 design — one storage boundary, two real backends (JSON default, SQLite)

This is a **design**, not an implementation. Signatures/schema use `...`/DDL sketches to fix the
shape a later objective builds against. No SQLite backend, DDL execution, queries, or CLI wiring
is written here; no commits.

It builds on stage 1 and stage 2 and treats their durable decisions (D-decisions, D1–D9) as
binding constraints. This is a **storage-only** change: the domain and service *logic* are
untouched — only how the service is *constructed* (which backend it is handed) changes. Places
that touch a durable decision are marked **[touches durable decision]**.

---

## 0. The one shape decision (the dominant uncertainty)

**What abstraction do the service/composition layers depend on, so they never know which backend
is live — per-entity repository ports, or an aggregate storage provider?**

**Decision: BOTH, at two different altitudes, because they answer two different questions.**

- **Four per-entity repository *Ports*** (`TaskRepository`, `MemberRepository`,
  `AgentRepository`, `ResultRepository`) — narrow structural interfaces the *services* depend on.
  Each service keeps its exact current constructor and depends only on the ports it actually
  calls (principle 3). This is where "the service never knows which backend is live" lives.
- **One aggregate `StorageBackend` provider** that *vends* the four repositories — the thing the
  *composition root* selects and holds. This is where "select JSON or SQLite at startup, once"
  lives, and where a backend's shared, backend-wide resources are owned.

Why the aggregate earns its place and is not a costume over the ports (principles 2, 8, 10): the
two backends **differ in whether the four repositories share resources**, and that difference has
to be owned *somewhere*:

- **JSON** — each repository owns one independent file (`tasks.json`, `members.json`,
  `agents.json`, `results.json`). Nothing is shared; there is no cross-repo state, no
  initialization step. Its `StorageBackend` is a trivial factory over a `data_dir`.
- **SQLite** — all four repositories live in **one database file** and should share **one
  connection** and **one schema-initialization (DDL) step**. If the composition root built four
  SQLite repos independently, "which db file, is the schema created yet, whose connection" would
  be duplicated four ways — exactly the scattered-ownership smell (principle 8). The aggregate
  owns "open the db once, ensure the schema once, vend four repos over the shared connection."

So the aggregate is a genuine two-implementation abstraction: its second implementation differs
*mechanically* from the first (shared connection + DDL vs. independent files), not cosmetically.
It is not `ICat.meow()`.

**Net:** services depend on narrow per-entity ports (unchanged constructors); the composition
root depends on one `StorageBackend`; selecting a backend is choosing which `StorageBackend` to
build; the choice never travels past the root.

---

## 1. The storage contract — ports the service and root depend on

### 1a. The exact consumer touchpoints (what the contract must cover — and nothing more)

Enumerated from the two real consumers, so the contract covers what is *used* and forces no
consumer to depend on a method it never calls (principle 3):

| Port | Methods actually called | Called by |
|---|---|---|
| `TaskRepository` | `add`, `save`, `get`, `all` | `TaskService` (add/save/get/all), `ExecutionService` (get) |
| `MemberRepository` | `add`, `team` | `TaskService` |
| `AgentRepository` | `add`, `registry` | `TaskService` (add/registry), `ExecutionService` (registry) |
| `ResultRepository` | `append`, `for_task` | `ExecutionService` |

Every method on every port has a real caller. There is no fat interface to segregate — the
per-entity split *is* the segregation. `MemberRepository` and `ResultRepository` are each used by
exactly one service; bundling all four into one "storage" god-interface would force
`ExecutionService` to depend on `members`/member-shaped methods it never calls, so the ports stay
four (principles 3, 8).

### 1b. The port signatures (structural `Protocol`s)

The ports are defined as `typing.Protocol` — structural, so the existing concrete classes satisfy
them **without inheriting anything** and no import cycle is created (the ports live in `storage`,
implementations live under it). Domain terms only; no path/row/table type appears in any
signature (principle 7).

```python
# storage/ports.py  — the contract; NO backend detail leaks through these signatures
from typing import List, Protocol
from ..domain import (
    Agent, AgentRegistry, ExecutionResult, Member, Task, TaskId, Team,
)

class TaskRepository(Protocol):
    def add(self, task: Task) -> None: ...
    def save(self, task: Task) -> None: ...           # existing task; raises TaskNotFoundError if absent
    def get(self, task_id: TaskId) -> Task: ...        # raises TaskNotFoundError if absent
    def all(self) -> List[Task]: ...

class MemberRepository(Protocol):
    def add(self, member: Member) -> None: ...         # upsert by id (idempotent name update)
    def team(self) -> Team: ...                        # vends the Team authority

class AgentRepository(Protocol):
    def add(self, agent: Agent) -> None: ...           # upsert by id (idempotent re-registration)
    def registry(self) -> AgentRegistry: ...           # vends the AgentRegistry authority

class ResultRepository(Protocol):
    def append(self, result: ExecutionResult) -> None: ...       # append-only; never overwrites
    def for_task(self, task_id: TaskId) -> List[ExecutionResult]: ...  # chronological order

class StorageBackend(Protocol):
    """One selected backend; vends the four repositories that share its resources."""
    def tasks(self) -> TaskRepository: ...
    def members(self) -> MemberRepository: ...
    def agents(self) -> AgentRepository: ...
    def results(self) -> ResultRepository: ...
```

The signatures are byte-identical to the methods the concrete JSON classes already expose — that
is deliberate: the JSON code becomes an implementation of a contract carved to fit it, and the 53
tests that drive those methods are unaffected.

**Is the per-entity port a genuine interface (principle 2)?** Yes, now — this is the concrete
second-implementation the abstraction was waited for. `TaskRepository.get(id)`: JSON linearly
scans a list of dicts read from a whole file; SQLite runs `SELECT ... WHERE id=?` against an
indexed table. `save`: JSON rewrites the whole file after finding the row; SQLite runs one
`UPDATE ... WHERE id=?`. Same behavior, entirely different mechanism — the `make_sound()` shape,
not a costume. A caller holding only `TaskRepository` genuinely cannot tell which is live.

### 1c. Which existing concrete classes become implementations (the renaming)

The four current concrete repositories become the **JSON implementation** of the contract, moved
under a `json/` subpackage and renamed so the class name states the backend it is (principle 11):

| Today | Becomes |
|---|---|
| `storage/task_repository.py :: TaskRepository` | `storage/json/task_repository.py :: JsonTaskRepository` |
| `storage/member_repository.py :: MemberRepository` | `storage/json/member_repository.py :: JsonMemberRepository` |
| `storage/agent_repository.py :: AgentRepository` | `storage/json/agent_repository.py :: JsonAgentRepository` |
| `storage/result_repository.py :: ResultRepository` | `storage/json/result_repository.py :: JsonResultRepository` |
| *(new)* | `storage/json/backend.py :: JsonStorage` (the aggregate) |

The **class bodies are unchanged** — only the names, file locations, and the addition of the
`JsonStorage` aggregate that constructs them from a `data_dir`. `storage/_jsonfile.py` stays
exactly as-is (shared JSON plumbing, still not an abstraction over storage). The name
`TaskRepository` is now the *Protocol*; consumers that imported `TaskRepository` as a type hint
still see the (now abstract) name and keep working.

---

## 2. Where the contract and the two implementations live

```
taskcli/
  domain/                     # UNCHANGED — knows nothing of storage. [touches durable decision]
  storage/
    __init__.py               # re-exports the ports + both backends' aggregate
    ports.py                  # the contract (§1b): four repo Ports + StorageBackend
    _jsonfile.py              # UNCHANGED shared JSON plumbing
    json/
      backend.py              # JsonStorage(data_dir): vends the four Json* repos
      task_repository.py      # JsonTaskRepository  (moved, body unchanged)
      member_repository.py    # JsonMemberRepository
      agent_repository.py     # JsonAgentRepository
      result_repository.py    # JsonResultRepository
    sqlite/
      backend.py              # SqliteStorage(db_path): opens/init db once, vends four repos
      schema.py               # the DDL (§3) — the ONLY place SQLite's table/column shape lives
      task_repository.py      # SqliteTaskRepository over the shared connection
      member_repository.py    # SqliteMemberRepository
      agent_repository.py     # SqliteAgentRepository
      result_repository.py    # SqliteResultRepository
```

- The **domain stays storage-free**; the **service talks only to the ports** (its constructors
  already take the port-typed collaborators). Neither imports a concrete backend.
- **What each implementation owns, sealed inside it:** the JSON side owns the four files, the
  row⇄domain dict mapping (`_to_row`/`_from_row`), and the stage-1 bare-string back-compat. The
  SQLite side owns the db file, the schema/DDL, the row⇄domain mapping (SQL params ⇄ domain
  objects), and the shared connection. **No table name, column name, SQL string, file name, or
  path crosses either aggregate's boundary** — callers receive domain objects and domain errors
  only (principle 7). The mapping is as sealed inside `SqliteTaskRepository` as it already is
  inside `JsonTaskRepository`.

---

## 3. The SQLite schema shape (real tables/rows, not JSON-in-a-column)

`sqlite3` from the **stdlib** — no ORM, no third-party dependency (honors "dependency-light").
Four tables, one per entity. Values stored as native columns; the domain's constructors remain
the single construction funnel (`_from_row` calls `Task(...)`, `Agent(...)`, etc., exactly as the
JSON repos do).

```sql
-- tasks: one row per task. The tagged assignee {kind, id} maps to TWO nullable columns,
-- not a JSON blob — this is the real-columns requirement.
CREATE TABLE tasks (
    id            TEXT PRIMARY KEY,
    title         TEXT NOT NULL,
    description   TEXT NOT NULL,
    status        TEXT NOT NULL,          -- Status.value token: 'todo' | 'in_progress' | 'done'
    assignee_kind TEXT,                   -- 'member' | 'agent' | NULL (unassigned)
    assignee_id   TEXT,                   -- underlying MemberId/AgentId value, or NULL
    CHECK ((assignee_kind IS NULL) = (assignee_id IS NULL)),
    CHECK (assignee_kind IN ('member','agent') OR assignee_kind IS NULL)
);

CREATE TABLE members (
    id           TEXT PRIMARY KEY,
    display_name TEXT NOT NULL
);

CREATE TABLE agents (
    id           TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    provider     TEXT NOT NULL,
    model        TEXT NOT NULL
);

-- results: append-only history. A surrogate autoincrement key preserves insertion order,
-- which is chronological — the relational equivalent of JSON's append position in a list.
CREATE TABLE results (
    seq       INTEGER PRIMARY KEY AUTOINCREMENT,  -- internal ordering key; never surfaced
    task_id   TEXT    NOT NULL,
    agent_id  TEXT    NOT NULL,
    succeeded INTEGER NOT NULL,                    -- 0/1; SQLite has no native bool
    output    TEXT    NOT NULL
);
CREATE INDEX ix_results_task ON results(task_id);
```

**How the design requirements map:**

- **Tagged assignee `{kind, id}` → two columns** (`assignee_kind`, `assignee_id`). Both NULL =
  unassigned; the paired `CHECK` makes "half-assigned" unrepresentable. `_from_row` reconstructs
  `AssigneeRef(kind=AssigneeKind(kind), id_value=id)` (or `None`), matching the JSON tagged form
  exactly, so the service's read path is identical across backends.
- **Append-only history preserving chronological order → `results` rows + `seq`.** Each execute
  is one `INSERT`; the code issues **no `UPDATE`/`DELETE`** against `results`. `for_task` =
  `SELECT ... WHERE task_id = ? ORDER BY seq ASC`. JSON preserves order *implicitly* by list
  position; SQLite preserves it *explicitly* via the monotonic surrogate key — a place the two
  mechanisms legitimately differ (§7) unified only at the behavior "returns oldest-first."
- **`succeeded` bool → INTEGER 0/1**, converted back to Python `bool` in `_from_row`. A place the
  SQLite mapping does real work JSON does not (JSON stores a native bool); sealed inside the repo.
- **"Upsert by id" (members, agents) → `INSERT ... ON CONFLICT(id) DO UPDATE SET ...`.** This is
  the relational form of the existing JSON `add` (scan-for-id, replace-else-append), and it is
  idempotent in the same observable way — re-adding an id updates the name and leaves one row.
- **"Save an existing task" → `UPDATE tasks SET ... WHERE id = ?`;** if `rowcount == 0`, raise
  **`TaskNotFoundError`** — mirroring the JSON `save`'s "no such row" raise byte-for-byte in the
  observable error. `add` → `INSERT`.
- **No `ExecutionResultId` leaks.** `seq` is a private ordering device; `ExecutionResult` still
  has no id (stage-2 D-decision preserved), and `seq` never appears in any port signature or
  domain object.

**Deliberately NO foreign keys** (a load-bearing decision, §7 and §5): `tasks.assignee_id` does
*not* reference `members`/`agents`, and `results.task_id`/`agent_id` reference nothing. The domain
*requires* dangling references to be tolerated — a task assigned to a later-removed agent must
still load and render `"<id> (unknown agent)"`; a result for any task must persist regardless.
An FK constraint would make SQLite *reject* what JSON *tolerates*, breaking behavior-identity.
The referential-integrity "leak" is exactly a place the two backends must NOT be forced to differ,
so SQLite is deliberately kept as permissive as JSON here.

---

## 4. Startup selection and the composition root

**[touches durable decision: the CLI is the composition root; it chooses concrete wiring.]**

### 4a. The selection spelling

One new option on the existing parser, plus reuse of the existing `--data-dir`:

```
--backend {json,sqlite}      # default: json
```

- **JSON (default):** unchanged — the four `*.json` files in `data_dir`. When nothing is passed,
  behavior is byte-for-byte today's.
- **SQLite:** one database file at `data_dir / "taskcli.db"` (location derived from the same
  `--data-dir`, so a user picks a directory once). No new path option is needed.

### 4b. The one wiring branch (the only place a backend name is interpreted)

```python
# cli.py (composition root)
def build_backend(kind: str, data_dir: Path) -> StorageBackend:
    if kind == "sqlite":
        return SqliteStorage(data_dir / "taskcli.db")   # opens + ensures schema once
    return JsonStorage(data_dir)                          # DEFAULT
```

`build_service` / `build_execution_service` are re-pointed to take an **optional backend**,
defaulting to a JSON backend built from `data_dir` — which **preserves their current signatures**
so all 53 tests that call `build_service(Path(...))` / `build_execution_service(data_dir)` keep
passing verbatim:

```python
def build_service(data_dir: Path, backend: Optional[StorageBackend] = None) -> TaskService:
    backend = backend or JsonStorage(data_dir)          # default path == today's behavior
    return TaskService(tasks=backend.tasks(),
                       members=backend.members(),
                       agents=backend.agents())

def build_execution_service(data_dir: Path, backend: Optional[StorageBackend] = None) -> ExecutionService:
    backend = backend or JsonStorage(data_dir)
    return ExecutionService(tasks=backend.tasks(), agents=backend.agents(),
                            results=backend.results(), provider=LocalProvider())
```

`main` builds **one** backend for the process and threads it into both builders (so SQLite's
single connection/schema-init is shared, not repeated):

```python
def main(argv=None, out=None) -> int:
    args = _build_parser().parse_args(argv)
    data_dir = _resolve_data_dir(args.data_dir)
    backend = build_backend(args.backend, data_dir)      # the ONE selection point
    service = build_service(data_dir, backend)
    # execute/history: build_execution_service(data_dir, backend)  — same backend instance
    ...
```

### 4c. Why the choice cannot leak past composition

`args.backend` is read **only** inside `build_backend`; from there on, everything downstream holds
a `StorageBackend` or a port, never the string `"json"/"sqlite"`. `TaskService`,
`ExecutionService`, and the entire `domain/` package have no parameter, import, or branch keyed on
the backend. There is exactly one `if kind == "sqlite"` in the whole program. The domain and
service literally cannot ask which backend they are on — there is no method that would tell them.

---

## 5. How "identical behavior" is structurally ensured AND proven

### 5a. Structural guarantee (identity is a property of the shape)

- Both backends implement the **same four ports** with the **same signatures** and raise the
  **same domain errors** (`TaskNotFoundError`, `UnknownAgentError`, …) for the same situations —
  the errors live in `domain/errors.py` and are the *only* failure vocabulary either backend
  emits. A caller cannot distinguish backends by their failures (principle 7).
- Both feed the **same domain constructors** in `_from_row` (`Task(...)`, `Agent(...)`,
  `ExecutionResult(...)`), so every reconstituted object has already passed the domain's
  invariants — neither backend can produce a "valid row" the domain would reject.
- The service holds ports, so it runs **one code path** over either backend; there is no
  backend-conditional logic to drift.

### 5b. The proof — one backend-agnostic conformance suite, run twice

A single abstract contract suite written purely against `StorageBackend`/the ports, with one
factory hook, subclassed once per backend. Any behavioral divergence fails one subclass — that is
the mechanical proof of identity.

```python
# tests/test_storage_contract.py
class StorageContractTests:                      # abstract; no TestCase base
    def make_backend(self) -> StorageBackend: ...  # overridden per backend

    # --- tasks ---
    #  add→get returns an equal task; get(unknown) raises TaskNotFoundError
    #  save(existing) persists changes, reflected by a fresh get
    #  save(absent) raises TaskNotFoundError
    #  all() returns everything added
    #  assignee round-trips for ALL THREE forms: None, AssigneeRef.member(...), AssigneeRef.agent(...)
    # --- members ---
    #  add→team().knows / .member / .display_name_for; re-add same id updates name, roster len == 1
    # --- agents ---
    #  add→registry().agent returns equal Agent incl provider/model; re-add updates
    #  registry().knows(unknown) is False; registry().agent(unknown) raises UnknownAgentError
    # --- results ---
    #  append→for_task returns it; multiple appends come back oldest-first
    #  re-append never overwrites (count grows); for_task filters by task id
    # --- cross-cutting identity ---
    #  same domain errors for the same misuse on BOTH backends (asserted here, once)
    #  read-tolerance parity: a task whose assignee id was removed from members/agents
    #     STILL loads via get/all (repo returns the dangling AssigneeRef; no FK rejects it)

class JsonStorageContract(StorageContractTests, unittest.TestCase):
    def make_backend(self): return JsonStorage(self._tmp)

class SqliteStorageContract(StorageContractTests, unittest.TestCase):
    def make_backend(self): return SqliteStorage(self._tmp / "taskcli.db")
```

The **read-tolerance parity** case is what proves the no-FK decision (§3): it removes an assignee
from members/agents via the port, then asserts the task still loads on both backends — pinning
that SQLite is exactly as permissive as JSON on the dangling-reference path.

### 5c. The existing 53 tests stay green

- The JSON implementation's **class bodies and file layout are unchanged**; only names/locations
  moved and an aggregate was added. `build_service(data_dir)` / `build_execution_service(data_dir)`
  keep their signatures and default to JSON, so every existing call site is untouched.
- The two **JSON-implementation-bound tests** stay bound to JSON and stay valid:
  `test_stage1_bare_string_assignee_reads_as_a_member` and
  `test_removed_agent_renders_unknown_agent_without_crashing` in `test_agents_service.py`, plus
  `test_execution.py`'s registry-wipe, reach into `*.json` files directly. They test
  **JSON-private** behavior (on-disk stage-1 back-compat; file manipulation) that legitimately
  does not exist for SQLite, so they are NOT lifted into the agnostic suite — the agnostic suite
  exercises the *same* read-tolerance behavior through the port instead (§5b), and the
  stage-1-bare-string back-compat is a JSON-only concern the contract says nothing about (§7).

Net: 53 existing (JSON) + one new agnostic suite that runs against both backends.

---

## 6. Localization of the extension (principle 6 — no shotgun surgery)

Adding SQLite touches exactly:

1. **A new implementation of the contract** — the `storage/sqlite/` subpackage (four repos +
   `schema.py` + `SqliteStorage`). One cohesive place; owns everything SQLite.
2. **One wiring branch** — the `if kind == "sqlite"` in `build_backend`, plus one `--backend`
   option string on the parser.

Nothing in `domain/`, `service.py`, `execution/service.py`, `provider.py`, or the CLI's command
handlers changes. A **future third backend** repeats the same two edits (a new subpackage + one
more branch) and nothing else — the extension point is the `StorageBackend` port and the single
`build_backend` switch. That is the demonstration that responsibility for "a backend" is owned in
one place per backend, not scattered (principles 6, 8).

---

## 7. What the contract legitimately leaks (principle 7), and where the backends deliberately differ

**Leaks, legitimately:** "a write can fail" and "this id was not found" — surfaced as the existing
domain errors (`TaskNotFoundError`, `UnknownAgentError`, and the domain's `__post_init__`
validation errors on rebuild). These are things a caller genuinely needs to know and are phrased
in the user's concepts, not storage terms.

**Does NOT leak:** field names, SQL text, table/column names, the `seq` surrogate key, the db
file path, or the JSON file names. No port signature mentions any of them; both backends return
domain objects and raise domain errors only. A caller cannot recover a single storage-internal
name through the contract.

**Where JSON and SQLite deliberately differ, and are NOT forced under a shared abstraction
(principle 10 — duplication/difference is cheaper than the wrong abstraction):**

- **Ordering mechanism for history** — JSON: implicit list-append position; SQLite: explicit
  `seq` autoincrement. Unified only at the behavior "oldest-first," not at the mechanism.
- **Upsert mechanism** — JSON: read-all/replace-or-append/write-all; SQLite:
  `INSERT ... ON CONFLICT DO UPDATE`. Same observable idempotency, different machinery.
- **`succeeded` representation** — native JSON bool vs. SQLite INTEGER 0/1.
- **Stage-1 bare-string assignee back-compat** — a **JSON-only** concern (there is no legacy
  SQLite data; the two stores are independent and there is no migration). The contract is silent
  on it; it stays sealed in `JsonTaskRepository._from_row`. Forcing SQLite to carry a
  back-compat branch it can never exercise would be the wrong abstraction.
- **Referential integrity** — deliberately *absent from both* (no FKs in SQLite), because the
  domain's read-tolerance requires dangling references to survive. Here the danger would be
  SQLite *adding* strictness JSON lacks; the design forbids it.

These differences are each sealed inside one backend and never surface, so they cost nothing to
the caller and buy honesty to each mechanism.

---

## 8. Reasoning against the load-bearing principles (summary)

- **Program-to-a-genuine-interface (2):** the ports are real now — two mechanically different
  implementations exist (whole-file JSON dict-mapping vs. SQL over tables), named and concrete.
  `get` scans a list vs. runs `SELECT`; `save` rewrites a file vs. runs `UPDATE`. The aggregate
  `StorageBackend` is also genuine: its second implementation differs in owning a shared
  connection + DDL where the first owns independent files. Neither is a costume.
- **Interface segregation (3):** four narrow ports carved from the *actual* touchpoints; every
  method has a caller; single-consumer ports (`MemberRepository`, `ResultRepository`) are not
  bundled into one interface that would force a service to depend on methods it never calls.
- **Single responsibility / shotgun surgery (6, 8):** one backend is owned in one subpackage;
  adding a backend is a new subpackage + one branch; the domain/service/CLI-handlers are untouched.
- **Which details leak (7):** domain errors yes; field/table/column/SQL/path names no.
- **Duplication vs. wrong abstraction (10):** JSON and SQLite are unified only where they share a
  contract (the behavior the ports name); where they legitimately differ (ordering, upsert, bool,
  back-compat, FKs) they are left to differ, sealed inside each.
- **Where a rule is enforced (9):** the SQLite schema/DDL lives in exactly one file
  (`sqlite/schema.py`); each backend's row⇄domain mapping lives in exactly one place per entity,
  as today.
- **Naming (11):** concrete classes are renamed to state their backend (`JsonTaskRepository`,
  `SqliteTaskRepository`); the bare `TaskRepository` name is now the contract.

Where a principle does not earn its place at this scale: no backend-plugin-registry-by-name is
introduced (there are exactly two backends; a name→factory map beyond the one `build_backend`
switch would be speculative flexibility for a stage we cannot see); no migration/format-conversion
layer (the two stores are independent by decision); no ORM (stdlib `sqlite3` keeps it
dependency-light).

---

## 9. Result against the design goal

**Status: met.**

The design delivers a storage boundary — four segregated per-entity ports the services depend on,
plus one aggregate `StorageBackend` the composition root selects — over which the application runs
on **either** the existing JSON store **or** a new real-tables SQLite store, chosen at startup
with **JSON as default**, such that all observable task/agent/execution/history behavior is
identical and the domain/service layers are unaware of which backend is live. The two
implementations are genuinely different in mechanism (named: `JsonStorage` over per-entity files,
`SqliteStorage` over one db with a shared connection + DDL), the SQLite schema is real tables/rows
(tagged assignee → two columns; append-only history → rows ordered by a surrogate key), behavior
identity is *proven* by one backend-agnostic conformance suite run against both, and the
extension is localized to one subpackage + one wiring branch. The existing 53 tests remain green
because the JSON implementation's bodies and file layout are unchanged and the default path is
byte-for-byte today's.

**New product tensions / questions surfaced for the Guide:**

1. **`--data-dir` semantics under `--backend sqlite`.** The design reuses `--data-dir` and puts
   the db at `data_dir/taskcli.db`. If the product prefers a distinct `--db-path` option, that is
   a one-line parser/`build_backend` change — flag for confirmation.
2. **No cross-backend migration is provided** (per the non-goals). A user who runs JSON then
   switches to SQLite starts empty on SQLite. This is by decision; noted so it is not a surprise.
3. **The stage-1 bare-string back-compat is JSON-only.** SQLite never had stage-1 data, so it
   carries no equivalent. Consistent with "two independent stores," flagged for awareness.
4. **Builder signature carries both `data_dir` and an optional `backend`.** Chosen to keep the 53
   tests' `build_service(Path)` calls working verbatim; `data_dir` is ignored when an explicit
   backend is passed. If the Guide prefers a single `backend`-only builder (updating the test call
   sites), that is a mechanical follow-up — flagged rather than decided.
