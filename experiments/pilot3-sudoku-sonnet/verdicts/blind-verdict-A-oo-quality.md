# Blind review A — OO/design-quality reviewer (pilot #3, sudoku). Private: X=direct(Sonnet), Y=balash(Sonnet).

Verdict: **Y better designed, ~80%.** Wins on typed domain modeling (Grid/Seed/Puzzle/Difficulty own their
rules; X passes bare 81-arrays) and on invariant ownership — `Puzzle.tryCreate`+`CREATE_GUARD` make "exactly
one solution" true by construction in one guarded place, vs X upholding it by convention inside `digPuzzle`
on a bare object literal. Y = one concept per file; X = a 613-line `sudoku-core.js` god-module fusing
solver+rater+generator+config, with difficulty interpretation scattered across 3 sites and the DOM layer
(`givenMask`) re-deriving domain facts.
Fair to X: its pure/DOM seam is as real as Y's, its tests are arguably more thorough, and it ships a BETTER
PRODUCT FEATURE — technique-graded difficulty (Easy provably solvable without guessing) vs Y's "approximate"
given-count bands. "If the question were which delivers better puzzles, X has a real claim." But on DESIGN
(structure, responsibility, object/seam shape) Y is the cleaner model.
Y worst: edge ceremony — data-only `PuzzleBatch` class, the Symbol guard, and especially immutable `Grid`
whose `withCell` copies 81 cells at every node of the recursive solver (purity vs the hot path). Not
credited to Y for mere layering; credited because its abstractions map 1:1 to real concepts and its
correctness property is structural.
