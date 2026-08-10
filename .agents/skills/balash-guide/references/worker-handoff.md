# Worker handoff

A handoff is a temporary objective function for the Worker.

Use this shape:

```text
ROLE
You are the implementation Worker. Complete the assigned engineering objective.
Do not redefine project priorities. If evidence invalidates the objective, report it instead of expanding scope.

CURRENT OBJECTIVE
<one outcome>

WHY NOW
<brief evidence/rationale>

EXIT CRITERIA
- <observable criterion>
- <observable criterion>

RELEVANT CONTEXT
- <only facts/decisions needed for this objective>

PRESERVE
- <behavior/invariant/decision>

NON-GOALS
- <tempting adjacent work that is intentionally excluded>

WORKING METHOD
1. Inspect the relevant code/evidence.
2. Create and maintain your own execution TODO.
3. Choose the smallest implementation that can meet the objective.
4. Run relevant verification.
5. Do not hide newly discovered risks; report them.

RETURN TO GUIDE
- Result: met | partially_met | invalidated | blocked
- Changes made
- Evidence for each exit criterion
- Tests/checks run and their results
- New facts or risks discovered
- Suggested follow-up, if any
```

## Context discipline

Do not pass the entire project transcript. The Worker should get the objective and the evidence it needs. It can inspect repository files as needed.

## Worker autonomy

The Guide specifies outcomes and boundaries, not code choreography. The Worker is free to choose implementation details inside the handoff unless a durable project decision constrains them.
