// Headless test of the PURE core — run with `node test/core.test.js`.
// Node stdlib only (assert). Imports the exact same core modules the browser
// loads, proving the core is browser-free (no document/window/Date/Math.random).

import assert from 'node:assert/strict';

import { WordList } from '../src/core/wordlist.js';
import { selectGridSize, MIN_WORDS } from '../src/core/gridsize.js';
import { Seed } from '../src/core/seed.js';
import { generate } from '../src/core/generate.js';
import { CardSet, maxDistinctCards } from '../src/core/cardset.js';
import { ErrorCode } from '../src/core/errors.js';

let passed = 0;
let failed = 0;
const failures = [];

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`  ok  ${name}`);
  } catch (e) {
    failed++;
    failures.push({ name, e });
    console.log(`FAIL  ${name}`);
    console.log(`       ${e && e.message}`);
  }
}

// Helpers ---------------------------------------------------------------------

function words(n, prefix = 'w') {
  return Array.from({ length: n }, (_, i) => `${prefix}${i + 1}`);
}

function fingerprints(cardSet) {
  return cardSet.cards.map((c) => c.fingerprint());
}

// A degenerate RNG stub: proves the core depends only on the `sampleDistinct`
// seam and lets us simulate a shallow/exhausted stream cheaply.
function stubRng(distinctPatterns) {
  let i = 0;
  return {
    sampleDistinct() {
      const pattern = distinctPatterns[i % distinctPatterns.length];
      i++;
      return pattern.slice();
    },
  };
}

// ---------------------------------------------------------------------------
console.log('WordList cleaning (D2, §6)');

test('trims, drops blanks, collapses case-insensitive dupes, keeps first spelling & order', () => {
  const { wordList, stats } = WordList.build([
    '  Apple ',
    '',
    'banana',
    'APPLE', // dup of Apple (case-insensitive) -> merged, first spelling kept
    '   ', // blank
    'Cherry',
    'cherry', // dup -> merged
  ]);
  assert.deepEqual(wordList.words, ['Apple', 'banana', 'Cherry']);
  assert.equal(wordList.size, 3);
  assert.equal(stats.blanksDropped, 2);
  assert.equal(stats.duplicatesMerged, 2);
});

test('accepts raw text with mixed newlines', () => {
  const { wordList } = WordList.build('a\r\nb\rc\n\nd');
  assert.deepEqual(wordList.words, ['a', 'b', 'c', 'd']);
});

test('internal spacing preserved, only ends trimmed', () => {
  const { wordList } = WordList.build(['  two  words  ']);
  assert.deepEqual(wordList.words, ['two  words']);
});

// ---------------------------------------------------------------------------
console.log('selectGridSize thresholds (D3)');

test('n < 9 → typed refusal, not an exception', () => {
  const r = selectGridSize(8);
  assert.equal(r.ok, false);
  assert.equal(r.error.code, ErrorCode.NOT_ENOUGH_WORDS);
  assert.equal(r.error.details.needed, MIN_WORDS);
  assert.equal(r.error.details.have, 8);
});

test('boundaries: 9→3, 15→3, 16→4, 24→4, 25→5, 100→5', () => {
  assert.equal(selectGridSize(9).value.dimension, 3);
  assert.equal(selectGridSize(15).value.dimension, 3);
  assert.equal(selectGridSize(16).value.dimension, 4);
  assert.equal(selectGridSize(24).value.dimension, 4);
  assert.equal(selectGridSize(25).value.dimension, 5);
  assert.equal(selectGridSize(100).value.dimension, 5);
});

test('cellCount derives from dimension (9/16/25)', () => {
  assert.equal(selectGridSize(9).value.cellCount, 9);
  assert.equal(selectGridSize(16).value.cellCount, 16);
  assert.equal(selectGridSize(25).value.cellCount, 25);
});

test('GridSize is not directly constructible', () => {
  // Imported class exists but the constructor refuses without the token.
  const G = Object.getPrototypeOf(selectGridSize(9).value).constructor;
  assert.throws(() => new G(3), /not directly constructible/);
});

// ---------------------------------------------------------------------------
console.log('Determinism (D1, D4)');

test('same (words, settings, seed) → identical cards', () => {
  const w = words(30);
  const seed = Seed.parse('deadbeef').value;
  const a = generate(w, { cardCount: 8 }, seed);
  const b = generate(w, { cardCount: 8 }, seed);
  assert.equal(a.ok && b.ok, true);
  assert.deepEqual(fingerprints(a.value), fingerprints(b.value));
});

