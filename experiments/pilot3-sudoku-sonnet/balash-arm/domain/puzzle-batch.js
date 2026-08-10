// domain/puzzle-batch.js
//
// PuzzleBatch: an ordered list of Puzzles plus the (Seed, Difficulty,
// count) that produced them. Pure data -- the reproducible, shareable
// unit ("give someone this seed+difficulty+count and they get this exact
// batch"). Does not itself verify anything; it only ever holds Puzzle
// instances, which are already verified-unique by construction (D2).

export class PuzzleBatch {
  constructor(seed, difficulty, count, puzzles) {
    this.seed = seed;
    this.difficulty = difficulty;
    this.count = count;
    this.puzzles = puzzles;
  }
}
