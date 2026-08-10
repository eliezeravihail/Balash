/*
 * bingo.js — pure, deterministic bingo-card generation logic.
 *
 * This module has NO DOM dependencies so it can be unit-tested headlessly
 * with node. It is exposed both as a CommonJS module (for node/tests) and as
 * a global `Bingo` object (for the browser via a plain <script> tag).
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) {
    module.exports = api;
  } else {
    root.Bingo = api;
  }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // --- Deterministic PRNG ---------------------------------------------------

  // xmur3 string hash: turns an arbitrary string into a well-mixed 32-bit seed.
  function xmur3(str) {
    let h = 1779033703 ^ str.length;
    for (let i = 0; i < str.length; i++) {
      h = Math.imul(h ^ str.charCodeAt(i), 3432918353);
      h = (h << 13) | (h >>> 19);
    }
    return function () {
      h = Math.imul(h ^ (h >>> 16), 2246822507);
      h = Math.imul(h ^ (h >>> 13), 3266489909);
      h ^= h >>> 16;
      return h >>> 0;
    };
  }

  // mulberry32: tiny, fast PRNG. Given the same 32-bit seed it always yields
  // the same stream of floats in [0, 1).
  function mulberry32(a) {
    return function () {
      a |= 0;
      a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // Build a deterministic rng from any string seed.
  function makeRng(seedStr) {
    const seed = xmur3(String(seedStr))();
    return mulberry32(seed);
  }

  // In-place Fisher-Yates shuffle of a copy of `arr`, driven by `rng`.
  function shuffled(arr, rng) {
    const out = arr.slice();
    for (let i = out.length - 1; i > 0; i--) {
      const j = Math.floor(rng() * (i + 1));
      const tmp = out[i];
      out[i] = out[j];
      out[j] = tmp;
    }
    return out;
  }

  // --- Word parsing ---------------------------------------------------------

  // Parse raw textarea input into a clean word list: split on newlines, trim,
  // drop blanks, and de-duplicate (case-insensitive) while preserving order.
  function parseWords(raw) {
    const seen = new Set();
    const out = [];
    String(raw == null ? '' : raw)
      .split(/\r?\n/)
      .forEach(function (line) {
        const w = line.trim();
        if (!w) return;
        const key = w.toLowerCase();
        if (seen.has(key)) return;
        seen.add(key);
        out.push(w);
      });
    return out;
  }

  // --- Grid sizing rules ----------------------------------------------------

  const GRID_SIZES = [3, 4, 5];
  const FREE_LABEL = 'FREE';

  function isOdd(n) {
    return n % 2 === 1;
  }

  // How many real words a card of `size` needs. A free center space (only
  // meaningful on odd grids) removes one required word.
  function cellsNeeded(size, freeSpace) {
    const total = size * size;
    return freeSpace && isOdd(size) ? total - 1 : total;
  }

  // Largest grid size whose word requirement is satisfied by `wordCount`.
  // Returns null when there aren't even enough words for a 3x3.
  function autoGridSize(wordCount, freeSpace) {
    for (let i = GRID_SIZES.length - 1; i >= 0; i--) {
      const size = GRID_SIZES[i];
      if (wordCount >= cellsNeeded(size, freeSpace)) return size;
    }
    return null;
  }

  // --- Validation -----------------------------------------------------------

  // Resolve and validate settings against the word pool. `gridSize` may be
  // 'auto' or one of 3/4/5. Returns { ok, error?, gridSize, cellsNeeded, ... }.
  function resolveSettings(words, opts) {
    opts = opts || {};
    const freeSpace = !!opts.freeSpace;
    const cardCount = Math.max(1, Math.floor(opts.cardCount || 1));
    const wordCount = words.length;

    const minFor3 = cellsNeeded(3, freeSpace);
    if (wordCount < minFor3) {
      return {
        ok: false,
        error:
          'Need at least ' +
          minFor3 +
          ' distinct words for a 3x3 card' +
          (freeSpace ? ' (with free space)' : '') +
          '. You supplied ' +
          wordCount +
          '.',
      };
    }

    let gridSize;
    if (opts.gridSize && opts.gridSize !== 'auto') {
      gridSize = Number(opts.gridSize);
      if (GRID_SIZES.indexOf(gridSize) === -1) {
        return { ok: false, error: 'Unsupported grid size: ' + opts.gridSize };
      }
      const need = cellsNeeded(gridSize, freeSpace);
      if (wordCount < need) {
        return {
          ok: false,
          error:
            'A ' +
            gridSize +
            'x' +
            gridSize +
            ' card needs ' +
            need +
            ' words; you supplied ' +
            wordCount +
            '. Add more words or pick a smaller grid.',
        };
      }
    } else {
      gridSize = autoGridSize(wordCount, freeSpace);
    }

    return {
      ok: true,
      gridSize: gridSize,
      freeSpace: freeSpace && isOdd(gridSize),
      cardCount: cardCount,
      cellsNeeded: cellsNeeded(gridSize, freeSpace && isOdd(gridSize)),
    };
  }

  // --- Card generation ------------------------------------------------------

  // Build one card as an object:
  //   { size, freeSpace, cells: [ { text, free } ... ] }  (row-major order)
  //
  // Each card is generated from a per-card sub-seed derived from the master
  // seed and the card index, so cards differ from one another yet the whole
  // batch is reproducible from (words, master seed, settings).
  function buildCard(words, resolved, masterSeed, index) {
    const rng = makeRng(String(masterSeed) + '::card::' + index);
    const need = resolved.cellsNeeded;

    // Draw `need` distinct words. When the pool is larger than a card, the
    // subset itself varies between cards; when it's exactly one card's worth,
    // distinctness comes from the arrangement.
    const picked = shuffled(words, rng).slice(0, need);

    const size = resolved.size;
    const cells = [];
    const freeIndex = resolved.freeSpace
      ? Math.floor((size * size) / 2)
      : -1;

    let p = 0;
    for (let i = 0; i < size * size; i++) {
      if (i === freeIndex) {
        cells.push({ text: FREE_LABEL, free: true });
      } else {
        cells.push({ text: picked[p++], free: false });
      }
    }

    return { size: size, freeSpace: resolved.freeSpace, cells: cells };
  }

  // Generate a full batch of cards. Returns:
  //   { ok, error?, seed, gridSize, freeSpace, cardCount, cards: [...] }
  function generateCards(rawWordsOrList, opts) {
    opts = opts || {};
    const words = Array.isArray(rawWordsOrList)
      ? rawWordsOrList
      : parseWords(rawWordsOrList);

    const resolvedSettings = resolveSettings(words, opts);
    if (!resolvedSettings.ok) {
      return { ok: false, error: resolvedSettings.error };
    }

    const seed = opts.seed == null || opts.seed === '' ? '0' : String(opts.seed);
    const resolved = {
      size: resolvedSettings.gridSize,
      freeSpace: resolvedSettings.freeSpace,
      cellsNeeded: resolvedSettings.cellsNeeded,
    };

    const cards = [];
    for (let i = 0; i < resolvedSettings.cardCount; i++) {
      cards.push(buildCard(words, resolved, seed, i));
    }

    return {
      ok: true,
      seed: seed,
      gridSize: resolved.size,
      freeSpace: resolved.freeSpace,
      cardCount: resolvedSettings.cardCount,
      cards: cards,
    };
  }

  // A short, human-friendly random seed (browser default / "new seed" button).
  function randomSeed() {
    return Math.random().toString(36).slice(2, 8).toUpperCase();
  }

  return {
    xmur3: xmur3,
    mulberry32: mulberry32,
    makeRng: makeRng,
    shuffled: shuffled,
    parseWords: parseWords,
    cellsNeeded: cellsNeeded,
    autoGridSize: autoGridSize,
    resolveSettings: resolveSettings,
    generateCards: generateCards,
    randomSeed: randomSeed,
    GRID_SIZES: GRID_SIZES,
    FREE_LABEL: FREE_LABEL,
  };
});
