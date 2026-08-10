// test/domain.test.js
//
// Headless, Node-only tests of the pure core (domain/). No DOM, no
// bundler, no third-party test framework -- uses Node's built-in test
// runner and assert module exclusively. Run with:
//   node --test test/
// or
//   npm test

import test from 'node:test';
import assert from 'node:assert/strict';

import { Grid } from '../domain/grid.js';
import { countSolutions } from '../domain/solver.js';
import { Puzzle } from '../domain/puzzle.js';
import { Difficulty } from '../domain/difficulty.js';
import { Seed } from '../domain/seed.js';
import { generateBatch } from '../domain/generator.js';

// ---------------------------------------------------------------------
// Grid + Solver sanity
// ---------------------------------------------------------------------

test('Grid.empty has 81 empty cells and no givens', () => {
  const grid = Grid.empty();
  assert.equal(grid.givenCount(), 0);
  assert.equal(grid.emptyPositions().length, 81);
  assert.equal(grid.isFilled(), false);
});

test('a generated full solution grid is filled and has exactly one solution', () => {
  const result = generateBatch(Seed.from('grid-sanity'), Difficulty.Easy, 1);
  assert.equal(result.ok, true);
  const solution = result.batch.puzzles[0].solution();
  assert.equal(solution.isFilled(), true);
  const { count } = countSolutions(solution, 2);
  assert.equal(count, 1); // a full grid has exactly one "solution": itself
});

test('countSolutions stops at `limit` and never exceeds it', () => {
  // An empty grid has vastly more than 2 solutions; countSolutions(empty, 2)
  // must stop counting at 2, not enumerate them all.
  const { count } = countSolutions(Grid.empty(), 2);
  assert.equal(count, 2);
});

// ---------------------------------------------------------------------
// Puzzle.tryCreate: the sole path to a verified-unique Puzzle
// ---------------------------------------------------------------------

test('Puzzle.tryCreate rejects a non-unique givens grid (empty grid: many solutions)', () => {
  const result = Puzzle.tryCreate(Grid.empty());
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'not-unique');
});

test('Puzzle.tryCreate accepts a givens grid with exactly one solution', () => {
  const batch = generateBatch(Seed.from('tryCreate-accept'), Difficulty.Medium, 1);
  assert.equal(batch.ok, true);
  const puzzle = batch.batch.puzzles[0];

  // Re-derive a Puzzle directly from the already-verified givens to prove
  // tryCreate accepts a genuinely-unique grid, independent of the
  // generator's own bookkeeping.
  const result = Puzzle.tryCreate(puzzle.givens());
  assert.equal(result.ok, true);
  assert.equal(result.puzzle.givenCount(), puzzle.givenCount());
});

test('Puzzle cannot be constructed except via tryCreate', () => {
  assert.throws(() => new Puzzle(Symbol('forged-guard'), Grid.empty(), Grid.empty()));
});

// ---------------------------------------------------------------------
// generateBatch: determinism, uniqueness, difficulty band, failure-as-value
// ---------------------------------------------------------------------

test('every puzzle in a generated batch has EXACTLY ONE solution', () => {
  for (const difficulty of Difficulty.all()) {
    const result = generateBatch(Seed.from(`uniqueness-${difficulty.key}`), difficulty, 5);
    assert.equal(result.ok, true, `expected ${difficulty.key} batch to succeed`);

    for (const puzzle of result.batch.puzzles) {
      const { count } = countSolutions(puzzle.givens(), 2);
      assert.equal(count, 1, `${difficulty.key} puzzle must have exactly one solution`);
    }
  }
});

test('every puzzle in a generated batch meets its difficulty band', () => {
  for (const difficulty of Difficulty.all()) {
    const result = generateBatch(Seed.from(`band-${difficulty.key}`), difficulty, 6);
    assert.equal(result.ok, true);

    for (const puzzle of result.batch.puzzles) {
      const gc = puzzle.givenCount();
      assert.ok(
        gc >= difficulty.min && gc <= difficulty.max,
        `${difficulty.key} puzzle given-count ${gc} outside band [${difficulty.min}, ${difficulty.max}]`,
      );
      assert.equal(difficulty.isSatisfiedBy(puzzle), true);
    }
  }
});

