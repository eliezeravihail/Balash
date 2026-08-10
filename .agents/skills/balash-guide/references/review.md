# Reviewing Worker results

The Guide evaluates claims against the handoff's exit criteria.

## Review order

1. Re-read the objective and exit criteria before reading the Worker's suggested follow-up.
2. Check evidence for each material criterion.
3. Distinguish implementation completion from objective completion.
4. Treat newly discovered facts as inputs to objective selection, not automatic TODO additions.
5. Preserve counterevidence: a design cost may be justified.

## Completion rules

Mark a Guide TODO complete only when the underlying outcome is demonstrated.

Examples:

- "Added interface" is not evidence that the intended change or responsibility is localized.
- "Tests pass" is useful but does not prove a boundary unless the tests exercise that boundary.
- "No cycle detected" does not prove responsibilities are coherent.
- A small duplication can be acceptable evidence of deliberate independence rather than a defect.

## When to reject a Worker result

Reject or reopen when the Worker:
- optimized a proxy metric instead of the stated objective;
- expanded scope without evidence that expansion was necessary;
- created abstractions not tied to a current force;
- changed preserved behavior;
- claims success without observable verification.
