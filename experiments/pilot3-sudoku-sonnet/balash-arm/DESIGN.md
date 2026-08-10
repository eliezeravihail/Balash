# Design: Deterministic Printable Sudoku Generator

A static page: pick a difficulty and count, get a printable batch of 9x9
Sudoku puzzles plus answer keys. No backend, no build step, no libraries.
Generation only — no interactive solving.

## Domain model

| Type | Owns |
|---|---|
| **Grid** | The 9x9 cell layout and Sudoku's placement rule (no repeat in any row/column/box). Immutable value: `cellAt(pos)`, `withCell(pos, value)`, `emptyPositions()`, `isFilled()`. Knows nothing about difficulty, randomness, or puzzles — just "is this arrangement legal." |
| **Solver** (`countSolutions(grid, limit)`) | The *only* place that answers "how many solutions does this Grid have." Backtracking search that stops counting as soon as it finds `limit` solutions — callers only ever ask for `limit = 2` (they need "exactly one" vs "more than one," never the true count), which bounds worst-case search cost. Pure function; no state. |
| **Puzzle** | Givens (a partially-filled Grid) paired with its Solution (a fully-filled Grid). **The one-solution invariant lives here, at construction time**: the *only* way to obtain a `Puzzle` is `Puzzle.tryCreate(givensGrid)`, which internally calls `Solver.countSolutions(givens, 2)`. If the count isn't exactly 1 it returns `NotUnique` instead of a `Puzzle`. There is no other constructor, no setter that mutates givens after creation. Consequence: **if you're holding a `Puzzle` object, uniqueness is a fact, not a hope** — nothing downstream (renderer, batch, print view) ever re-checks it. |
| **Difficulty** | The rule for "how hard." A closed set of named levels (Easy/Medium/Hard), each owning a target *given-count band*. Exposes `isSatisfiedBy(puzzle)` — the generator asks Difficulty to judge a candidate rather than the generator hardcoding thresholds inline. Difficulty owns its own rule; changing what "Hard" means is a one-file change. |
| **Seed** | A value type wrapping a normalized string/int identity. Owns turning that identity into a deterministic number stream (a small seeded PRNG, e.g. mulberry32) via `seed.stream()`, and owns deriving per-puzzle child seeds for a batch via `seed.derive(index)`. This is the single place "same seed → same numbers" is decided; nothing else in the codebase calls `Math.random`. |
| **PuzzleBatch** | An ordered list of Puzzles plus the `(Seed, Difficulty, count)` that produced them. Pure data — the reproducible, shareable unit ("give someone this seed+difficulty+count and they get this exact batch"). |
| **PuzzleGenerator** | Orchestrates Grid + Solver + Difficulty + Seed to produce a `PuzzleBatch`. This is the pure core's single entry point: `generateBatch(seed, difficulty, count) -> BatchResult`. Contains no DOM, no print, no rendering. |

## Boundaries

- **Pure core** = `Grid`, `Solver`, `Puzzle`, `Difficulty`, `Seed`, `PuzzleBatch`, `PuzzleGenerator`. All plain data/functions operating on numbers and arrays-of-cells wrapped in the types above — no `document`, no HTML strings, no I/O. This layer is unit-testable headless and is the real seam: a different output (print HTML today, a PDF library or a CLI tomorrow) can sit behind it untouched.
- **Uniqueness** is guaranteed exactly once, inside `Puzzle.tryCreate`, which is itself the only path that produces a `Puzzle`. The digging loop in `PuzzleGenerator` calls the same `Solver.countSolutions` while deciding whether a candidate cell is safe to remove — same function, same code path, no duplicated "am I still unique" logic (principle 9: one enforcement point).
- **Difficulty rule** lives only in `Difficulty`. The generator never compares given-counts against magic numbers itself; it calls `difficulty.isSatisfiedBy(candidate)`.
- **Determinism** lives only in `Seed`. Every random decision in generation (fill order for the full solution, removal order for digging, which child seed each batch slot uses) is drawn from a stream produced by `Seed`, so `generateBatch` is a pure function of `(Seed, Difficulty, count)`.
- **Rendering** (`rendering/print-view.js`, DOM-aware) walks a finished `PuzzleBatch` to build two printable sections: puzzle pages and answer-key pages. It only ever reads `Puzzle.givens()` and `Puzzle.solution()` — it cannot construct or mutate a Puzzle, so it cannot accidentally introduce an unverified one.
- **App/UI layer** (`app/controller.js`) is thin glue: reads the difficulty/count/seed form inputs, calls `PuzzleGenerator.generateBatch`, hands the result to the renderer, wires the print button. It owns no domain rules.

