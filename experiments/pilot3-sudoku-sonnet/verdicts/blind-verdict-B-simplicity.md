# Blind review B — pro-simplicity/YAGNI reviewer (pilot #3, sudoku). Private: X=direct(Sonnet), Y=balash(Sonnet).

Verdict: **Y better designed, ~70%** — "not a blowout." Note: Y is MORE layered but SLIGHTLY SMALLER (~815
vs ~920 LOC); X is flatter but larger, the bulk buying a real ~170-line technique difficulty rater.
Y wins on the two things that matter most: it OWNS the one correctness invariant by construction in one
place (`Puzzle.tryCreate`+`CREATE_GUARD`, illegal state unrepresentable), and it SPLITS responsibilities that
X welds into a 613-line module while passing bare arrays through to the DOM. X's three real defects (count
even against a lean codebase): the god-module; invariant-by-convention on a bare array; and `app.js:givenMask`
re-deriving "a given is a non-empty cell" in the presentation layer (redundantly).
Docked Y for trimmable ceremony, incl. a VERIFIED defect: `Difficulty.isSatisfiedBy` is dead in production
(generator compares min/max inline; the method is exercised only by tests) — "an abstraction paying rent to
nobody, and a comment that lies about it." Also `PuzzleBatch`-as-class and the `Difficulty` dual API. And the
immutable `Grid.withCell` 81-cell copy in the solver's hot path (X's in-place bitmask solver is leaner).
Credits X's technique difficulty as a genuine product feature (better than Y's bands) and its leaner solver.
Flip-to-X condition: if X (a) extracted a Puzzle type built only through the uniqueness check and (b) split
the god-module, its better product + less indirection would win. As they stand, the one that can't emit a
non-unique puzzle and doesn't concentrate six jobs in one file is better designed — Y.
