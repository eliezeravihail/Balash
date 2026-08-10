// domain/seed.js
//
// Seed: a value type wrapping a normalized string identity. Owns turning
// that identity into a deterministic number stream (mulberry32, a small
// seeded PRNG) via seed.stream(), and owns deriving per-slot/per-attempt
// child seeds via seed.derive(index).
//
// This is the ONLY place "same seed -> same numbers" is decided, and the
// ONLY source of randomness anywhere in domain/. Nothing in domain/ calls
// Math.random or Date -- this module doesn't either. Minting a *fresh*
// seed identity when the user leaves the field blank is a UI concern
// (app/controller.js's job, since that's genuinely nondeterministic) --
// Seed itself only ever turns a given identity into deterministic output.

function hashStringToUint32(str) {
  // FNV-1a, 32-bit. Simple, dependency-free, good-enough avalanche for
  // seeding a PRNG (not cryptographic, not trying to be).
  let h = 0x811c9dc5;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

function mulberry32(seedInt) {
  let a = seedInt >>> 0;
  return function next() {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export class Seed {
  #identity;
  #hash;

  constructor(identity) {
    this.#identity = String(identity);
    this.#hash = hashStringToUint32(this.#identity);
  }

  static from(identity) {
    return new Seed(identity);
  }

  identity() {
    return this.#identity;
  }

  // Returns a fresh { next(): number in [0,1) } stream. Each call starts
  // the stream over from this seed's hash -- callers that need many draws
  // across a computation should call stream() once and reuse the object.
  stream() {
    const rand = mulberry32(this.#hash);
    return { next: () => rand() };
  }

  // Deterministically derives a child Seed for slot/attempt `index`.
  // Same (seed, index) always yields the same child identity.
  derive(index) {
    return new Seed(`${this.#identity}::${index}`);
  }
}
