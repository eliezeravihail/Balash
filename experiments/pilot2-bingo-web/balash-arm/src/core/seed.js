// Seed — a value type over the reproducibility token (D2, §5). It owns its
// format (8 hex chars = one 32-bit integer) and parsing, and it carries the
// "same seed → same output" contract. Never a loose string inside the core.
// Minting a fresh seed is the UI's job (the one nondeterministic act, done
// OUTSIDE the core and fed in) — this type only formats/parses/holds.

import { ok, err } from './result.js';
import { GenerationError } from './errors.js';

const TOKEN = Symbol('Seed.construct');

export class Seed {
  #value; // uint32

  constructor(uint32, token) {
    if (token !== TOKEN) {
      throw new Error('Seed is not directly constructible; use Seed.fromUint32 / Seed.parse.');
    }
    this.#value = uint32 >>> 0;
    Object.freeze(this);
  }

  static fromUint32(n) {
    return new Seed(n >>> 0, TOKEN);
  }

  // Result<Seed, GenerationError>. Accepts 1–8 hex chars, case-insensitive,
  // with surrounding whitespace trimmed.
  static parse(raw) {
    const cleaned = String(raw ?? '').trim().toLowerCase();
    if (!/^[0-9a-f]{1,8}$/.test(cleaned)) {
      return err(GenerationError.invalidSeed(raw));
    }
    return ok(new Seed(parseInt(cleaned, 16) >>> 0, TOKEN));
  }

  toUint32() {
    return this.#value;
  }

  // Canonical form: zero-padded 8-char lowercase hex — stable and copyable.
  toString() {
    return this.#value.toString(16).padStart(8, '0');
  }
}
