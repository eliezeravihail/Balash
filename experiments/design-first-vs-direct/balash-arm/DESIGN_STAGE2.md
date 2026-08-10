# Stage 2 design — an assignee may be a human member OR an AI agent; agent-assigned tasks can be executed

This is a **design**, not an implementation. Signatures below use `...` bodies to fix the
shape a later objective implements against; no method bodies, persistence code, CLI wiring, or
execution logic is written here.

It builds on stage 1 and treats stage-1's durable decisions as constraints. Every place the
design touches one of those decisions is called out with **[touches durable decision]**.

---

## 0. The one shape decision (the dominant uncertainty)

**Is "assignee" one abstraction or two things handled side by side?**

**Decision: one *reference* type that Task holds opaquely, resolved by two authorities handled
side by side. No shared `Directory`/`Assignee` behavioral interface.**

Reasoning, against principle 2 ("would a real second implementation exist, or is it a costume?"):

- A behavioral, polymorphic `Assignee` (`MemberAssignee` / `AgentAssignee` with
  `display_name()` and `is_executable`) *looks* like a real abstraction — the two do differ
  genuinely. But it **fails the stage-1 constraints**: to answer `display_name()` the object
  must either cache a name (staleness — breaks "reads tolerate a stale assignee" and Team's
  ownership of names) or hold a reference to its authority (a value object coupled to Team /
  the registry). And an `AgentAssignee` rich enough to be "the agent" drags **provider/model
  into whatever Task holds** — directly violating "Task acquires no provider/model knowledge."
  So the behavioral-Assignee abstraction is rejected: it is real in the abstract but wrong here.

- A **unified `Directory` interface** (`knows(id)`, `display_name_for(id)`) over `Team` and a
  new `AgentRegistry` would be a genuine two-implementation abstraction. It is still rejected,
  for scale + segregation reasons (principles 3, 10, 12): the execute path needs
  `agent(id) -> Agent` *with provider/model*, which `Team` cannot supply, so a shared interface
  could only cover the `knows`/`display_name_for` subset while kind-routing for execution
  remains anyway. Introducing the ABC would save one two-branch lookup and buy nothing the
  current need requires. Two authorities are two genuinely different concepts (a roster of
  people vs. a registry of agents with provider/model) that merely share two method *names*;
  per "duplication is cheaper than the wrong abstraction," they stay side by side.

- What *is* real and does earn a type is the **reference** a Task holds: "whoever this task is
  assigned to, which may be a member or an agent." That is a value object (`AssigneeRef`),
  judged under primitive-obsession (principle 4), not under interface/costume (principle 2). It
  has meaning, a validity rule, and more than one caller (Task holds it; the display resolver
  reads it; the execute gate reads it). Task carries it **opaquely** and never branches on its
  kind, so Task stays kind-agnostic — it gets *simpler*, losing even its member-specificity.

Net: **Task holds `Optional[AssigneeRef]`. Two authorities (`Team`, `AgentRegistry`) resolve
the two kinds side by side. Executability is a property of the *reference's kind*, gated in one
place, never known to Task.**

---

## 1. Domain shape — concepts, types, and the signatures to build against

### 1a. New value objects

`AgentId` — parallel to `MemberId`. **Earns a type** (principle 4): referenced by *both* tasks
(via `AssigneeRef`) and execution results → a genuine second caller.

```python
# domain/ids.py
@dataclass(frozen=True)
class AgentId:
    value: str
    def __post_init__(self) -> None: ...   # non-blank, same rule shape as MemberId
    def __str__(self) -> str: ...
    # caller-supplied at registration, mirroring Member (no .new()); see §2.
```

`AssigneeKind` — a closed set of exactly two, modelled like `Status` (principle 4, closed
vocabulary):

```python
# domain/assignee.py
class AssigneeKind(Enum):
    MEMBER = "member"
    AGENT = "agent"
```

`AssigneeRef` — the reference Task holds. A value object, not a costume interface. It answers
one small question about *itself* (`is_agent`) so callers tell-don't-ask rather than pulling
`.kind` out and comparing (principle 1); it never resolves names or runs anything.

