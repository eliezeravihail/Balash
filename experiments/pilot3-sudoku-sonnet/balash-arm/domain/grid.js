// domain/grid.js
//
// Grid: the 9x9 cell layout and Sudoku's placement rule (no repeat in any
// row/column/box). An immutable value type. Knows nothing about difficulty,
// randomness, puzzles, or I/O -- purely "is this arrangement legal."
//
// Positions are plain integers 0..80 (row-major: pos = row*9 + col). This
// keeps the type dependency-free (no {row,col} object needed by callers
// that just want to iterate/store positions), while row/col/box helpers
// are exposed for anything that needs them.

export const EMPTY = 0;
export const SIZE = 9;
export const CELL_COUNT = SIZE * SIZE;

export function rowOf(pos) {
  return Math.floor(pos / SIZE);
}

export function colOf(pos) {
  return pos % SIZE;
}

export function boxOf(pos) {
  const boxRow = Math.floor(rowOf(pos) / 3);
  const boxCol = Math.floor(colOf(pos) / 3);
  return boxRow * 3 + boxCol;
}

export class Grid {
  #cells;

  // Not part of the public API surface conceptually, but JS has no
  // package-private -- callers should use Grid.empty()/Grid.fromArray()
  // rather than `new Grid(...)` directly.
  constructor(cells) {
    if (cells.length !== CELL_COUNT) {
      throw new Error(`Grid requires exactly ${CELL_COUNT} cells, got ${cells.length}`);
    }
    this.#cells = cells;
  }

  static empty() {
    return new Grid(new Array(CELL_COUNT).fill(EMPTY));
  }

  static fromArray(cells) {
    return new Grid(cells.slice());
  }

  // Compact serialization: 81 chars, '.' for empty, '1'-'9' for filled.
  // Handy for tests and for debugging/printing; not used by domain logic.
  static fromString(s) {
    if (s.length !== CELL_COUNT) {
      throw new Error(`Grid.fromString requires ${CELL_COUNT} characters, got ${s.length}`);
    }
    const cells = new Array(CELL_COUNT);
    for (let i = 0; i < CELL_COUNT; i++) {
      const ch = s[i];
      cells[i] = ch === '.' || ch === '0' ? EMPTY : Number(ch);
    }
    return new Grid(cells);
  }

  cellAt(pos) {
    return this.#cells[pos];
  }

  withCell(pos, value) {
    const next = this.#cells.slice();
    next[pos] = value;
    return new Grid(next);
  }

  emptyPositions() {
    const out = [];
    for (let i = 0; i < CELL_COUNT; i++) {
      if (this.#cells[i] === EMPTY) out.push(i);
    }
    return out;
  }

  isFilled() {
    for (let i = 0; i < CELL_COUNT; i++) {
      if (this.#cells[i] === EMPTY) return false;
    }
    return true;
  }

  // Would placing `value` at `pos` respect Sudoku's placement rule (no
  // repeat in pos's row, column, or 3x3 box)? Does NOT require pos to
  // currently be empty -- callers that only remove/replace should check
  // that separately if it matters to them.
  canPlace(pos, value) {
    const row = rowOf(pos);
    const col = colOf(pos);
    const boxRow = Math.floor(row / 3) * 3;
    const boxCol = Math.floor(col / 3) * 3;

    for (let c = 0; c < SIZE; c++) {
      if (c !== col && this.#cells[row * SIZE + c] === value) return false;
    }
    for (let r = 0; r < SIZE; r++) {
      if (r !== row && this.#cells[r * SIZE + col] === value) return false;
    }
    for (let r = boxRow; r < boxRow + 3; r++) {
      for (let c = boxCol; c < boxCol + 3; c++) {
        const p = r * SIZE + c;
        if (p !== pos && this.#cells[p] === value) return false;
      }
    }
    return true;
  }

  givenCount() {
    return CELL_COUNT - this.emptyPositions().length;
  }

  toArray() {
    return this.#cells.slice();
  }

  toString() {
    let out = '';
    for (let i = 0; i < CELL_COUNT; i++) {
      out += this.#cells[i] === EMPTY ? '.' : String(this.#cells[i]);
    }
    return out;
  }
}
