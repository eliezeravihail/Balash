// CardSet — the batch: the resolved GridSize, the Seed that produced it, and the
// ordered Cards. It OWNS the batch-level distinctness guarantee (D5), stated
// honestly:
//   - No two cards in a set are IDENTICAL (same words in the same positions):
//     reject-and-redraw on fingerprint collision.
//   - NO promise of word-disjointness or cross-seed/global uniqueness.
//   - If the pool is too shallow to make the requested number of distinct cards,
//     stop at the maximum it can actually produce and REPORT how many and why —
//     never loop forever, never pad with duplicates.

import { Card } from './card.js';

// The honest ceiling on distinct cards: permutations P(poolSize, cellCount) =
// poolSize! / (poolSize - cellCount)!. That is how many distinct (contents +
// arrangement) cards can exist at all. Capped to avoid meaningless huge numbers.
const CEILING_CAP = Number.MAX_SAFE_INTEGER;

export function maxDistinctCards(poolSize, cellCount) {
  if (cellCount > poolSize) return 0;
  let product = 1;
  for (let i = 0; i < cellCount; i++) {
    product *= poolSize - i;
    if (product >= CEILING_CAP) return CEILING_CAP;
  }
  return product;
}

export class CardSet {
  #gridSize;
  #seed;
  #cards;
  #requestedCount;

  constructor(gridSize, seed, cards, requestedCount) {
    this.#gridSize = gridSize;
    this.#seed = seed;
    this.#cards = Object.freeze(cards.slice());
    this.#requestedCount = requestedCount;
    Object.freeze(this);
  }

  // Assemble a distinct batch by reject-and-redraw. `rng` is injected (the seam)
  // and only needs a `sampleDistinct(pool, k)` method. `pool` is the cleaned,
  // ordered word array. Every card draws `cellCount` distinct words from the
  // WHOLE pool (words may recur ACROSS cards) and arranges them via the stream.
  static build({ gridSize, seed, pool, requestedCount, rng }) {
    const cellCount = gridSize.cellCount;

    // How many distinct cards are even possible — the reason a batch may stop
    // short. min(requested, ceiling) is the honest target.
    const ceiling = maxDistinctCards(pool.length, cellCount);
    const target = Math.min(requestedCount, ceiling);

    const cards = [];
    const seen = new Set();

    // Runtime safety net so a degenerate/shallow stream can never spin forever:
    // if we fail to find a NEW distinct card too many times in a row, the pool
    // is effectively exhausted and we stop with what we have.
    const maxConsecutiveMisses = Math.max(1000, target * 50);
    let consecutiveMisses = 0;

    while (cards.length < target && consecutiveMisses < maxConsecutiveMisses) {
      const cells = rng.sampleDistinct(pool, cellCount);
      const card = new Card(gridSize, cells);
      const fp = card.fingerprint();
      if (seen.has(fp)) {
        consecutiveMisses++;
        continue;
      }
      seen.add(fp);
      cards.push(card);
      consecutiveMisses = 0;
    }

    return new CardSet(gridSize, seed, cards, requestedCount);
  }

  get gridSize() {
    return this.#gridSize;
  }

  get seed() {
    return this.#seed;
  }

  get cards() {
    return this.#cards;
  }

  get requestedCount() {
    return this.#requestedCount;
  }

  get producedCount() {
    return this.#cards.length;
  }

  // Honest fact: did the shallow pool force us to stop short?
  get isTruncated() {
    return this.#cards.length < this.#requestedCount;
  }
}
