# Architectural correctness checklist

For each item, the reviewer must state, per repository:
1. Which pole (Correct / Incorrect / Hybrid-violation) the code matches.
2. The exact citation (file, line, or quoted excerpt) proving it.
3. An explicit sentence ruling out the *other* pole — i.e. why this isn't secretly a case that
   only looks correct on the surface. A "correct" verdict without that sentence is invalid.

## 1. Identity & ownership

- **Correct:** an entity with its own persistent identity and lifecycle (e.g. an AI agent) has its
  own type, created/looked-up by id, referenced by id from anything that uses it.
- **Incorrect:** the entity's data is embedded as bare fields directly on whatever references it
  (e.g. `provider`/`model` living directly on `Task`), duplicated per reference.
- **Hybrid violation to rule out:** the entity has an id-based record *and* some of its fields are
  still separately embedded on the referencing object (so the two can drift).

## 2. Invariant placement

- **Correct:** every stated product invariant is enforced at exactly one choke point that every
  code path capable of violating it must pass through.
- **Incorrect:** the same rule is checked independently in two or more call sites (even if both
  currently agree), so a future third call site could forget it.
- **Hybrid violation to rule out:** there is one shared function, but at least one call site
  bypasses it via a different route to the same mutation (e.g. calling the repository's `save`
  directly instead of going through the guarded service method).

## 3. Unrepresentable invalid states

