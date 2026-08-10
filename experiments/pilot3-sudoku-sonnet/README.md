# Pilot #3 — design-first (Balash) vs. a plain session, with a **Sonnet executor**

Same method as pilots #1–2, but the executing Workers ran on **Sonnet** (the Guide/design direction
stayed strong). Product: a deterministic printable **Sudoku generator** (static web). Hard invariant:
every puzzle has exactly one solution. Question: does Balash still clear the bar with a weaker executor?

- `balash-arm/` — design objective (see `DESIGN.md`) implemented by Sonnet Workers. `node --test` → 15 pass.
- `direct-arm/` — plain Sonnet session. `node tests/test-core.js` → 33 pass.
- `verdicts/` — two blind reviews (opposite dispositions) + claim-verification (all claims source-checked).

**Result:** both blind judges chose the Balash arm (~80% / ~70%) — six-for-six across three pilots. The
strong design objective carried the Sonnet Worker: it built the hard invariant *by construction*
(`Puzzle.tryCreate`). Closest pilot yet, with honest caveats: uniqueness is intrinsic to Sudoku so the
plain arm also enforced it (by convention, not construction); the plain arm shipped a better difficulty
feature; and the Sonnet executor left a verified fidelity slip (a dead `isSatisfiedBy` with a misleading
comment). See `FINDINGS.md`.
