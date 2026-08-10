// generate — the core entry point (D1). PURE: no document, no window, no dates,
// no Math.random. Its inputs are values; its output is a Result<CardSet,
// GenerationError> (D6). It wires pool sampling + arrangement + distinctness
// through the single seeded RNG (D4), and the size rule lives entirely in
// selectGridSize (D3).
//
//   generate(words, settings, seed) → Result<CardSet, GenerationError>
//
//   words    : a WordList, OR raw text / array of raw lines (built via WordList)
//   settings : { cardCount }
//   seed     : a Seed value

import { ok, err } from './result.js';
import { GenerationError } from './errors.js';
import { WordList } from './wordlist.js';
import { selectGridSize } from './gridsize.js';
import { CardSet } from './cardset.js';
import { Rng } from './rng.js';

export function generate(words, settings, seed) {
  // Accept a prebuilt WordList (so the UI can build once and read stats) or
  // raw input (so the core is usable standalone). WordList owns all cleaning.
  const wordList = words instanceof WordList ? words : WordList.build(words).wordList;

  const cardCount = settings?.cardCount;
  if (!Number.isInteger(cardCount) || cardCount < 1) {
    return err(GenerationError.invalidCardCount(cardCount));
  }

  // The one owner of the size rule; a typed refusal when there are too few words.
  const sized = selectGridSize(wordList.size);
  if (!sized.ok) {
    return err(sized.error);
  }
  const gridSize = sized.value;

  // The single guarded randomness path: one seeded RNG derived from the seed.
  const rng = new Rng(seed.toUint32());

  const cardSet = CardSet.build({
    gridSize,
    seed,
    pool: wordList.words,
    requestedCount: cardCount,
    rng,
  });

  return ok(cardSet);
}