- **Correct:** a state the product declares invalid (e.g. "assigned to a human and an agent at
  once") cannot be constructed — the type system or a single shared constructor forbids it.
- **Incorrect:** the invalid state is representable in the data model and only avoided by callers
  remembering to null out the other field.
- **Hybrid violation to rule out:** construction is guarded, but deserialization (loading from
  disk) is not, so a hand-edited or legacy file can still produce the invalid state at runtime.

## 4. Boundary discipline

- **Correct:** the module(s) the codebase itself calls "domain"/"business logic" contain zero
  imports of a concrete storage/format/technology — checkable from the import list alone.
- **Incorrect:** a domain type has a `to_dict`/`from_json`/`to_row` method, or the service layer
  imports a concrete storage class name.
- **Hybrid violation to rule out:** imports are clean, but a domain method's *logic* still encodes
  a storage assumption (e.g. an ordering or uniqueness rule that only holds for one backend).

## 5. No unreachable or test-only production code

- **Correct:** every class/method/module in the delivered (non-test) source has at least one real
  caller reachable from the CLI/API entry point.
- **Incorrect:** a class or function exists with zero callers outside its own test file, or is
  never instantiated/wired anywhere the running program can reach.
- **Hybrid violation to rule out:** it has one caller, but that caller is itself dead (so the whole
  chain is unreachable transitively even though a naive one-hop grep looks fine).

## 6. Duplication that matters

- **Correct:** where two implementations must satisfy the same contract, any logic that would need
  to change in lockstep between them is factored into one shared place.
- **Incorrect:** two implementations contain byte-identical or near-identical method bodies
  copy-pasted between them.
- **Hybrid violation to rule out (the other direction):** don't flag superficially similar-looking
  code that implements genuinely independent concerns — that duplication is fine. State explicitly
  why a flagged instance is lockstep-coupled and not this case.

## 7. Failure is representable

- **Correct:** an operation that can fail for a product-relevant reason exposes the failure and its
  reason to the caller through the same channel as success (a typed result, a field, a specific
  exception the caller is expected to catch and the product requires catching).
- **Incorrect:** failure is indistinguishable from "never happened" (nothing stored, no field, a
  swallowed exception) when the product cares about the difference.
- **Hybrid violation to rule out:** failure is representable in the type, but the actual write path
  has a branch that skips writing it for one failure mode (e.g. only exceptions are recorded, not
  a runner returning a false/failed result value).

## 8. Defaults are deliberate

- **Correct:** a default a user could be surprised by (a file path, a limit, a fallback) is a
  stated, documented decision.
- **Incorrect:** the default is an accident of an unrelated implementation choice with no comment
  or record explaining it (e.g. relying on `cwd` because that's what the constructor happened to
  receive first).
- **Hybrid violation to rule out:** the default is documented in a docstring, but the documentation
  doesn't match what the code actually does (verify by reading the code, not the comment).

## 9. Naming tells the truth

- **Correct:** a name describes what the thing does/is, confirmed by reading its implementation.
- **Incorrect:** the name implies behavior the implementation does not have, or omits a
  significant side effect (e.g. `get_task` that also mutates cached state, `list_all` that filters
  something silently).
- **Hybrid violation to rule out:** the name is accurate for the common case but silently wrong for
  an edge case the tests don't exercise — state whether you checked the edge case yourself.

## 10. One coherent owner per responsibility

- **Correct:** task lifecycle, persistence, and execution/agent behavior each have exactly one
  module that owns them.
- **Incorrect:** a second, unrelated module also contains logic belonging to one of these
  responsibilities "for convenience" (e.g. the CLI module validates a domain rule itself instead
  of delegating).
- **Hybrid violation to rule out:** ownership is correct for the common path, but an error-handling
  or edge-case branch re-implements a fragment of the owned logic locally instead of delegating.

## 11. Correct division into modules

- **Correct:** each module corresponds to one cohesive concept, sized so a reader can predict which
  module owns a given behavior from the concept alone, before opening the file ("where would
  provider validation live? `providers.py`, obviously").
- **Incorrect:** either direction of failure — (a) one module interleaves multiple concepts that
  would each independently justify their own module (domain rules + CLI parsing + persistence
  tangled together), or (b) one concept is fragmented across many files with no single place a
  reader would land first to understand it.
- **Hybrid violation to rule out:** the file layout *looks* right (plausible names, sensible count)
  but a specific piece of logic conceptually belonging to module A is implemented inside module B
  "because it was convenient" — check actual logic placement, not just file names.

## 12. Absence of a god object

- **Correct:** no single class/module accumulates responsibility for multiple concerns the
  codebase's own stated layering (domain/service/storage/CLI) says belong to different layers.
- **Incorrect:** one class's methods span 3+ of those declared layers — e.g. a "service" class that
  also decides storage format, also validates raw CLI strings, also owns configuration. Test: would
  removing this class force simultaneous changes to the CLI, storage, and domain layers?
- **Hybrid violation to rule out:** the class's name and primary methods suggest one clean
  responsibility, but it has accumulated a handful of loosely related "misc" methods that don't
  serve that stated responsibility — small in count, but a real accumulation pattern starting.

## 13. Encapsulation

- **Correct:** an object's internal state cannot be mutated from outside except through methods
  that preserve its own invariants; nothing external reaches in and changes a field directly with
  no validation.
- **Incorrect:** a caller obtains a live, mutable reference to an object's internals (a returned
  object whose fields it can set directly, or a returned list/dict that is the actual internal
  collection, not a copy) and the object has no way to detect or reject an invalid resulting state.
- **Hybrid violation to rule out:** the object exposes only read-accessors for scalar fields (looks
  encapsulated) but a collection-typed accessor (a list, a dict) returns the internal object by
  reference rather than a copy or an immutable view — mutable state leaking through a "read-only
  looking" API.

## 14. The interface represents the object's purpose, not its internal shape

- **Correct:** a type's public methods express meaningful operations on the concept it models
  (what you can *do* with it), not a 1:1 mirror of its stored fields with no added behavior.
- **Incorrect:** the type is a bag of getters/setters exactly matching its internal fields, with
  zero behavior of its own — all real logic lives elsewhere and pokes at the exposed internals
  directly (an "anemic" object).
- **Hybrid violation to rule out:** the object has real behavioral methods (looks fine) but *also*
  exposes direct field access to the same state alongside them, so callers can silently bypass the
  behavioral methods and mutate the fields directly instead.

## 15. Absence of complex/many function parameters

- **Correct:** a function's parameter list can be understood and used correctly without the reader
  re-checking the signature; parameters that always vary together are grouped into one meaningful
  object rather than passed as several loose primitives of the same type.
- **Incorrect:** a function takes many independent parameters — especially several primitives of
  the same type in a row (a classic mix-up hazard) — or nested optional parameters that create
  implicit, undocumented modes of behavior.
- **Hybrid violation to rule out:** the parameters were grouped into one object (looks fixed), but
  that object is itself just a loose, unvalidated bag mirroring the old parameter list one level
  down — the smell moved, it didn't resolve. (Cross-check against item 14.)

## 16. One consistent naming convention across the codebase

- **Correct:** the same kind of thing is named the same way everywhere — one term per concept
  across every module it appears in, one style for equivalent operations (e.g. all non-mutating
  lookups use the same verb prefix throughout).
- **Incorrect:** the same underlying concept is called by different names in different modules
  (e.g. "member_id" in one file, "assignee_id" in another, referring to the same thing), or
  structurally identical operations follow different naming styles with no visible rule.
- **Hybrid violation to rule out:** naming is fully consistent *within* each module but diverges
  *across* modules with no shared vocabulary, so it reads fine locally while a cross-module search
  for one concept fails because the codebase calls it two different things.

## 17. Uniform error checking, without redundant duplication across internal layers

- **Correct:** a given check is performed at exactly one layer — the earliest point with enough
  information to make it — and inner layers trust that outer layers already validated; if
  defense-in-depth is deliberate, the codebase states why in a comment.
- **Incorrect:** the same check (e.g. "title non-empty") is silently reimplemented at two or more
  layers with no stated reason, so a future rule change requires remembering every copy.
- **Hybrid violation to rule out:** the check exists as one named function (not copy-pasted text),
  but it is *called* redundantly from multiple layers that each also do their own partial pre-check
  before delegating — duplicated effective validation without duplicated source text.

## 18. Error messages are clear and actionable

- **Correct:** an error message names the specific entity/values involved and states what's needed
  to understand or fix the problem (e.g. "task t7 cannot start: prerequisite t3 (Design) is still
  todo").
- **Incorrect:** a generic or unhelpful message ("invalid input", a raw exception `repr()` reaching
  the user, or a message that leaks an internal name/variable instead of the user-facing concept).
- **Hybrid violation to rule out:** the well-tested, commonly-hit error paths have good messages,
  but a less-tested path (corrupt file, unknown backend, a dangling internal reference) falls back
  to a raw traceback instead of the same message discipline — check the uncommon paths
  specifically, not just the ones with example messages already in view.

---

Reviewer instruction: for every item above, produce this shape per repository, not prose:

```
Item N — <repo>: <Correct | Incorrect | Hybrid-violation>
Citation: <file:line or quoted code>
Ruled out: <one sentence confirming why the other pole doesn't secretly apply>
```

A repository's overall "architectural correctness" is the resulting Correct/Incorrect/Hybrid tally
per item — not a synthesized score. Do not average it into a single number.