```python
# domain/assignee.py
@dataclass(frozen=True)
class AssigneeRef:
    kind: AssigneeKind
    id_value: str                     # the underlying MemberId/AgentId value

    def __post_init__(self) -> None: ...          # id_value non-blank; kind is an AssigneeKind

    @classmethod
    def member(cls, member_id: MemberId) -> "AssigneeRef": ...   # kind=MEMBER
    @classmethod
    def agent(cls, agent_id: AgentId) -> "AssigneeRef": ...      # kind=AGENT

    @property
    def is_agent(self) -> bool: ...               # kind is AGENT — the executability signal

    def as_member_id(self) -> MemberId: ...        # typed accessor for the resolver (MEMBER only)
    def as_agent_id(self) -> AgentId: ...          # typed accessor (AGENT only)
```

### 1b. Agent (new persisted entity)

```python
# domain/agent.py
@dataclass(frozen=True)
class Agent:
    id: AgentId
    display_name: str
    provider_name: str     # belongs to the agent, NOT to any task
    model_name: str        # belongs to the agent, NOT to any task
    def __post_init__(self) -> None: ...   # all non-blank; one constructor, fresh & rebuild both here
```

`provider_name` / `model_name` **stay plain strings**, not value objects — deliberately, per
the stage-1 precedent that kept `title`/`description` plain: their only rule is "non-blank,"
validated in exactly one place (Agent's constructor), with no second caller re-implementing a
rule. **[touches durable decision: typed-vocabulary-only-with-a-second-caller]**

### 1c. AgentRegistry (the authority — analog of Team)

```python
# domain/agent.py
class AgentRegistry:
    def __init__(self, agents: Iterable[Agent] = ()) -> None: ...
    def knows(self, agent_id: AgentId) -> bool: ...
    def agent(self, agent_id: AgentId) -> Agent: ...            # reality gate; raises UnknownAgentError
    def display_name_for(self, agent_id: AgentId) -> str: ...   # for the read-model
    def require_executable(self, assignment: Optional[AssigneeRef]) -> Agent: ...  # THE execute gate, §4
    def __iter__(self) -> Iterator[Agent]: ...
    def roster(self) -> List[Agent]: ...
```

### 1d. ExecutionResult (new domain record)

A stored historical fact. It is intentionally a **record with no rich behavior** — an execution
result *is* an immutable fact ("this run happened, it succeeded/failed, here is the text"); a
behavior on it would be artificial. This is a justified exception to the anemic-domain concern
(principle 5), not an oversight.

```python
# domain/execution_result.py
@dataclass(frozen=True)
class ExecutionResult:
    task_id: TaskId
    agent_id: AgentId
    succeeded: bool
    output: str
    def __post_init__(self) -> None: ...   # one construction funnel; fresh & rebuild both here
```

**Identity/ordering decision:** an `ExecutionResult` gets **no `ExecutionResultId` value
object**. Nothing references a result by id (append-only; never fetched or updated singly), so
such a type would have exactly one caller and fail the second-caller test (principle 4, applied
in the restraining direction). **Ordering is by append order in the store** — the result store
appends and returns rows in insertion order, which is chronological. If the product later wants
an explicit timestamp column it is a plain field added to this record, still not a new id type;
noted, not built.

### 1e. Task — what changes

**[touches durable decision: Task holds an assignee id and does not know the roster.]** The
change *generalizes the assignee's type* while preserving the behavior exactly: Task still holds
one opaque assignee, still trusts an already-validated reference, still routes all construction
through one `__init__`.

```python
# domain/task.py  (deltas only)
def __init__(self, task_id, title, description, status,
             assignee: Optional[AssigneeRef]) -> None: ...   # was Optional[MemberId]
def assign_to(self, assignee: AssigneeRef) -> None: ...       # was (member_id: MemberId)
def unassign(self) -> None: ...                               # unchanged
@property
def assignee(self) -> Optional[AssigneeRef]: ...              # was Optional[MemberId]
@property
def is_assigned(self) -> bool: ...                            # unchanged
```

Task **loses** its `MemberId` import and gains no `AgentId` import — it now depends only on
`AssigneeRef`, and never on either kind. It gains **no** `is_executable`, **no** kind branch,
**no** provider/model. `create()` is unchanged (fresh task starts unassigned).

### 1f. New domain errors

```python
# domain/errors.py
class UnknownAgentError(DomainError): ...          # analog of UnknownMemberError
class TaskNotExecutableError(DomainError): ...     # task is unassigned or assigned to a human
```

---

## 2. Where each rule is owned (the ownership map)

| Rule / question | Owner (single funnel) | How the human path is preserved |
|---|---|---|
| "Is this **member** real?" | `Team.member(id)` (unchanged) | Untouched. |
| "Is this **agent** real?" | `AgentRegistry.agent(id)` | New, symmetric with `Team.member`. |
| "Which **kind** is this assignee?" | `AssigneeRef` itself (`is_agent`, kind) | Task never asks; only the resolver / execute gate do. |
| "Resolve a **display name**" | the read-model builder in the service, routing by `ref.kind` to `Team.display_name_for` (unchanged) **or** `AgentRegistry.display_name_for` | The member branch is byte-for-byte the stage-1 code. |
| "**Only an agent-assigned task can be executed**" | `AgentRegistry.require_executable(assignment)` — ONE method, §4 | Humans never reach execute; the gate refuses non-agent assignments. |
| "You may only **assign** to a real X" | one gate *per kind* (`Team.member`, `AgentRegistry.agent`), both funnelling into `Task.assign_to(ref)` | Human assign gate + Task mutator behavior unchanged; only the service wraps the validated id in `AssigneeRef.member(...)`. |

Two assign gates (not one unified gate) because reality-checking a human against the roster and
an agent against the registry are two genuinely different lookups against two different
authorities (principle 10 — not duplication to unify). The **single funnel on the Task side** is
`Task.assign_to(ref)`, which every assign path passes through.

### Assignment orchestration (extends `TaskService`, unchanged behavior for humans)

`TaskService` already owns member registration + roster + assignment; agent registration and
agent-assignment are the *same reason to change* (task/roster orchestration), so they extend it.
It gains an `AgentRepository` collaborator alongside its member repo.

```python
# service.py  (new/changed methods — signatures only)
def add_agent(self, agent_id: str, provider: str, model: str, display_name: str) -> Agent: ...
def agents(self) -> List[Agent]: ...

def assign_task(self, task_id: str, member_id: str) -> None: ...       # UNCHANGED body:
    # member = self._members.team().member(MemberId(member_id))        #   gate (unchanged)
    # task.assign_to(AssigneeRef.member(member.id))                     #   only wrap-in-ref is new
def assign_task_to_agent(self, task_id: str, agent_id: str) -> None: ...
    # agent = self._agents.registry().agent(AgentId(agent_id))          #   agent reality gate
    # task.assign_to(AssigneeRef.agent(agent.id))
```

---

## 3. Execution — the single gate and the collaboration

### 3a. The one gate every execute funnels through

```python
# domain/agent.py  (on AgentRegistry)
def require_executable(self, assignment: Optional[AssigneeRef]) -> Agent:
    """The single place 'only an agent-assigned task can be executed' is enforced.
    Refuses None or a member-kind assignment (TaskNotExecutableError); refuses an
    agent id it does not know (UnknownAgentError); otherwise returns the Agent
    (which carries provider/model)."""
    ...
```

It composes both checks in one auditable method: the *kind* check is delegated to the ref
(`assignment.is_agent`, tell-don't-ask), the *reality* check is the registry's own
`agent(...)`. One place to read to know the rule is safe (principle 9).

### 3b. Execution lives in a separate `ExecutionService` (application layer)

Execution has genuinely different collaborators (a provider, a result store) and a different
reason to change than task/roster orchestration → its own service (principle 8, SRP). Domain
stays free of provider/storage: the provider and result repo are held here, not in the domain.

```python
# execution/service.py
class ExecutionService:
    def __init__(self, tasks: TaskRepository,
                 agents: AgentRepository,
                 results: ResultRepository,
                 provider: Provider) -> None: ...
    def execute(self, task_id: str) -> ExecutionResult: ...
```

### 3c. The execute collaboration (sequence)

```
ExecutionService.execute(task_id)
  1. task    = tasks.get(TaskId(task_id))                     # load
  2. agent   = agents.registry().require_executable(task.assignee)   # THE gate → Agent (+provider/model)
  3. request = ExecutionRequest(agent.provider_name, agent.model_name,
                                task.title, task.description)  # minimal work data; no ids leak to provider
  4. outcome = provider.run(request)                          # ExecutionOutcome(succeeded, output) — network-free seam
  5. result  = ExecutionResult(task.id, agent.id, outcome.succeeded, outcome.output)
  6. results.append(result)                                   # append-only history
  7. return result
```

- **Task** hands over only its `AssigneeRef` (step 2) and its title/description (step 3). It
  never sees a provider. **[touches durable decision: Task ignorant of providers.]**
- **AgentRegistry** is the only thing that turns an assignment into a runnable Agent.
- **Provider** does the work and reports success/failure + text; it receives no domain ids.
- **ResultRepository** stores the fact.
- **Status is NOT touched here** — see §6.

---

## 4. The provider seam (network-free), and what it legitimately leaks

```python
# execution/provider.py   (application layer — NOT domain; keeps the port out of the domain)
@dataclass(frozen=True)
class ExecutionRequest:
    provider_name: str
    model_name: str
    title: str
    description: str

@dataclass(frozen=True)
class ExecutionOutcome:
    succeeded: bool
    output: str

class Provider(Protocol):
    def run(self, request: ExecutionRequest) -> ExecutionOutcome:
        """Run the agent's work and report success/failure + text output."""
        ...

class LocalProvider:
    """The one real implementation now: deterministic local output, NEVER touches the
    network. Reads provider_name/model_name to shape its text; invents no network call."""
    def run(self, request: ExecutionRequest) -> ExecutionOutcome: ...
```

**Is `Provider` a real interface or a costume (principle 2)?** Real. The plausible, genuinely
different second implementation is an actual AI provider that makes an HTTP call to a model API
and returns the same `succeeded/output` contract — same behavior, entirely different mechanism,
exactly the `Animal.make_sound()` shape. It is introduced *because the current execute need
already requires* expressing "run work that can fail" without hard-coding the mechanism, so it
is not speculative. **The real provider is out of scope and is NOT built or scaffolded** — only
the `Provider` port + the single `LocalProvider`.

**What the seam legitimately leaks (principle 7):** "work can fail" (`succeeded`) and "work
produces text" (`output`). **What it must not leak, and does not:** that this is/ever will be a
network call, HTTP/SDK types, retries, or the fake's internals. `ExecutionOutcome` is a plain
success+text record with none of that.

**No provider selection is built.** There is exactly one provider today; it is wired at the
composition root and injected. `agent.provider_name` is persisted and passed into the request
(honest about the seam, ready for a future real provider), but **no registry/plugin map keyed by
provider_name** is introduced — that would be speculative flexibility for a stage we cannot see.
`ExecutionRequest`/`ExecutionOutcome` are deliberately *not* domain types (the provider must not
receive or return domain ids), which is why they live in the execution layer, not `domain/`.

---

## 5. Persistence — new stores over the same JSON backend

**[touches durable decision: one JSON backend, no storage interface/ABC.]** Two new concrete
repositories join the existing two, each owning one file and its own row mapping, all over the
shared `_jsonfile` helper. No interface is introduced.

```python
# storage/agent_repository.py
class AgentRepository:
    def __init__(self, path: Path) -> None: ...
    def add(self, agent: Agent) -> None: ...                 # upsert by id, like MemberRepository.add
    def registry(self) -> AgentRegistry: ...                 # load all → the authority (mirrors .team())
# _to_row/_from_row: id, display_name, provider, model — the only place agents' disk shape lives.

# storage/result_repository.py
class ResultRepository:
    def __init__(self, path: Path) -> None: ...
    def append(self, result: ExecutionResult) -> None: ...   # APPEND ONLY — never overwrites; keeps history
    def for_task(self, task_id: TaskId) -> List[ExecutionResult]: ...  # in append (chronological) order
# no save()/update — re-running execute simply appends another row; prior rows are untouched.
```

- Files: `agents.json`, `results.json`, chosen at the composition root next to
  `tasks.json`/`members.json`.
- Construction funnels through each domain type's one constructor via `_from_row`
  (`Agent(...)`, `ExecutionResult(...)`), exactly like the existing repos.

### Task row shape change (owned entirely inside `TaskRepository`)

The task row's `assignee` becomes the tagged form; the mapping stays the only code that knows
disk shape:

```python
# task_repository._to_row:   "assignee": {"kind": ref.kind.value, "id": ref.id_value} | None
# task_repository._from_row: dict  -> AssigneeRef(kind, id)
#                            str   -> AssigneeRef.member(MemberId(str))   # back-compat: stage-1 bare-id rows read as MEMBER
#                            None  -> None
```

Back-compat for existing stage-1 data lives in `_from_row` (a bare string = a member), so old
stores keep working without a migration step.

---

## 6. Display resolution + read-tolerance, extended

**[touches durable decision: reads tolerate a stale assignee.]** The resolver moves from a
member-only lookup to a kind-routed one, in the same place (the service read-model builder), and
extends the tolerance to agents.

```python
# service.py  (extends _assignee_label; loads BOTH authorities once per list/show)
def _assignee_label(ref, team, registry) -> str:
    if ref is None:                      return "unassigned"
    if not ref.is_agent:                 # MEMBER — unchanged stage-1 behavior
        return team.display_name_for(...) if team.knows(...) else f"{id} (unknown member)"
    # AGENT — new, symmetric tolerance
    return registry.display_name_for(...) if registry.knows(...) else f"{id} (unknown agent)"
```

- A task pointing at a **removed agent** renders `"<id> (unknown agent)"` rather than crashing a
  read — the exact extension of the stage-1 `"(unknown member)"` decision.
- `list_tasks`/`show_task` now load both the `Team` and the `AgentRegistry` once and pass both
  into `_view`. `TaskView` is unchanged: `assignee` is still a single resolved display string,
  so the CLI's formatting is untouched.
- Result history display (if a `results <task_id>` command is added) tolerates a removed agent
  the same way; noted, CLI wiring out of scope for this design.

**New value objects recap (principle 4):** `AgentId` (2nd caller: tasks + results — earns it),
`AssigneeKind` (closed 2-value vocabulary — earns it), `AssigneeRef` (meaning + rule + multiple
callers — earns it). **Deliberately NOT typed:** `provider_name`, `model_name` (single non-blank
rule, one validation site — like `title`/`description`), and an `ExecutionResultId` (no second
caller).

---

## 7. Decide-and-report

**Executing a task does NOT change the task's status.** `ExecutionService.execute` produces and
stores an `ExecutionResult` and does nothing else — it never calls `task.change_status` and
never saves the task. The grounded facts enumerate only "a result is produced and stored," so no
status side-effect is added on our initiative. **Product owner can veto this**; if a status
transition on execute is wanted, it is a one-line addition in `ExecutionService.execute` (route
it through the existing `Task.change_status` gate), not a structural change.

---

## 8. Reasoning against the load-bearing principles (summary)

- **Program-to-a-genuine-interface (2):** the only behavioral interface introduced is
  `Provider`, whose real second implementation (a networked AI provider) is concrete and
  plausible — not a costume. The *assignee* is deliberately **not** a behavioral interface: the
  reference is a value object (`AssigneeRef`) and the two authorities stay side by side, because
  a shared `Directory`/`Assignee` abstraction would either leak provider/model into Task or buy
  nothing the current need requires.
- **Where rules are enforced (9):** "known member" = `Team.member` (unchanged); "known agent" =
  `AgentRegistry.agent`; "only agents execute" = `AgentRegistry.require_executable` — one method
  each, every real path funnels through them.
- **Tell-don't-ask / anemic model (1, 5):** assignment and execution are things callers *tell*
  objects to do; `AssigneeRef.is_agent` and `require_executable` keep the kind decision inside
  objects rather than pulled out and branched externally. `ExecutionResult` is a justified
  record (an immutable fact), the single deliberate anemic type.
- **Leaky abstractions (7):** the provider leaks "work can fail" + "text output"; it hides
  "network call" and the fake's internals.
- **Single responsibility (8):** agent *identity* (`AgentRegistry`), *running* a provider
  (`Provider`/`ExecutionService`), and *storing* a result (`ResultRepository`) are three
  distinct reasons to change, in three places.
- **Primitive obsession (4):** new types only where a second caller has a rule; explicitly
  restrained on provider/model names and a result id.
- **Duplication vs. wrong abstraction (10):** two assign gates and two authorities kept
  side-by-side over a forced shared interface, on purpose.

---

## 9. Result against the design goal

**Status: met.**

Every behavior the objective requires has a named owner and a single funnel: an assignee may be
a member (unchanged) or an agent; agents are a persisted entity with provider/model owned by the
agent and absent from Task; the two "is this real?" gates and the one "only agents execute" gate
are each single places; execution runs through a network-free provider seam whose leak is
honest; results append to history without overwrite; read-tolerance covers a removed agent.

**New product tensions surfaced for the Guide/product owner:**

1. **Status-on-execute** (decide-and-report above) — explicitly left as no-op; needs a veto or
   a confirm.
2. **Agent id provenance** — this design mirrors `Member`: the agent id is *caller-supplied* at
   registration (referenceable by a stable handle the user types), not minted like a `TaskId`.
   If agents should instead get minted ids, that is a small change to `add_agent`/`AgentId` —
   flag for confirmation.
3. **Removing/deleting agents** is out of scope (as with members), yet read-tolerance now
   assumes an agent *can* vanish from the registry. The tolerance is designed; an actual
   remove-agent command is not — consistent with stage-1's stance on members.
