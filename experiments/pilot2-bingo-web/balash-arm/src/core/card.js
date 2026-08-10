// Card — one card: an immutable GridSize plus its cells in row-major order (D2).
// It knows its own layout (iterate by row) and reports a fingerprint (ordered
// contents) so a CardSet can reason about distinctness. It carries NO render
// logic — it is data-with-rules, and it refuses to exist with the wrong number
// of cells.

// NUL separator: a trimmed, non-blank word can never contain U+0000, so joining
// cells with it makes the fingerprint a lossless, collision-free identity.
const FP_SEP = '\u0000';

export class Card {
  #gridSize;
  #cells; // frozen array, length === gridSize.cellCount

  constructor(gridSize, cells) {
    if (cells.length !== gridSize.cellCount) {
      // A programming error, not user input — the pure pipeline must never
      // hand a Card the wrong cell count.
      throw new Error(
        `Card for ${gridSize} needs ${gridSize.cellCount} cells; got ${cells.length}.`,
      );
    }
    this.#gridSize = gridSize;
    this.#cells = Object.freeze(cells.slice());
    Object.freeze(this);
  }

  get gridSize() {
    return this.#gridSize;
  }

  get cells() {
    return this.#cells;
  }

  // Ordered contents → identity for distinctness (same words, same positions).
  fingerprint() {
    return this.#cells.join(FP_SEP);
  }

  // Tell-don't-ask: the renderer asks the Card to iterate rows; it never pulls
  // the raw array and recomputes geometry. Yields arrays of length `dimension`.
  *rows() {
    const dim = this.#gridSize.dimension;
    for (let r = 0; r < dim; r++) {
      yield this.#cells.slice(r * dim, r * dim + dim);
    }
  }
}
