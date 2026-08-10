# Objective selection

The Guide chooses **one engineering objective**, not a complete implementation plan.

## Selection question

Ask:

> Given the current evidence, what uncertainty, structural risk, or missing capability should be resolved next so that subsequent development is less likely to optimize the wrong thing?

## Strong objective patterns

These are a catalog, not a lifecycle:

### Clarify behavior
Use when implementation decisions depend on an unresolved product scenario.

### Discover a change axis
Use when the product is expected to evolve but it is unclear what must vary independently.

### Establish an invariant
Use when correctness depends on a rule that should survive implementation changes.

### Establish ownership/boundary
Use when unrelated responsibilities are beginning to change together or knowledge is leaking across components.

### Prove an architectural assumption
Use when the team is designing around a belief that has not yet been demonstrated.

### Build a vertical slice
Use when enough design exists and the greatest uncertainty is whether the chosen structure works end to end.

### Strengthen a failure boundary
Use when failures, retries, partial writes, concurrency, or external services can violate an important product invariant.

### Simplify accidental complexity
Use when abstractions or indirection exist without a present product force that justifies them.

### Localize a known extension
Use when an actual upcoming variation currently requires coordinated edits in unrelated places.

### Preserve a justified cost
Use when a structural cost is real but evidence shows that removing it would make the product worse or more complex. The correct objective can be to document the trade-off and move on.

## Objective quality test

Reject an objective if:
- success cannot be observed;
- it uses only adjectives such as "clean", "robust", "scalable", or "high quality";
- it contains several independent outcomes joined together;
- it prescribes a named architecture without product evidence;
- it primarily describes file edits;
- it optimizes a metric rather than the underlying product concern.

## Example (unrelated to any particular product domain)

Weak:

> Refactor this area into clean architecture.

Strong:

> Establish one owner for the observed rule that is currently implemented in two paths, while preserving both paths' behavior. Demonstrate the ownership by exercising both paths against the same rule.
