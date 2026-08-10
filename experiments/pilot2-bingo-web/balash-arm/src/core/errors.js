// GenerationError — a named, concept-level failure the core hands back (D6).
// It speaks in the user's terms and carries the numbers the UI needs to explain
// what happened. It is data, never a thrown exception across the seam.

export const ErrorCode = Object.freeze({
  NOT_ENOUGH_WORDS: 'NOT_ENOUGH_WORDS',
  INVALID_CARD_COUNT: 'INVALID_CARD_COUNT',
  INVALID_SEED: 'INVALID_SEED',
});

export class GenerationError {
  #code;
  #message;
  #details;

  constructor(code, message, details = {}) {
    this.#code = code;
    this.#message = message;
    this.#details = Object.freeze({ ...details });
    Object.freeze(this);
  }

  get code() {
    return this.#code;
  }

  get message() {
    return this.#message;
  }

  get details() {
    return this.#details;
  }

  static notEnoughWords(have, needed) {
    return new GenerationError(
      ErrorCode.NOT_ENOUGH_WORDS,
      `Need at least ${needed} words for the smallest card; you have ${have}.`,
      { have, needed },
    );
  }

  static invalidCardCount(requested) {
    return new GenerationError(
      ErrorCode.INVALID_CARD_COUNT,
      `Card count must be a whole number of at least 1; got ${requested}.`,
      { requested },
    );
  }

  static invalidSeed(raw) {
    return new GenerationError(
      ErrorCode.INVALID_SEED,
      `Seed must be 1–8 hexadecimal characters (0–9, a–f); got "${raw}".`,
      { raw },
    );
  }
}
