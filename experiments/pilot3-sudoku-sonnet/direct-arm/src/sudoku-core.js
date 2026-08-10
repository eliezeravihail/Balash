/**
 * Core Sudoku generation engine.
 *
 * Everything a puzzle batch needs lives here: building a valid solved
 * grid, counting how many solutions a board has, a light "human
 * technique" solver used to grade difficulty, and the hole-digging
 * routine that turns a full grid into a puzzle with a guaranteed
 * unique solution.
 *
 * Pure logic, no DOM - runs identically in the browser and in Node
 * (see tests/), which is what makes the generator testable headlessly.
 *
 * Board representation: a flat array of 81 numbers, row-major
 * (index = row * 9 + col), 0 meaning "empty".
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory(require("./rng.js"));
  } else {
    root.SudokuCore = factory(root.SudokuRng);
  }
})(typeof self !== "undefined" ? self : this, function (SudokuRng) {
  "use strict";

  const SIZE = 9;
  const BOX = 3;
  const CELL_COUNT = SIZE * SIZE;
  const ALL_DIGITS_MASK = 0b111111111; // digits 1-9 as bits 0-8

  // ---------------------------------------------------------------------
  // Small board utilities
  // ---------------------------------------------------------------------

  function boxOf(r, c) {
    return Math.floor(r / BOX) * BOX + Math.floor(c / BOX);
  }

  function rowOf(i) {
    return (i / SIZE) | 0;
  }
  function colOf(i) {
    return i % SIZE;
  }

  function bitFor(digit) {
    return 1 << (digit - 1);
  }
  function digitFor(bit) {
    return 32 - Math.clz32(bit);
  }

  function popcount(x) {
    x = x - ((x >> 1) & 0x55555555);
    x = (x & 0x33333333) + ((x >> 2) & 0x33333333);
    x = (x + (x >> 4)) & 0x0f0f0f0f;
    return (x * 0x01010101) >> 24;
  }

  // Precompute the 27 units (9 rows, 9 cols, 9 boxes) as arrays of cell indices.
  const UNITS = (function buildUnits() {
    const units = [];
    for (let r = 0; r < SIZE; r++) {
      const cells = [];
      for (let c = 0; c < SIZE; c++) cells.push(r * SIZE + c);
      units.push(cells);
    }
    for (let c = 0; c < SIZE; c++) {
      const cells = [];
      for (let r = 0; r < SIZE; r++) cells.push(r * SIZE + c);
      units.push(cells);
    }
    for (let b = 0; b < SIZE; b++) {
      const br = Math.floor(b / BOX) * BOX;
      const bc = (b % BOX) * BOX;
      const cells = [];
      for (let dr = 0; dr < BOX; dr++)
        for (let dc = 0; dc < BOX; dc++)
          cells.push((br + dr) * SIZE + (bc + dc));
      units.push(cells);
    }
    return units;
  })();

  function flatten(grid) {
    const flat = new Array(CELL_COUNT);
    for (let r = 0; r < SIZE; r++)
      for (let c = 0; c < SIZE; c++) flat[r * SIZE + c] = grid[r][c];
    return flat;
  }

  function toGrid(flat) {
    const grid = [];
    for (let r = 0; r < SIZE; r++) grid.push(flat.slice(r * SIZE, r * SIZE + SIZE));
    return grid;
  }

  function countGivens(flat) {
    let n = 0;
    for (let i = 0; i < CELL_COUNT; i++) if (flat[i] !== 0) n++;
    return n;
  }

  // ---------------------------------------------------------------------
  // 1. Build a random, fully-solved, valid grid.
  //
  // Classic technique: start from a fixed base Latin-square pattern that
  // is guaranteed to satisfy every Sudoku constraint, then apply a
  // sequence of symmetry-preserving transformations - permuting rows
  // within a band, bands amongst themselves, likewise for columns, and
  // relabeling digits. Every one of these transformations preserves
  // validity, so the result is guaranteed to be a valid complete grid
  // with no search or backtracking required.
  // ---------------------------------------------------------------------

  function generateFullGrid(rng) {
    const pattern = (r, c) => (BOX * (r % BOX) + Math.floor(r / BOX) + c) % SIZE;

    const bandOrder = rng.shuffle([0, 1, 2]);
    const rows = [];
    for (const band of bandOrder) {
      const within = rng.shuffle([0, 1, 2]);
      for (const off of within) rows.push(band * BOX + off);
    }

    const stackOrder = rng.shuffle([0, 1, 2]);
    const cols = [];
    for (const stack of stackOrder) {
      const within = rng.shuffle([0, 1, 2]);
      for (const off of within) cols.push(stack * BOX + off);
    }

    const digits = rng.shuffle([1, 2, 3, 4, 5, 6, 7, 8, 9]);

    const flat = new Array(CELL_COUNT);
    for (let r = 0; r < SIZE; r++) {
      for (let c = 0; c < SIZE; c++) {
        flat[r * SIZE + c] = digits[pattern(rows[r], cols[c])];
      }
    }
    return flat;
  }

  // ---------------------------------------------------------------------
  // 2. Exact solution counter (capped) - this is what GUARANTEES
  //    uniqueness. Backtracking search with MRV (minimum-remaining-
  //    values) cell selection via bitmask candidates, stopping as soon
  //    as `limit` solutions have been found (we only ever need to know
  //    "is it 0, 1, or 2+").
  // ---------------------------------------------------------------------

  function countSolutions(inputFlat, limit) {
    limit = limit || 2;
    const board = inputFlat.slice();
    const rowMask = new Array(SIZE).fill(0);
    const colMask = new Array(SIZE).fill(0);
    const boxMask = new Array(SIZE).fill(0);

    for (let i = 0; i < CELL_COUNT; i++) {
      const v = board[i];
      if (v) {
        const r = rowOf(i), c = colOf(i), b = boxOf(r, c);
        const bit = bitFor(v);
        // A given that repeats within its own row/col/box makes the
        // board unsolvable outright - report 0 solutions rather than
        // silently ignoring the conflict.
        if (rowMask[r] & bit || colMask[c] & bit || boxMask[b] & bit) return 0;
        rowMask[r] |= bit;
        colMask[c] |= bit;
        boxMask[b] |= bit;
      }
    }

    let solutions = 0;

    function search() {
      if (solutions >= limit) return;

      // Find the empty cell with the fewest legal candidates (MRV).
      let bestI = -1, bestCands = 0, bestCount = 10;
      for (let i = 0; i < CELL_COUNT; i++) {
        if (board[i] !== 0) continue;
        const r = rowOf(i), c = colOf(i), b = boxOf(r, c);
        const used = rowMask[r] | colMask[c] | boxMask[b];
        const cands = ALL_DIGITS_MASK & ~used;
        if (cands === 0) return; // dead end, no legal digit here
        const cnt = popcount(cands);
        if (cnt < bestCount) {
          bestCount = cnt;
          bestI = i;
          bestCands = cands;
          if (cnt === 1) break; // can't do better than a forced cell
        }
      }

      if (bestI === -1) {
        // No empty cells left: a complete, valid solution.
        solutions++;
        return;
      }

      const r = rowOf(bestI), c = colOf(bestI), b = boxOf(r, c);
      let cands = bestCands;
      while (cands) {
        const bit = cands & -cands;
        cands ^= bit;
        board[bestI] = digitFor(bit);
        rowMask[r] |= bit;
        colMask[c] |= bit;
        boxMask[b] |= bit;

        search();

        rowMask[r] ^= bit;
        colMask[c] ^= bit;
        boxMask[b] ^= bit;
        board[bestI] = 0;

        if (solutions >= limit) return;
      }
    }

    search();
    return solutions;
  }

  function hasUniqueSolution(flat) {
    return countSolutions(flat, 2) === 1;
  }

  // Solve a board that is known/assumed to have a unique solution, and
  // return the filled grid (used for sanity checks / tests, not needed
  // by generation itself since we already know the full solution).
  function solveUnique(flat) {
    const board = flat.slice();
    const rowMask = new Array(SIZE).fill(0);
    const colMask = new Array(SIZE).fill(0);
    const boxMask = new Array(SIZE).fill(0);
    for (let i = 0; i < CELL_COUNT; i++) {
      const v = board[i];
      if (v) {
        const r = rowOf(i), c = colOf(i), b = boxOf(r, c);
        rowMask[r] |= bitFor(v);
        colMask[c] |= bitFor(v);
        boxMask[b] |= bitFor(v);
      }
    }
    let solved = null;
    function search() {
      if (solved) return;
      let bestI = -1, bestCands = 0, bestCount = 10;
      for (let i = 0; i < CELL_COUNT; i++) {
        if (board[i] !== 0) continue;
        const r = rowOf(i), c = colOf(i), b = boxOf(r, c);
        const cands = ALL_DIGITS_MASK & ~(rowMask[r] | colMask[c] | boxMask[b]);
        if (cands === 0) return;
        const cnt = popcount(cands);
        if (cnt < bestCount) {
          bestCount = cnt;
          bestI = i;
          bestCands = cands;
          if (cnt === 1) break;
        }
      }
      if (bestI === -1) {
        solved = board.slice();
        return;
      }
      const r = rowOf(bestI), c = colOf(bestI), b = boxOf(r, c);
      let cands = bestCands;
      while (cands && !solved) {
        const bit = cands & -cands;
        cands ^= bit;
        board[bestI] = digitFor(bit);
        rowMask[r] |= bit;
        colMask[c] |= bit;
        boxMask[b] |= bit;
        search();
        rowMask[r] ^= bit;
        colMask[c] ^= bit;
        boxMask[b] ^= bit;
        board[bestI] = 0;
      }
    }
    search();
    return solved;
  }

  // ---------------------------------------------------------------------
  // 3. "Human technique" logical solver, used purely to grade how hard
  //    a puzzle is to solve by logic alone (not used to prove
  //    uniqueness - countSolutions already guarantees that).
  //
  //    Technique tiers:
  //      1 = naked singles / hidden singles only
  //      2 = also needs locked candidates (pointing/claiming) and/or
  //          naked pairs
  //      3 = logic above stalls out; a solver would need to guess and
  //          backtrack (this is what makes a puzzle feel "hard")
  // ---------------------------------------------------------------------

  function rateLogicalDifficulty(inputFlat) {
    const board = inputFlat.slice();
    const cand = new Array(CELL_COUNT).fill(0);

    function recomputeAllCandidates() {
      const rowMask = new Array(SIZE).fill(0);
      const colMask = new Array(SIZE).fill(0);
      const boxMask = new Array(SIZE).fill(0);
      for (let i = 0; i < CELL_COUNT; i++) {
        const v = board[i];
        if (v) {
          const r = rowOf(i), c = colOf(i), b = boxOf(r, c);
          rowMask[r] |= bitFor(v);
          colMask[c] |= bitFor(v);
          boxMask[b] |= bitFor(v);
        }
      }
      for (let i = 0; i < CELL_COUNT; i++) {
        if (board[i]) {
          cand[i] = 0;
        } else {
          const r = rowOf(i), c = colOf(i), b = boxOf(r, c);
          cand[i] = ALL_DIGITS_MASK & ~(rowMask[r] | colMask[c] | boxMask[b]);
        }
      }
    }

    function assign(i, digit) {
      board[i] = digit;
      cand[i] = 0;
      const r = rowOf(i), c = colOf(i), b = boxOf(r, c);
      const bit = bitFor(digit);
      for (const idx of UNITS[r]) cand[idx] &= ~bit;
      for (const idx of UNITS[SIZE + c]) cand[idx] &= ~bit;
      for (const idx of UNITS[2 * SIZE + b]) cand[idx] &= ~bit;
      cand[i] = 0;
    }

    function tryNakedSingles() {
      let progressed = false;
      for (let i = 0; i < CELL_COUNT; i++) {
        if (board[i] === 0 && popcount(cand[i]) === 1) {
          assign(i, digitFor(cand[i]));
          progressed = true;
        }
      }
      return progressed;
    }

    function tryHiddenSingles() {
      let progressed = false;
      for (const unit of UNITS) {
        for (let d = 1; d <= 9; d++) {
          const bit = bitFor(d);
          let found = -1, count = 0;
          for (const idx of unit) {
            if (board[idx] === 0 && (cand[idx] & bit)) {
              count++;
              found = idx;
              if (count > 1) break;
            }
          }
          if (count === 1) {
            assign(found, d);
            progressed = true;
          }
        }
      }
      return progressed;
    }

    // Pointing (box -> line) and claiming (line -> box) eliminations.
    function tryLockedCandidates() {
      let eliminated = false;
      const boxUnits = UNITS.slice(2 * SIZE, 3 * SIZE);
      const rowUnits = UNITS.slice(0, SIZE);
      const colUnits = UNITS.slice(SIZE, 2 * SIZE);

      // Pointing: within a box, if all candidates for digit d lie in one row/col,
      // eliminate d from the rest of that row/col outside the box.
      for (const box of boxUnits) {
        for (let d = 1; d <= 9; d++) {
          const bit = bitFor(d);
          const cells = box.filter((idx) => board[idx] === 0 && (cand[idx] & bit));
          if (cells.length === 0) continue;
          const rows = new Set(cells.map(rowOf));
          const cols = new Set(cells.map(colOf));
          if (rows.size === 1) {
            const r = [...rows][0];
            for (const idx of UNITS[r]) {
              if (!box.includes(idx) && (cand[idx] & bit)) {
                cand[idx] &= ~bit;
                eliminated = true;
              }
            }
          }
          if (cols.size === 1) {
            const c = [...cols][0];
            for (const idx of UNITS[SIZE + c]) {
              if (!box.includes(idx) && (cand[idx] & bit)) {
                cand[idx] &= ~bit;
                eliminated = true;
              }
            }
          }
        }
      }

      // Claiming: within a row/col, if all candidates for digit d lie in one box,
      // eliminate d from the rest of that box outside the row/col.
      for (const line of rowUnits.concat(colUnits)) {
        for (let d = 1; d <= 9; d++) {
          const bit = bitFor(d);
          const cells = line.filter((idx) => board[idx] === 0 && (cand[idx] & bit));
          if (cells.length === 0) continue;
          const boxes = new Set(cells.map((idx) => boxOf(rowOf(idx), colOf(idx))));
          if (boxes.size === 1) {
            const b = [...boxes][0];
            for (const idx of UNITS[2 * SIZE + b]) {
              if (!line.includes(idx) && (cand[idx] & bit)) {
                cand[idx] &= ~bit;
                eliminated = true;
              }
            }
          }
        }
      }

      return eliminated;
    }

    // Naked pairs: two cells in a unit share the exact same 2 candidates ->
    // those two digits can be eliminated from every other cell in the unit.
    function tryNakedPairs() {
      let eliminated = false;
      for (const unit of UNITS) {
        const pairCells = unit.filter((idx) => board[idx] === 0 && popcount(cand[idx]) === 2);
        for (let a = 0; a < pairCells.length; a++) {
          for (let bIdx = a + 1; bIdx < pairCells.length; bIdx++) {
            const i1 = pairCells[a], i2 = pairCells[bIdx];
            if (cand[i1] !== cand[i2]) continue;
            const mask = cand[i1];
            for (const idx of unit) {
              if (idx !== i1 && idx !== i2 && board[idx] === 0 && (cand[idx] & mask)) {
                cand[idx] &= ~mask;
                eliminated = true;
              }
            }
          }
        }
      }
      return eliminated;
    }

    recomputeAllCandidates();
    let tier = 0;
    for (let guard = 0; guard < 200; guard++) {
      if (countGivens(board) === CELL_COUNT) break;

      if (tryNakedSingles() || tryHiddenSingles()) {
        tier = Math.max(tier, 1);
        continue;
      }
      if (tryLockedCandidates() || tryNakedPairs()) {
        tier = Math.max(tier, 2);
        continue;
      }
      break; // stuck: would require search/guessing
    }

    const solved = countGivens(board) === CELL_COUNT;
    return { solved, level: solved ? Math.max(tier, 1) : 3 };
  }

  // ---------------------------------------------------------------------
  // 4. Difficulty presets and the hole-digging generator.
  //
  //    Digging removes givens one (symmetric pair of) cell(s) at a time,
  //    in an order shuffled by the seeded RNG. A removal is only kept if
  //    the resulting board STILL has exactly one solution (checked with
  //    countSolutions, limit 2) - this is what guarantees every puzzle
  //    that ships has exactly one solution. Difficulty is controlled by
  //    (a) the target number of givens and (b) an optional cap on the
  //    logical technique level required to fully solve the puzzle.
  // ---------------------------------------------------------------------

  const DIFFICULTIES = {
    easy: {
      label: "Easy",
      targetGivens: 40,
      minGivens: 34,
      maxTechniqueLevel: 1, // naked/hidden singles only
      jitter: 2,
    },
    medium: {
      label: "Medium",
      targetGivens: 32,
      minGivens: 28,
      maxTechniqueLevel: 2, // + locked candidates / naked pairs
      jitter: 2,
    },
    hard: {
      label: "Hard",
      targetGivens: 25,
      minGivens: 22,
      maxTechniqueLevel: null, // unrestricted: may require search
      jitter: 2,
    },
  };

  function digPuzzle(fullFlat, rng, options) {
    const board = fullFlat.slice();
    const { targetGivens, minGivens, maxTechniqueLevel } = options;
    let givens = CELL_COUNT;

    function tryRemove(toRemove) {
      if (givens <= targetGivens) return false;
      if (toRemove.some((i) => board[i] === 0)) return false;
      if (givens - toRemove.length < minGivens) return false;

      const backup = toRemove.map((i) => board[i]);
      toRemove.forEach((i) => (board[i] = 0));

      let keep = countSolutions(board, 2) === 1;
      if (keep && maxTechniqueLevel != null) {
        keep = rateLogicalDifficulty(board).level <= maxTechniqueLevel;
      }

      if (keep) {
        givens -= toRemove.length;
        return true;
      }
      toRemove.forEach((i, k) => (board[i] = backup[k]));
      return false;
    }

    // Pass 1: remove cells in 180-degree-symmetric pairs, for a
    // classic-looking puzzle layout.
    const symmetricPositions = rng.shuffle(Array.from({ length: CELL_COUNT }, (_, i) => i));
    for (const idx of symmetricPositions) {
      if (givens <= targetGivens) break;
      const partner = CELL_COUNT - 1 - idx;
      tryRemove(partner !== idx ? [idx, partner] : [idx]);
    }

    // Pass 2: symmetric digging can plateau before reaching the target
    // (removing a cell's mirror partner may break uniqueness even when
    // the cell alone would not). Fall back to single-cell removals so
    // harder difficulties still reliably reach their target given count.
    if (givens > targetGivens) {
      const singlePositions = rng.shuffle(Array.from({ length: CELL_COUNT }, (_, i) => i));
      for (const idx of singlePositions) {
        if (givens <= targetGivens) break;
        tryRemove([idx]);
      }
    }

    return board;
  }

  /**
   * Generate a deterministic batch of puzzles.
   *
   * The same {seed, difficulty, count} always produces the same batch,
   * because a single RNG stream is created from `seed` and consumed in
   * a fixed order as each puzzle is built.
   */
  function generateBatch({ seed, difficulty, count }) {
    if (!DIFFICULTIES[difficulty]) {
      throw new Error(`Unknown difficulty: ${difficulty}`);
    }
    const config = DIFFICULTIES[difficulty];
    const rng = SudokuRng.createRng(seed);
    const puzzles = [];

    for (let i = 0; i < count; i++) {
      const solutionFlat = generateFullGrid(rng);
      const jitter = config.jitter || 0;
      const jitterAmount = jitter ? rng.nextInt(jitter * 2 + 1) - jitter : 0;
      const targetGivens = Math.max(config.targetGivens + jitterAmount, config.minGivens);

      const puzzleFlat = digPuzzle(solutionFlat, rng, {
        targetGivens,
        minGivens: config.minGivens,
        maxTechniqueLevel: config.maxTechniqueLevel,
      });

      puzzles.push({
        index: i,
        givens: countGivens(puzzleFlat),
        puzzle: toGrid(puzzleFlat),
        solution: toGrid(solutionFlat),
      });
    }

    return { seed: String(seed), difficulty, count, puzzles };
  }

  return {
    SIZE,
    DIFFICULTIES,
    flatten,
    toGrid,
    countGivens,
    generateFullGrid,
    countSolutions,
    hasUniqueSolution,
    solveUnique,
    rateLogicalDifficulty,
    digPuzzle,
    generateBatch,
  };
});
