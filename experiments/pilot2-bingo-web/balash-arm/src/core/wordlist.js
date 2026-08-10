// WordList — the SOLE owner of input hygiene (D2, §6). Construction is the only
// place cleaning rules live: trim each line, drop blanks, collapse
// case-insensitive duplicates (keeping the first spelling), preserve order.
// A WordList that survives construction is clean by definition — downstream
// code never re-validates. It also JUDGES grid support (`supports`) rather than
// exposing a raw count for callers to reason about.

const TOKEN = Symbol('WordList.construct');

export class WordList {
  #words; // frozen array of cleaned words, in supply order

  constructor(words, token) {
    if (token !== TOKEN) {
      throw new Error('WordList is not directly constructible; use WordList.build.');
    }
    this.#words = Object.freeze(words.slice());
    Object.freeze(this);
  }

  // Build from raw text OR an array of raw lines. Returns
  //   { wordList, stats: { kept, blanksDropped, duplicatesMerged } }
  // so the UI can honestly report how the pool changed.
  static build(input) {
    const rawLines = Array.isArray(input)
      ? input
      : String(input ?? '').split(/\r\n|\r|\n/);

    const kept = [];
    const seen = new Set(); // case-insensitive keys already taken
    let blanksDropped = 0;
    let duplicatesMerged = 0;

    for (const rawLine of rawLines) {
      // Trim leading/trailing whitespace; internal spacing is preserved.
      const word = String(rawLine ?? '').trim();
      if (word === '') {
        blanksDropped++;
        continue;
      }
      // Case-insensitive collapse. `toLowerCase` is a no-op for case-less
      // scripts (e.g. Hebrew), which then fall back to exact-string matching.
      const key = word.toLowerCase();
      if (seen.has(key)) {
        duplicatesMerged++;
        continue;
      }
      seen.add(key);
      kept.push(word); // keep the FIRST spelling
    }

    return {
      wordList: new WordList(kept, TOKEN),
      stats: { kept: kept.length, blanksDropped, duplicatesMerged },
    };
  }

  get size() {
    return this.#words.length;
  }

  // Read-only ordered view.
  get words() {
    return this.#words;
  }

  // The list DECIDES whether it can fill a grid, rather than leaking its count.
  supports(gridSize) {
    return this.#words.length >= gridSize.cellCount;
  }
}
