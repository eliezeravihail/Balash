// domain/difficulty.js
//
// Difficulty: the rule for "how hard." A closed set of named levels
// (Easy/Medium/Hard), each owning a target given-count band. Exposes
// isSatisfiedBy(puzzle) so the generator asks Difficulty to judge a
// candidate rather than hardcoding thresholds inline. Changing what
// "Hard" means is a one-file change.
//
// Modeled as a given-count band, not a technique-rating engine (naked
// singles / hidden pairs / requires-guessing) -- deliberately not
// over-built for a static printable-puzzle page. Bands below are
// approximate targets, not hard guarantees about human-perceived
// difficulty.

const LEVEL_DEFS = [
  { key: 'easy', name: 'Easy', min: 38, max: 45 },
  { key: 'medium', name: 'Medium', min: 30, max: 36 },
  { key: 'hard', name: 'Hard', min: 24, max: 28 },
];

function makeLevel(def) {
  return Object.freeze({
    key: def.key,
    name: def.name,
    min: def.min,
    max: def.max,
    // Accepts either a Puzzle (has .givenCount()) or a raw number.
    isSatisfiedBy(puzzleOrCount) {
      const count = typeof puzzleOrCount === 'number' ? puzzleOrCount : puzzleOrCount.givenCount();
      return count >= def.min && count <= def.max;
    },
  });
}

const LEVELS_BY_KEY = new Map(LEVEL_DEFS.map((def) => [def.key, makeLevel(def)]));

export const Difficulty = Object.freeze({
  Easy: LEVELS_BY_KEY.get('easy'),
  Medium: LEVELS_BY_KEY.get('medium'),
  Hard: LEVELS_BY_KEY.get('hard'),

  all() {
    return [...LEVELS_BY_KEY.values()];
  },

  byKey(key) {
    return LEVELS_BY_KEY.get(key) ?? null;
  },
});
