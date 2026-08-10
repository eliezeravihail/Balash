# Scrutiny of the blind judges — claim verification (pilot #3, sudoku, Sonnet executor)

Private key: X = direct-arm (plain Sonnet), Y = balash-arm (design-first, Sonnet Workers).

| # | Claim | Direction | Verified? | Evidence |
|---|---|---|---|---|
| 1 | Y owns the one-solution invariant BY CONSTRUCTION: `Puzzle.tryCreate` is the sole path, `new Puzzle` throws without a module-private `CREATE_GUARD` symbol, uniqueness checked via `countSolutions(givens,2)===1` at creation | for Y (decisive) | **YES** | `domain/puzzle.js`: `CREATE_GUARD=Symbol(...)` (l.23), ctor throws unless guard matches (l.30-31), `tryCreate` the only mint (l.41-46). `countSolutions` only in puzzle.js + generator.js |
| 2 | X enforces uniqueness only by CONVENTION: gated inside `digPuzzle`, but the shipped puzzle is a bare 2-D array with no type/chokepoint | against X | **YES** | `sudoku-core.js`: uniqueness gate `countSolutions(board,2)===1` at l.524 inside digging; `generateBatch` returns `{givens, puzzle: toGrid(...), solution: toGrid(...)}` (l.590-592); `hasUniqueSolution` exists (l.226) but is a helper, not a gate |
| 3 | X's `sudoku-core.js` is a ~613-line god-module fusing full-grid build, solver, a ~170-line technique difficulty rater, presets, digging, batch | against X | **YES** | 613 lines, 28 functions incl. `rateLogicalDifficulty` |
| 4 | Y's `Difficulty.isSatisfiedBy` is effectively DEAD in production — its doc comment says the generator asks it to judge, but the generator compares `difficulty.min/max` inline; `isSatisfiedBy` is referenced only by tests | **against Y** | **YES** | `isSatisfiedBy` refs: only `test/domain.test.js` (l.101,160) + its def `difficulty.js:28` + the claiming comment `difficulty.js:5`. `generator.js` uses `difficulty.max-difficulty.min` (l.158), `finalCount<difficulty.min||>difficulty.max` (l.180) inline — never calls `isSatisfiedBy` |
| 5 | X ships a genuinely better product feature: technique-based difficulty ("Easy provably solvable by singles, no guessing") vs Y's admittedly-approximate given-count bands | for X | **YES** | X `rateLogicalDifficulty` (naked/hidden singles, locked candidates, pairs); Y `difficulty.js` = given-count bands, its own comment calls them "approximate targets" |

## Reading

All five load-bearing claims verify — including two that cut AGAINST the design-first arm (claim 4, a
dead abstraction with a comment that overstates it; claim 5, the plain arm's better difficulty feature).
Neither judge confabulated. Claim 4 is notable: it is a **fidelity slip by the Sonnet executor** — it
built the `isSatisfiedBy` method the design specified but did not route the generator through it, leaving
dead code and a misleading comment. A finding about the executor, caught by source-verified scrutiny.
