/*
 * Headless tests for the deterministic generation logic.
 * Run with: node test/bingo.test.js   (node stdlib only, no deps)
 */
'use strict';

const assert = require('assert');
const Bingo = require('../bingo.js');

let passed = 0;
function test(name, fn) {
  fn();
  passed++;
  console.log('  ok  - ' + name);
}

// Helper: a pool of N unique words "w0".."w{N-1}".
function pool(n) {
  const a = [];
  for (let i = 0; i < n; i++) a.push('w' + i);
  return a;
}

// Flatten a card's cell texts.
function texts(card) {
  return card.cells.map(function (c) {
    return c.text;
  });
}

console.log('parseWords');
test('trims, drops blanks, de-dupes case-insensitively, keeps order', function () {
  const w = Bingo.parseWords('  Apple \n\nbanana\napple\nBANANA\n cherry ');
  assert.deepStrictEqual(w, ['Apple', 'banana', 'cherry']);
});
test('empty input yields empty list', function () {
  assert.deepStrictEqual(Bingo.parseWords(''), []);
  assert.deepStrictEqual(Bingo.parseWords('   \n  \n'), []);
});

console.log('grid sizing');
test('cellsNeeded accounts for free space on odd grids only', function () {
  assert.strictEqual(Bingo.cellsNeeded(3, false), 9);
  assert.strictEqual(Bingo.cellsNeeded(3, true), 8);
  assert.strictEqual(Bingo.cellsNeeded(4, false), 16);
  assert.strictEqual(Bingo.cellsNeeded(4, true), 16); // even grid: no free cell
  assert.strictEqual(Bingo.cellsNeeded(5, false), 25);
  assert.strictEqual(Bingo.cellsNeeded(5, true), 24);
});
test('autoGridSize picks the largest grid that fits', function () {
  assert.strictEqual(Bingo.autoGridSize(8, false), null); // < 9
  assert.strictEqual(Bingo.autoGridSize(9, false), 3);
  assert.strictEqual(Bingo.autoGridSize(15, false), 3);
  assert.strictEqual(Bingo.autoGridSize(16, false), 4);
  assert.strictEqual(Bingo.autoGridSize(24, false), 4);
  assert.strictEqual(Bingo.autoGridSize(25, false), 5);
  assert.strictEqual(Bingo.autoGridSize(100, false), 5);
  // With free space the thresholds drop by one.
  assert.strictEqual(Bingo.autoGridSize(8, true), 3);
  assert.strictEqual(Bingo.autoGridSize(24, true), 5);
});

console.log('validation / bad input');
test('too few words is rejected', function () {
  const r = Bingo.generateCards(pool(5), { seed: 's' });
  assert.strictEqual(r.ok, false);
  assert.ok(/at least 9/.test(r.error), r.error);
});
test('manual grid too big for pool is rejected', function () {
  const r = Bingo.generateCards(pool(10), { seed: 's', gridSize: 4 });
  assert.strictEqual(r.ok, false);
  assert.ok(/needs 16/.test(r.error), r.error);
});
test('card count is clamped to >= 1', function () {
  const r = Bingo.generateCards(pool(9), { seed: 's', cardCount: 0 });
  assert.strictEqual(r.ok, true);
  assert.strictEqual(r.cardCount, 1);
});

console.log('generation shape');
test('auto 3x3 from exactly 9 words uses all words, no free cell', function () {
  const r = Bingo.generateCards(pool(9), { seed: 's', cardCount: 3 });
  assert.strictEqual(r.ok, true);
  assert.strictEqual(r.gridSize, 3);
  assert.strictEqual(r.freeSpace, false);
  r.cards.forEach(function (card) {
    assert.strictEqual(card.cells.length, 9);
    const set = new Set(texts(card));
    assert.strictEqual(set.size, 9, 'no duplicate words within a card');
    card.cells.forEach(function (c) {
      assert.strictEqual(c.free, false);
    });
  });
});
test('free space puts FREE label in the center of an odd grid', function () {
  const r = Bingo.generateCards(pool(24), {
    seed: 's',
    gridSize: 5,
    freeSpace: true,
  });
  assert.strictEqual(r.ok, true);
  assert.strictEqual(r.freeSpace, true);
  const card = r.cards[0];
  const center = card.cells[12]; // index 12 of 25 is the middle
  assert.strictEqual(center.free, true);
  assert.strictEqual(center.text, 'FREE');
  // Exactly one free cell; 24 real distinct words.
  const free = card.cells.filter(function (c) {
    return c.free;
  });
  assert.strictEqual(free.length, 1);
  const real = card.cells
    .filter(function (c) {
      return !c.free;
    })
    .map(function (c) {
      return c.text;
    });
  assert.strictEqual(new Set(real).size, 24);
});

console.log('determinism');
test('same seed + words + settings reproduces identical cards', function () {
  const opts = { seed: 'HELLO', cardCount: 8, gridSize: 4 };
  const a = Bingo.generateCards(pool(30), opts);
  const b = Bingo.generateCards(pool(30), opts);
  assert.deepStrictEqual(a.cards, b.cards);
});
test('different seed produces a different batch', function () {
  const base = { cardCount: 6, gridSize: 4 };
  const a = Bingo.generateCards(pool(30), Object.assign({ seed: 'AAA' }, base));
  const b = Bingo.generateCards(pool(30), Object.assign({ seed: 'BBB' }, base));
  assert.notDeepStrictEqual(a.cards, b.cards);
});
test('cards within one batch differ from each other', function () {
  const r = Bingo.generateCards(pool(30), {
    seed: 'X',
    cardCount: 10,
    gridSize: 4,
  });
  const sigs = r.cards.map(function (c) {
    return texts(c).join('|');
  });
  const unique = new Set(sigs);
  assert.strictEqual(unique.size, sigs.length, 'all cards should be distinct');
});
test('when pool == card size, distinctness comes from arrangement', function () {
  const r = Bingo.generateCards(pool(9), {
    seed: 'Y',
    cardCount: 5,
    gridSize: 3,
  });
  // Every card uses the same 9 words (the whole pool)...
  r.cards.forEach(function (card) {
    assert.strictEqual(new Set(texts(card)).size, 9);
  });
  // ...but the orderings differ.
  const sigs = new Set(
    r.cards.map(function (c) {
      return texts(c).join('|');
    })
  );
  assert.ok(sigs.size > 1, 'arrangements should vary');
});

console.log('');
console.log('All ' + passed + ' tests passed.');
