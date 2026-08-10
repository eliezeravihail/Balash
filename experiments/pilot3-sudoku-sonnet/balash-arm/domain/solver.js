// domain/solver.js
//
// The ONLY place in the codebase that answers "how many solutions does
// this Grid have." Pure function, no state, no randomness. Backtracking
// search that stops as soon as it has found `limit` solutions -- callers
// only ever need "exactly one" vs "more than one," never the true count,
// so `limit` is always 2 in practice. This bounds worst-case search cost
// and is what makes uniqueness-checking during digging cheap enough to
// run 80+ times per candidate puzzle.
//
// Uses a minimum-remaining-values (MRV) cell-selection heuristic purely
// for search-speed; it does not affect correctness or introduce any
// randomness (candidate cells/values are always considered in a fixed
// deterministic order).

import { CELL_COUNT } from './grid.js';

// Returns { count, solution }:
//   count    -- number of solutions found, capped at `limit`.
//   solution -- the first full solution found (a Grid), or null if count === 0.
export function countSolutions(grid, limit) {
  if (limit < 1) throw new Error('countSolutions requires limit >= 1');

  let count = 0;
  let solution = null;

  function search(g) {
    if (count >= limit) return;

    const pos = pickMRVCell(g);
    if (pos === -1) {
      // No empty cells left. Every placement made on the way here passed
      // canPlace, so this is necessarily a legal, complete solution.
      count++;
      if (solution === null) solution = g;
      return;
    }

    for (let value = 1; value <= 9; value++) {
      if (count >= limit) return;
      if (g.canPlace(pos, value)) {
        search(g.withCell(pos, value));
      }
    }
  }

  search(grid);
  return { count, solution };
}

// Picks the empty cell with the fewest legal candidate values (ties broken
// by lowest position index, i.e. row-major). Returns -1 if the grid has no
// empty cells. A cell with zero candidates is returned immediately since
// nothing beats "definitely a dead end" for pruning.
function pickMRVCell(grid) {
  let bestPos = -1;
  let bestCount = 10; // > max possible (9)

  for (let pos = 0; pos < CELL_COUNT; pos++) {
    if (grid.cellAt(pos) !== 0) continue;

    let candidates = 0;
    for (let value = 1; value <= 9; value++) {
      if (grid.canPlace(pos, value)) candidates++;
    }

    if (candidates === 0) return pos; // dead end, no point searching further
    if (candidates < bestCount) {
      bestCount = candidates;
      bestPos = pos;
    }
  }

  return bestPos;
}
