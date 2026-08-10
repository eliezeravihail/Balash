// domain/generator.js
//
// PuzzleGenerator: orchestrates Grid + Solver + Difficulty + Seed to
// produce a PuzzleBatch. The pure core's single entry point:
//   generateBatch(seed, difficulty, count) -> BatchResult
// No DOM, no print, no rendering. No Math.random/Date -- every random
// choice is drawn from a stream derived from `seed` (D4).
//
// Generate-full-then-dig (D3): build one fully-solved, legal Grid via
// randomized backtracking, then remove givens one at a time in a
// seeded-random order, using Solver.countSolutions(candidate, 2) after
// each removal to confirm the candidate is still uniquely solvable
// before accepting it. This is the SAME solver call the Puzzle
// constructor uses (D2) -- the digging loop uses it only to decide
// which cells are *safe to remove*; the final Puzzle object is always
// produced via Puzzle.tryCreate, which re-derives uniqueness itself.
// Uniqueness as a fact about a Puzzle is therefore still established in
// exactly one place.
//
// Failure is a value (D6): if digging gets stuck before a candidate's
// given-count lands in Difficulty's band, or Puzzle.tryCreate somehow
// rejects the final givens, that attempt fails; a slot retries a bounded
// number of times with fresh derived attempt-seeds, and if it still
// can't produce a puzzle satisfying the difficulty, the slot's result is
// { ok: false, reason }. generateBatch surfaces the first such failure
// as part of its BatchResult rather than throwing or returning a
// mislabeled puzzle.

import { Grid, CELL_COUNT } from './grid.js';
import { countSolutions } from './solver.js';
import { Puzzle } from './puzzle.js';
import { PuzzleBatch } from './puzzle-batch.js';

const MAX_ATTEMPTS_PER_SLOT = 8;

// generateBatch(seed, difficulty, count) -> BatchResult
//
// BatchResult is one of:
//   { ok: true,  batch: PuzzleBatch }
//   { ok: false, failedSlot: number, reason: string, seed, difficulty, count }
//
// Pure function of (seed, difficulty, count): every random decision is
// drawn from seed.derive(i)'s stream, so identical inputs always produce
// an identical result.
export function generateBatch(seed, difficulty, count) {
  const puzzles = [];

  for (let i = 0; i < count; i++) {
    const slotSeed = seed.derive(i);
    const slotResult = generateSlot(slotSeed, difficulty);

    if (!slotResult.ok) {
      return {
        ok: false,
        failedSlot: i,
        reason: slotResult.reason,
        seed,
        difficulty,
        count,
      };
    }

    puzzles.push(slotResult.puzzle);
  }

  return { ok: true, batch: new PuzzleBatch(seed, difficulty, count, puzzles) };
}

// Produces one Puzzle satisfying `difficulty`, or a failure value, using
// only randomness derived from slotSeed. Retries a bounded number of
// times with fresh derived attempt-seeds (a fresh full grid + a fresh
// removal order each time) before giving up.
function generateSlot(slotSeed, difficulty) {
  let lastReason = 'no attempts made';

  for (let attempt = 0; attempt < MAX_ATTEMPTS_PER_SLOT; attempt++) {
    const attemptSeed = slotSeed.derive(attempt);
    const stream = attemptSeed.stream();

    const fullGrid = fillFullGrid(stream);
    const dug = digToDifficulty(fullGrid, difficulty, stream);

    if (dug.ok) return dug;
    lastReason = dug.reason;
  }

  return { ok: false, reason: `exhausted ${MAX_ATTEMPTS_PER_SLOT} attempts: ${lastReason}` };
}

// Randomized backtracking fill: builds one fully-solved, legal Grid.
// Cells are visited in row-major order; the candidate VALUE order at
// each cell is shuffled from `stream`, which is what makes the resulting
// solution vary by seed while remaining a legal, complete Sudoku grid.
function fillFullGrid(stream) {
  let grid = Grid.empty();

  function backtrack(idx) {
    if (idx === CELL_COUNT) return true;

    const pos = idx;
    const values = shuffledDigits(stream);

    for (const value of values) {
      if (grid.canPlace(pos, value)) {
        const prior = grid;
        grid = grid.withCell(pos, value);
        if (backtrack(idx + 1)) return true;
        grid = prior;
      }
    }

    return false;
  }

  const solved = backtrack(0);
  if (!solved) {
    // Should not happen for a standard 9x9 grid with randomized
    // backtracking from empty, but fail loudly rather than silently
    // returning a partial/illegal grid if it ever does.
    throw new Error('fillFullGrid: failed to produce a full solved grid');
  }

  return grid;
}

function shuffledDigits(stream) {
  const values = [1, 2, 3, 4, 5, 6, 7, 8, 9];
  for (let i = values.length - 1; i > 0; i--) {
    const j = Math.floor(stream.next() * (i + 1));
    [values[i], values[j]] = [values[j], values[i]];
  }
  return values;
}

function shuffledPositions(stream) {
  const positions = Array.from({ length: CELL_COUNT }, (_, i) => i);
  for (let i = positions.length - 1; i > 0; i--) {
    const j = Math.floor(stream.next() * (i + 1));
    [positions[i], positions[j]] = [positions[j], positions[i]];
  }
  return positions;
}

// Removes givens from `fullGrid` in a seeded-random order, accepting each
// removal only if the resulting grid is still uniquely solvable (checked
// via the same Solver.countSolutions(candidate, 2) call Puzzle.tryCreate
// uses) AND removing wouldn't drop the given-count below a target picked
// (from `stream`, so still deterministic) uniformly within the
// difficulty's band. Picking a per-attempt target rather than always
// digging to the band's floor spreads resulting given-counts across the
// whole band instead of every puzzle landing on the same edge value.
// Stops once the target is reached or the shuffled order is exhausted
// (i.e. digging got stuck above the target because no remaining cell
// could be safely removed).
//
// Returns { ok: true, puzzle } or { ok: false, reason }.
function digToDifficulty(fullGrid, difficulty, stream) {
  const bandWidth = difficulty.max - difficulty.min + 1;
  const target = difficulty.min + Math.floor(stream.next() * bandWidth);

  let givens = fullGrid;
  const order = shuffledPositions(stream);

  for (const pos of order) {
    const currentGivenCount = givens.givenCount();
    if (currentGivenCount <= target) break; // reached this attempt's target

    if (givens.cellAt(pos) === 0) continue; // already removed

    const candidate = givens.withCell(pos, 0);
    const { count } = countSolutions(candidate, 2);
    if (count === 1) {
      givens = candidate;
    }
    // count !== 1: removing this cell would break uniqueness; skip it
    // and try the next cell in the shuffled order.
  }

  const finalCount = givens.givenCount();
  if (finalCount < difficulty.min || finalCount > difficulty.max) {
    return {
      ok: false,
      reason: `stuck at ${finalCount} givens, outside [${difficulty.min}, ${difficulty.max}] band for ${difficulty.name}`,
    };
  }

  const created = Puzzle.tryCreate(givens);
  if (!created.ok) {
    // Should not happen -- digging only ever accepted removals the
    // solver already confirmed left exactly one solution -- but if it
    // ever did, this is a failure value, not a mislabeled puzzle.
    return { ok: false, reason: `Puzzle.tryCreate rejected final givens: ${created.reason}` };
  }

  return { ok: true, puzzle: created.puzzle };
}