## Key decisions and why

**Generate-full-then-dig, not direct construction.** Build one fully-solved, legal `Grid` first (randomized backtracking fill, seeded), then remove givens one at a time in a seeded-random order, checking after each removal that `Solver.countSolutions(candidate, 2) == 1` still holds; stop removing along a branch the moment removal would make it non-unique, and skip that cell. This is the standard, provably-correct construction for uniquely-solvable puzzles, is simple to implement and reason about, and needs only one solver — no separate "puzzle synthesis" algorithm. A fully-solved grid is trivially satisfiable, so the invariant only has to be defended while removing cells, not while adding them.

**Difficulty as a given-count band, not a technique-rating engine.** At this product's scale (a static printable-puzzle page, not a solving app) a technique-based rating (naked singles vs. hidden pairs vs. requires guessing) is real complexity for real value, but it's more machinery than three named tiers need. The design models Difficulty as an owned rule object precisely so that upgrade is contained to one file later, without redesigning Puzzle/Generator/Seed. Stated explicitly: **this is a place the design deliberately does not over-build.**

**Seed is surfaced, not hidden.** The UI shows the seed used for a batch (auto-generated if the user didn't supply one) and lets the user type one in. `Seed` derives one child seed per batch slot (`seed.derive(i)`) rather than reusing one PRNG stream across all puzzles, so batches are stable under a count change in a defined way (asking for 5 puzzles gives you the same first 3 as asking for 3) — a reasonable determinism contract to state, not an accident of implementation.

**Failure is a value, not an exception or a silent bad puzzle.** Digging can, in principle, get stuck (no more cells are safely removable) before reaching a difficulty's target band. `PuzzleGenerator` bounds retries (a few reshuffled removal orders drawn from the same derived seed) and if a slot still can't satisfy `Difficulty`, that slot's result is `Failed(reason)`, not a thrown exception and not a puzzle that quietly ignores the difficulty target. `generateBatch` returns a batch-level result that distinguishes "all N puzzles ready" from "slot k failed" so the UI can say so and offer "try a different seed" instead of either crashing or printing a mislabeled puzzle. In practice, for standard 9x9 with reasonable bands this should essentially never trigger — but the design does not assume that; it names the outcome.

## Module/responsibility skeleton

```
domain/grid.js          Grid: cell layout + Sudoku placement legality. No randomness, no I/O.
domain/solver.js         countSolutions(grid, limit): the sole "how many solutions" authority.
domain/puzzle.js         Puzzle.tryCreate(givens): the sole path to a verified-unique Puzzle.
domain/difficulty.js     Difficulty levels + isSatisfiedBy(puzzle): owns the difficulty rule.
domain/seed.js           Seed: normalizes an identity, derives PRNG streams and child seeds.
domain/puzzle-batch.js   PuzzleBatch: (seed, difficulty, count, puzzles) as reproducible data.
domain/generator.js      generateBatch(seed, difficulty, count): fill -> dig -> assemble batch.
rendering/print-view.js  PuzzleBatch -> printable HTML (puzzle pages + answer-key pages). DOM-aware.
app/controller.js        Wires form inputs to generator + renderer + window.print(). No rules.
```

## Open product questions

- Exact given-count bands per difficulty (and whether a future "Hard" needs a technique ceiling, not just fewer givens).
- Must puzzles within one batch be guaranteed distinct from each other, or is "different seed per slot" considered sufficient?
- Practical max batch size for print (page/performance ceiling of backtracking-based generation in-browser).
- Is the seed meant to be user-editable/shareable as a headline feature (e.g. shown in print footer, put in the URL), or just an internal reproducibility detail?
- Target paper size/print layout (A4 vs Letter, one puzzle per page vs grid of puzzles) — a rendering-layer question, but it affects how much batch metadata the renderer needs from `PuzzleBatch`.
