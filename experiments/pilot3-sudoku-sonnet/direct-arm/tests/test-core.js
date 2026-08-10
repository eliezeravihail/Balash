/**
 * Headless test suite for the Sudoku generation engine.
 *
 * Run with: node tests/test-core.js
 * (or `npm test`, see package.json)
 *
 * No test framework - plain Node `assert`, a tiny `test()` runner
 * below, and a non-zero exit code on failure so it plugs into CI
 * easily.
 */
"use strict";

const assert = require("assert");
const path = require("path");
const core = require(path.join(__dirname, "..", "src", "sudoku-core.js"));
const { createRng } = require(path.join(__dirname, "..", "src", "rng.js"));

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`  ok - ${name}`);
  } catch (err) {
    failed++;
    console.error(`  FAIL - ${name}`);
    console.error(`         ${err.message}`);
  }
}

function isValidCompleteGrid(flat) {
  const unitOk = (cells) => {
    const seen = new Set();
    for (const v of cells) {
      if (v < 1 || v > 9) return false;
      if (seen.has(v)) return false;
      seen.add(v);
    }
    return seen.size === 9;
  };
  for (let r = 0; r < 9; r++) {
    if (!unitOk(Array.from({ length: 9 }, (_, c) => flat[r * 9 + c]))) return false;
  }
  for (let c = 0; c < 9; c++) {
    if (!unitOk(Array.from({ length: 9 }, (_, r) => flat[r * 9 + c]))) return false;
  }
  for (let br = 0; br < 3; br++) {
    for (let bc = 0; bc < 3; bc++) {
      const cells = [];
      for (let dr = 0; dr < 3; dr++)
        for (let dc = 0; dc < 3; dc++)
          cells.push(flat[(br * 3 + dr) * 9 + (bc * 3 + dc)]);
      if (!unitOk(cells)) return false;
    }
  }
  return true;
}

function puzzleMatchesSolutionOnGivens(puzzleFlat, solutionFlat) {
  for (let i = 0; i < 81; i++) {
    if (puzzleFlat[i] !== 0 && puzzleFlat[i] !== solutionFlat[i]) return false;
  }
  return true;
}

console.log("RNG determinism");
test("same seed produces identical number stream", () => {
  const a = createRng("seed-123");
  const b = createRng("seed-123");
  const seqA = Array.from({ length: 20 }, () => a.next());
  const seqB = Array.from({ length: 20 }, () => b.next());
  assert.deepStrictEqual(seqA, seqB);
});

test("different seeds produce different streams", () => {
  const a = createRng("seed-123");
  const b = createRng("seed-124");
  assert.notStrictEqual(a.next(), b.next());
});

test("shuffle is deterministic for a given seed", () => {
  const a = createRng("shuffle-seed").shuffle([1, 2, 3, 4, 5, 6, 7, 8, 9]);
  const b = createRng("shuffle-seed").shuffle([1, 2, 3, 4, 5, 6, 7, 8, 9]);
  assert.deepStrictEqual(a, b);
});

console.log("\nFull grid generation");
test("generateFullGrid produces a valid complete grid", () => {
  const rng = createRng("full-grid-seed");
  const grid = core.generateFullGrid(rng);
  assert.strictEqual(grid.length, 81);
  assert.ok(isValidCompleteGrid(grid), "grid violates Sudoku constraints");
});

test("generateFullGrid varies with seed", () => {
  const g1 = core.generateFullGrid(createRng("grid-a"));
  const g2 = core.generateFullGrid(createRng("grid-b"));
  assert.notDeepStrictEqual(g1, g2);
});

console.log("\nSolution counter");
test("a solved grid counts as exactly 1 solution", () => {
  const grid = core.generateFullGrid(createRng("counter-seed"));
  assert.strictEqual(core.countSolutions(grid, 5), 1);
});

test("an empty board has many solutions (capped by limit)", () => {
  const empty = new Array(81).fill(0);
  assert.strictEqual(core.countSolutions(empty, 2), 2);
});

test("a board with a duplicate digit in a row has 0 solutions", () => {
  const grid = core.generateFullGrid(createRng("dup-seed"));
  grid[1] = grid[0]; // duplicate within row 0
  assert.strictEqual(core.countSolutions(grid, 2), 0);
});

console.log("\nBatch generation: uniqueness and correctness (the core guarantee)");
const seeds = ["alpha", "bravo-42", "charlie-seed", "delta-9000", "echo"];
const difficulties = ["easy", "medium", "hard"];

for (const difficulty of difficulties) {
  for (const seed of seeds) {
    test(`[${difficulty}] seed="${seed}" batch of 3: every puzzle has exactly one solution`, () => {
      const batch = core.generateBatch({ seed, difficulty, count: 3 });
      assert.strictEqual(batch.puzzles.length, 3);
      for (const p of batch.puzzles) {
        const flat = core.flatten(p.puzzle);
        const solCount = core.countSolutions(flat, 2);
        assert.strictEqual(
          solCount,
          1,
          `puzzle ${p.index} (${difficulty}, seed=${seed}) has ${solCount} solutions, expected 1`
        );
      }
    });
  }
}