test('different seed → different set', () => {
  const w = words(30);
  const a = generate(w, { cardCount: 8 }, Seed.parse('00000001').value);
  const b = generate(w, { cardCount: 8 }, Seed.parse('00000002').value);
  assert.notDeepEqual(fingerprints(a.value), fingerprints(b.value));
});

test('seed round-trips through its canonical 8-hex form', () => {
  assert.equal(Seed.fromUint32(0xdeadbeef).toString(), 'deadbeef');
  assert.equal(Seed.parse('1').value.toUint32(), 1);
  assert.equal(Seed.parse('  DEADBEEF ').value.toString(), 'deadbeef');
  assert.equal(Seed.parse('xyz').ok, false);
});

// ---------------------------------------------------------------------------
console.log('Distinctness within a set (D5)');

test('no two cards in a set are identical', () => {
  const w = words(25); // 5×5, pool exactly fills — arrangement varies
  const res = generate(w, { cardCount: 20 }, Seed.parse('abc123').value);
  assert.equal(res.ok, true);
  const fps = fingerprints(res.value);
  assert.equal(new Set(fps).size, fps.length);
});

test('each cell is a word (no free space) and card has full cellCount', () => {
  const res = generate(words(9), { cardCount: 3 }, Seed.fromUint32(7));
  const card = res.value.cards[0];
  assert.equal(card.cells.length, 9);
  assert.ok(card.cells.every((c) => typeof c === 'string' && c.length > 0));
});

test('rows() yields the grid in row-major order', () => {
  const res = generate(words(9), { cardCount: 1 }, Seed.fromUint32(7));
  const card = res.value.cards[0];
  const rows = [...card.rows()];
  assert.equal(rows.length, 3);
  assert.deepEqual([].concat(...rows), [...card.cells]);
});

// ---------------------------------------------------------------------------
console.log('Shallow pool stops at max distinct and reports it (D5)');

test('maxDistinctCards computes permutations P(n, k)', () => {
  assert.equal(maxDistinctCards(4, 2), 12); // 4*3
  assert.equal(maxDistinctCards(3, 3), 6); // 3!
  assert.equal(maxDistinctCards(2, 3), 0); // impossible
  assert.equal(maxDistinctCards(9, 9), 362880); // 9!
});

test('CardSet.build stops at the distinct ceiling and reports truncation', () => {
  // Degenerate stream yields only 3 distinct cards; ask for 10.
  const gridSize = selectGridSize(9).value; // 3×3, cellCount 9
  const pool = words(9);
  const rng = stubRng([
    words(9, 'a'),
    words(9, 'b'),
    words(9, 'c'),
  ].map((p) => p.slice(0, 9)));
  const set = CardSet.build({
    gridSize,
    seed: Seed.fromUint32(1),
    pool,
    requestedCount: 10,
    rng,
  });
  assert.equal(set.producedCount, 3);
  assert.equal(set.requestedCount, 10);
  assert.equal(set.isTruncated, true);
});

test('build never loops forever on a fully degenerate (single-card) stream', () => {
  const gridSize = selectGridSize(9).value;
  const rng = stubRng([words(9, 'only')]); // always the same card
  const set = CardSet.build({
    gridSize,
    seed: Seed.fromUint32(1),
    pool: words(9),
    requestedCount: 5,
    rng,
  });
  assert.equal(set.producedCount, 1);
  assert.equal(set.isTruncated, true);
});

// ---------------------------------------------------------------------------
console.log('Typed outcomes across the seam (D6)');

test('too few words → Result error, no throw', () => {
  const res = generate(words(5), { cardCount: 8 }, Seed.fromUint32(1));
  assert.equal(res.ok, false);
  assert.equal(res.error.code, ErrorCode.NOT_ENOUGH_WORDS);
});

test('invalid card count → Result error', () => {
  assert.equal(generate(words(9), { cardCount: 0 }, Seed.fromUint32(1)).ok, false);
  assert.equal(generate(words(9), { cardCount: 2.5 }, Seed.fromUint32(1)).ok, false);
});

test('generate accepts a prebuilt WordList too', () => {
  const { wordList } = WordList.build(words(9));
  const res = generate(wordList, { cardCount: 2 }, Seed.fromUint32(3));
  assert.equal(res.ok, true);
  assert.equal(res.value.producedCount, 2);
});

// ---------------------------------------------------------------------------
console.log('');
console.log(`${passed} passed, ${failed} failed, ${passed + failed} total`);
if (failed > 0) {
  process.exitCode = 1;
}