test('same (seed, difficulty, count) -> identical batch', () => {
  const seed = Seed.from('reproducible-seed-42');
  const a = generateBatch(seed, Difficulty.Medium, 4);
  const b = generateBatch(Seed.from('reproducible-seed-42'), Difficulty.Medium, 4);

  assert.equal(a.ok, true);
  assert.equal(b.ok, true);
  assert.equal(a.batch.puzzles.length, b.batch.puzzles.length);

  for (let i = 0; i < a.batch.puzzles.length; i++) {
    assert.equal(a.batch.puzzles[i].givens().toString(), b.batch.puzzles[i].givens().toString());
    assert.equal(a.batch.puzzles[i].solution().toString(), b.batch.puzzles[i].solution().toString());
  }
});

test('different seed -> different batch', () => {
  const a = generateBatch(Seed.from('seed-A'), Difficulty.Medium, 3);
  const b = generateBatch(Seed.from('seed-B'), Difficulty.Medium, 3);

  assert.equal(a.ok, true);
  assert.equal(b.ok, true);

  const aSerialized = a.batch.puzzles.map((p) => p.givens().toString()).join('|');
  const bSerialized = b.batch.puzzles.map((p) => p.givens().toString()).join('|');
  assert.notEqual(aSerialized, bSerialized);
});

test('asking for more puzzles reproduces the same earlier slots (derive(i) determinism contract)', () => {
  const seed = Seed.from('growing-batch');
  const small = generateBatch(seed, Difficulty.Easy, 3);
  const big = generateBatch(Seed.from('growing-batch'), Difficulty.Easy, 5);

  assert.equal(small.ok, true);
  assert.equal(big.ok, true);

  for (let i = 0; i < 3; i++) {
    assert.equal(
      small.batch.puzzles[i].givens().toString(),
      big.batch.puzzles[i].givens().toString(),
      `slot ${i} should be identical whether count is 3 or 5`,
    );
  }
});

test('failure surfaces as a value, not a throw, when a band is unreachable', () => {
  // A deliberately-impossible band (0 givens: an empty grid can never be
  // uniquely solvable) forces every attempt to get stuck above the
  // target, so the slot must fail out as a value rather than throwing
  // or silently returning a puzzle that ignores the band.
  const impossible = Object.freeze({
    key: 'impossible',
    name: 'Impossible',
    min: 0,
    max: 0,
    isSatisfiedBy(p) {
      const gc = typeof p === 'number' ? p : p.givenCount();
      return gc === 0;
    },
  });

  let result;
  assert.doesNotThrow(() => {
    result = generateBatch(Seed.from('impossible-band'), impossible, 2);
  });

  assert.equal(result.ok, false);
  assert.equal(result.failedSlot, 0);
  assert.equal(typeof result.reason, 'string');
  assert.ok(result.reason.length > 0);
});

test('generateBatch is a pure function: repeated calls do not mutate seed/difficulty/inputs', () => {
  const seed = Seed.from('purity-check');
  const identityBefore = seed.identity();
  const difficulty = Difficulty.Hard;
  const minBefore = difficulty.min;
  const maxBefore = difficulty.max;

  generateBatch(seed, difficulty, 2);

  assert.equal(seed.identity(), identityBefore);
  assert.equal(difficulty.min, minBefore);
  assert.equal(difficulty.max, maxBefore);
});

// ---------------------------------------------------------------------
// Seed: determinism primitives
// ---------------------------------------------------------------------

test('Seed.stream() is deterministic per identity', () => {
  const s1 = Seed.from('abc').stream();
  const s2 = Seed.from('abc').stream();
  for (let i = 0; i < 10; i++) {
    assert.equal(s1.next(), s2.next());
  }
});

test('Seed.derive(i) is deterministic and distinct per index', () => {
  const seed = Seed.from('base');
  const d0a = seed.derive(0).identity();
  const d0b = seed.derive(0).identity();
  const d1 = seed.derive(1).identity();
  assert.equal(d0a, d0b);
  assert.notEqual(d0a, d1);
});
