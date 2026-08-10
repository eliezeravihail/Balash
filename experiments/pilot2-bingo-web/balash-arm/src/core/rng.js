// The ONLY randomness in the core (D4). A small, well-known seeded 32-bit PRNG
// (mulberry32). No Math.random, no Date, no globals — purely a function of the
// seed handed in. `Math.imul` here is arithmetic, not randomness.

function mulberry32(seedUint32) {
  let a = seedUint32 >>> 0;
  return function next() {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Rng is the injectable seam for randomness. The core depends on this interface
// (`sampleDistinct`), so a degenerate stub can stand in for tests, and a PDF or
// SVG backend could reuse the exact same generation path.
export class Rng {
  #next;

  constructor(seedUint32) {
    this.#next = mulberry32(seedUint32);
  }

  // A float in [0, 1).
  float() {
    return this.#next();
  }

  // An integer in [0, nExclusive).
  int(nExclusive) {
    return Math.floor(this.float() * nExclusive);
  }

  // Draw `k` distinct items from `pool` in random order (partial Fisher–Yates).
  // The order IS the card's arrangement — one draw yields contents + layout.
  // Requires k <= pool.length (guaranteed upstream by the grid-size rule).
  sampleDistinct(pool, k) {
    const arr = pool.slice();
    const n = arr.length;
    const out = [];
    for (let i = 0; i < k; i++) {
      const j = i + this.int(n - i);
      const tmp = arr[i];
      arr[i] = arr[j];
      arr[j] = tmp;
      out.push(arr[i]);
    }
    return out;
  }
}
