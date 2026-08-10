/**
 * Deterministic seeded pseudo-random number generator.
 *
 * Any string (or number) seed hashes down to a 32-bit integer via a
 * FNV-1a style string hash, which then seeds a mulberry32 generator.
 * The same seed always produces the same stream of numbers, on any
 * machine, forever - this is what makes puzzle batches reproducible
 * from a seed alone.
 *
 * Exposed as a small UMD-style module so it can be `require()`d from
 * Node (tests) and loaded as a plain <script> in the browser (no
 * bundler, no build step).
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.SudokuRng = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  // FNV-1a inspired string hash -> 32-bit unsigned seed.
  function hashSeed(str) {
    let h = 0x811c9dc5; // FNV offset basis
    for (let i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 0x01000193); // FNV prime
    }
    // Extra avalanche so short/similar seeds still diverge quickly.
    h ^= h >>> 16;
    h = Math.imul(h, 0x45d9f3b);
    h ^= h >>> 16;
    return h >>> 0;
  }

  // mulberry32: small, fast, decent-quality 32-bit PRNG.
  function mulberry32(seed) {
    let a = seed >>> 0;
    return function () {
      a |= 0;
      a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /**
   * Create a deterministic RNG from a seed (string or number).
   * Returns an object with:
   *   next()        -> float in [0, 1)
   *   nextInt(n)     -> integer in [0, n)
   *   shuffle(array) -> Fisher-Yates shuffle in place, returns array
   */
  function createRng(seed) {
    const numericSeed = hashSeed(String(seed));
    const next = mulberry32(numericSeed);
    return {
      next,
      nextInt(n) {
        return Math.floor(next() * n);
      },
      shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
          const j = Math.floor(next() * (i + 1));
          const tmp = array[i];
          array[i] = array[j];
          array[j] = tmp;
        }
        return array;
      },
    };
  }

  return { createRng, hashSeed };
});
