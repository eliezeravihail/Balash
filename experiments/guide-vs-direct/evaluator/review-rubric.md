# Blinded review rubric

Reviewers should receive anonymized repositories labelled only X/Y, preferably at each stage snapshot, without knowing which is Direct or Guide.

Do not give one composite "quality score". Answer each question with evidence and a short judgment.

## Behavior

- Does the repository satisfy the current stage requirements?
- Are important failure/edge cases covered by tests?

## Change locality

For the change introduced in this stage:

- Which production modules had to change?
- Did the change touch modules whose responsibilities are unrelated to the requirement?
- Did the implementation require a preparatory refactor before the feature could be added?
- Are new extension points tied to the product change, or are they speculative?

## Responsibility and ownership

- Is there a clear place that owns task lifecycle rules?
- Is assignee-specific behavior separated from general task behavior where that separation is justified?
- Is persistence behavior contained enough that storage choices do not leak through unrelated application logic?
- At stage 4, is prerequisite eligibility enforced in one coherent place rather than duplicated across status-change and AI-execution paths?

## Invariants

Identify the product invariants that now exist. For each:

- where is it enforced?
- where is it tested?
- can another path bypass it?

## Accidental complexity

- Which abstractions/classes/interfaces exist only for flexibility?
- Which of them have more than one actual implementation/use?
- Did abstractions introduced earlier become useful in later stages?
- Is there pass-through layering that makes behavior harder to trace without protecting a product force?

## Final judgment

State separately:

- strongest evidence favoring X;
- strongest evidence favoring Y;
- important counterevidence;
- uncertainties that cannot be settled from static review;
- which repository you would prefer to extend with one more unknown requirement, and why.
