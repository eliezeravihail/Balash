// GridSize — a value type over the allowed dimensions {3, 4, 5} with derived
// cellCount (9/16/25) (D2). It is NOT a bare int: it is the single answer to
// "how big is a card," and it is obtainable ONLY through selectGridSize, so an
// out-of-range size is unrepresentable.
//
// selectGridSize is the ONE owner of the size rule (D3): thresholds and the
// {3,4,5} ceiling live here and nowhere else.

import { ok, err } from './result.js';
import { GenerationError } from './errors.js';

const TOKEN = Symbol('GridSize.construct');

// The two product knobs, in exactly one place.
const SMALLEST_DIMENSION = 3; // 3×3 → 9 cells → 9 words minimum
const THRESHOLDS = [
  { min: 25, dimension: 5 }, // ≥25 → 5×5 (largest; extra words widen the pool)
  { min: 16, dimension: 4 }, // 16–24 → 4×4
  { min: 9, dimension: 3 }, // 9–15 → 3×3
];

export class GridSize {
  #dimension;

  constructor(dimension, token) {
    if (token !== TOKEN) {
      throw new Error('GridSize is not directly constructible; use selectGridSize.');
    }
    this.#dimension = dimension;
    Object.freeze(this);
  }

  get dimension() {
    return this.#dimension;
  }

  get cellCount() {
    return this.#dimension * this.#dimension;
  }

  toString() {
    return `${this.#dimension}×${this.#dimension}`;
  }
}

// The minimum word count any card could need — the single source for the
// "too few words" boundary.
export const MIN_WORDS = SMALLEST_DIMENSION * SMALLEST_DIMENSION; // 9

// selectGridSize(n) → Result<GridSize, GenerationError>.
// n < 9 is a typed refusal, not an exception. Extra words are never an error.
export function selectGridSize(wordCount) {
  const n = wordCount | 0;
  if (n < MIN_WORDS) {
    return err(GenerationError.notEnoughWords(n, MIN_WORDS));
  }
  for (const { min, dimension } of THRESHOLDS) {
    if (n >= min) {
      return ok(new GridSize(dimension, TOKEN));
    }
  }
  // Unreachable given the n < MIN_WORDS guard above, but explicit for safety.
  return err(GenerationError.notEnoughWords(n, MIN_WORDS));
}
