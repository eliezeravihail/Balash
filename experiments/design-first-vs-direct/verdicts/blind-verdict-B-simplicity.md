# Blind design review — adversarial (pro-simplicity / YAGNI) reviewer

Second blind review, run with a deliberately opposite prior to test whether the verdict is an artifact
of the judge's philosophy. Reviewer instruction: distrust abstraction that does not pay for itself;
treat extra size as a cost to justify file by file; but still call a god-class, a leaky domain, or an
object that can't guard its invariants a defect even in a small codebase.

Private key: X = direct-arm (plain session), Y = balash-arm (design-first).

## Size

- X (`tasktool`): 7 production files, ~1,075 lines.
- Y (`taskcli`): ~30 production files, ~2,240 lines. ~2x code, ~4x files for the same four requirements.

## Q1 — Which would I rather maintain; does size match problem?

- X's size matches its problem almost exactly. Two exemplary minimal abstractions: the `TaskStore`
  `load()/save(State)` contract (least abstraction that fully does the job, two real backends) and the
  execution seam modeled as a four-line `AgentRunner = Callable[[Agent, Task], Tuple[bool, str]]` —
  same extensibility Y spends a whole `execution/` package on.
- Y's size does NOT earn its keep at the edges: `domain/readiness.py` (an enum that is a bool with a
  label); the four-way JSON repository split (pays on SQLite, buys nothing on JSON and *loses*
  whole-world atomicity X has for free); Member/Team as unrequested scope.
- Y's size DOES earn its keep at the center: `Task` encapsulation, `Prerequisites` as rule-owner,
  `AgentRegistry.require_executable` single gate, serialization-free domain.
- Lean: for a 5-minute change, X; for a business-rule change, Y (the rule has one home and the object
  won't let you corrupt it). Business-rule changes hurt more → lean Y, not a landslide.

## Q2 — Defects X's smallness is hiding

- Anemic + mutable `Task` (public fields; `task.status = DONE` or `task.prerequisites.append(7)` skip
  every rule); rules parked in `TaskManager` (248 lines, ~14 methods) — trends toward god-class though
  still a cohesive transaction script.
- Presentation leak: `TaskManager.assignee_label()` is display logic in the business layer.
- Storage shape leaks into the domain: every `models.py` dataclass carries `to_dict`/`from_dict`, and
  `sqlite_store.py` reuses `task.assignee.to_dict()` as its `assignee_json` column content.
- Primitive obsession: bare `int`/`str` ids.
- **Point for X, in fairness:** X's `Status.next()` is forward-only (no skip, no regress) — a stronger
  invariant than Y's `change_status`, which allows any transition.

## Q3 — Y's abstractions: load-bearing or ceremony?

- Keep (real): `domain/task.py`, `domain/prerequisites.py`, `domain/assignee.py`, `AgentRegistry`,
  `storage/ports.py` + the `SqliteStorage` aggregate (owns a real shared connection), the `Provider`
  port concept.
- Cut (ceremony): `Readiness` enum → bool; four separate JSON repos → one store; the
  `TaskService`/`ExecutionService` split (speculative at this scale). `ids.py`: keep `TaskId` (set
  equality is load-bearing in readiness), lukewarm on `MemberId`/`AgentId`.
- Tell: several Y modules open by arguing for their own right to exist — sometimes admirable clarity,
  sometimes protesting too much.

## Q4 — The cycle call (most decisive): clearly Y

X built transitive DFS (`_reaches`) but follows the *same* creation-time-only, existence-checked,
incrementing-id discipline as Y — under which `_reaches(prereqs, new_id, edges)` can never return true.
X's detector guards a state its own rules make unreachable: the textbook wrong abstraction. Y reasoned
this out and enforced only `require_all_known`, documenting the immutability assumption a future
maintainer would revisit. On this question the larger codebase wrote *less* by reasoning — YAGNI
applied correctly. Goes to Y even on a pro-simplicity prior.

## Q5 — Overall: Y better designed, ~60% (a genuine close call)

Y wins where it counts most (a domain that protects its invariants, clean domain/storage boundary,
single executability gate, the cycle reasoning). Its failures are a nameable minority at the edges and
are decorative. X is a pleasure to read with two masterclass minimal abstractions, a stronger `Status`
invariant, and whole-state atomicity — but its smallness is partly under-modeling: an open mutable
`Task` that can't guard itself, a fat manager holding the domain's rules, a presentation leak,
serialization bleeding into the domain, and the one piece of genuinely dead machinery across both
codebases. **X's defects are structural; Y's are decorative.** Not awarding Y points for looking
disciplined — awarding them because its load-bearing abstractions are real and X's missing ones show
up as concrete weaknesses.

What would make X the better-designed one: if the product stays small and stable (invariant-protection
rarely exercised, Y's edge-ceremony becomes pure tax); if you weight "one obvious place for everything,
atomic whole-state writes" above "each object guards its own rules"; if anemic-domain-with-fat-service
is deemed fine at CLI scale; if Y's ceremony is judged representative rather than edge-confined. Each is
a defensible worldview — hence 60/40, not higher.