test("puzzle givens are a subset consistent with the stored solution", () => {
  const batch = core.generateBatch({ seed: "consistency-seed", difficulty: "medium", count: 2 });
  for (const p of batch.puzzles) {
    const puzzleFlat = core.flatten(p.puzzle);
    const solutionFlat = core.flatten(p.solution);
    assert.ok(isValidCompleteGrid(solutionFlat), "stored solution is not a valid complete grid");
    assert.ok(
      puzzleMatchesSolutionOnGivens(puzzleFlat, solutionFlat),
      "puzzle givens disagree with stored solution"
    );
  }
});

test("solving the puzzle independently reproduces the stored solution", () => {
  const batch = core.generateBatch({ seed: "solve-check-seed", difficulty: "hard", count: 2 });
  for (const p of batch.puzzles) {
    const puzzleFlat = core.flatten(p.puzzle);
    const solved = core.solveUnique(puzzleFlat);
    assert.deepStrictEqual(solved, core.flatten(p.solution));
  }
});

console.log("\nDifficulty behaves as documented");
test("easy puzzles have more givens than medium, which has more than hard", () => {
  const avgGivens = (difficulty) => {
    const batch = core.generateBatch({ seed: "difficulty-order-seed", difficulty, count: 5 });
    return batch.puzzles.reduce((sum, p) => sum + p.givens, 0) / batch.puzzles.length;
  };
  const easyAvg = avgGivens("easy");
  const mediumAvg = avgGivens("medium");
  const hardAvg = avgGivens("hard");
  assert.ok(easyAvg > mediumAvg, `expected easy (${easyAvg}) > medium (${mediumAvg})`);
  assert.ok(mediumAvg > hardAvg, `expected medium (${mediumAvg}) > hard (${hardAvg})`);
});

test("easy puzzles are solvable using only naked/hidden singles", () => {
  const batch = core.generateBatch({ seed: "easy-technique-seed", difficulty: "easy", count: 4 });
  for (const p of batch.puzzles) {
    const rating = core.rateLogicalDifficulty(core.flatten(p.puzzle));
    assert.ok(rating.solved, "easy puzzle was not fully solved by the logical solver");
    assert.strictEqual(rating.level, 1, `expected technique level 1, got ${rating.level}`);
  }
});

test("medium puzzles never require deeper than locked candidates / pairs", () => {
  const batch = core.generateBatch({ seed: "medium-technique-seed", difficulty: "medium", count: 4 });
  for (const p of batch.puzzles) {
    const rating = core.rateLogicalDifficulty(core.flatten(p.puzzle));
    assert.ok(rating.solved, "medium puzzle was not fully solved by the logical solver");
    assert.ok(rating.level <= 2, `expected technique level <= 2, got ${rating.level}`);
  }
});

test("all difficulties respect the configured minimum givens floor", () => {
  for (const difficulty of difficulties) {
    const batch = core.generateBatch({ seed: "floor-seed", difficulty, count: 3 });
    const min = core.DIFFICULTIES[difficulty].minGivens;
    for (const p of batch.puzzles) {
      assert.ok(p.givens >= min, `${difficulty} puzzle has ${p.givens} givens, below floor ${min}`);
    }
  }
});

console.log("\nReproducibility (the seed contract)");
test("same seed + difficulty + count reproduces an identical batch", () => {
  const a = core.generateBatch({ seed: "share-me-2026", difficulty: "medium", count: 6 });
  const b = core.generateBatch({ seed: "share-me-2026", difficulty: "medium", count: 6 });
  assert.deepStrictEqual(a.puzzles, b.puzzles);
});

test("different seeds produce different batches", () => {
  const a = core.generateBatch({ seed: "seed-one", difficulty: "medium", count: 3 });
  const b = core.generateBatch({ seed: "seed-two", difficulty: "medium", count: 3 });
  assert.notDeepStrictEqual(a.puzzles, b.puzzles);
});

test("different difficulty with the same seed produces different puzzles", () => {
  const a = core.generateBatch({ seed: "same-seed", difficulty: "easy", count: 2 });
  const b = core.generateBatch({ seed: "same-seed", difficulty: "hard", count: 2 });
  assert.notDeepStrictEqual(a.puzzles, b.puzzles);
});

test("requesting more puzzles just extends the same deterministic stream (prefix stable)", () => {
  const small = core.generateBatch({ seed: "prefix-seed", difficulty: "medium", count: 2 });
  const large = core.generateBatch({ seed: "prefix-seed", difficulty: "medium", count: 5 });
  assert.deepStrictEqual(small.puzzles, large.puzzles.slice(0, 2));
});

console.log(`\n${passed} passed, ${failed} failed`);
if (failed > 0) process.exit(1);
