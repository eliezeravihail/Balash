// domain/puzzle.js
//
// Puzzle: Givens (a partially-filled Grid) paired with its Solution (a
// fully-filled Grid). The one-solution invariant lives HERE, at
// construction time, and nowhere else in the codebase.
//
// Puzzle.tryCreate(givensGrid) is the ONLY way to obtain a Puzzle. It
// calls Solver.countSolutions(givens, 2) internally; if the count isn't
// exactly 1 it returns a NotUnique-style failure value instead of a
// Puzzle. There is no other constructor and no setter that mutates
// givens after creation.
//
// Consequence: if you're holding a Puzzle object, uniqueness is a fact,
// not a hope -- nothing downstream (generator's own bookkeeping aside,
// renderer, batch, print view) ever re-checks it.

import { countSolutions } from './solver.js';

// Module-private guard so `new Puzzle(...)` cannot be called from outside
// this file with a fabricated pair of grids. JS has no true "private
// constructor," so this symbol is the enforcement mechanism: only code
// inside this module can produce it.
const CREATE_GUARD = Symbol('puzzle-create-guard');

export class Puzzle {
  #givens;
  #solution;

  constructor(guard, givens, solution) {
    if (guard !== CREATE_GUARD) {
      throw new Error('Puzzle cannot be constructed directly; use Puzzle.tryCreate(givens)');
    }
    this.#givens = givens;
    this.#solution = solution;
  }

  // Returns { ok: true, puzzle } if `givens` has exactly one solution,
  // otherwise { ok: false, reason, count }. `reason` is one of:
  //   'no-solution'  -- count === 0
  //   'not-unique'   -- count >= 2
  static tryCreate(givens) {
    const { count, solution } = countSolutions(givens, 2);
    if (count !== 1) {
      return { ok: false, reason: count === 0 ? 'no-solution' : 'not-unique', count };
    }
    return { ok: true, puzzle: new Puzzle(CREATE_GUARD, givens, solution) };
  }

  givens() {
    return this.#givens;
  }

  solution() {
    return this.#solution;
  }

  givenCount() {
    return this.#givens.givenCount();
  }
}
