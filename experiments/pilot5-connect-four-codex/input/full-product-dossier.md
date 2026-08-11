# Fixed product dossier

## Product

A complete browser-based Connect Four game for one human player against one computer opponent.

## Required behavior

- The board is 7 columns by 6 rows.
- The human chooses Easy, Normal, or Hard before each game.
- Human and computer alternate turns. The human chooses a non-full column; a piece falls to its
  lowest available cell.
- A game ends when either player creates four contiguous pieces horizontally, vertically, or on
  either diagonal, or when the board is full with no winner.
- The result, current turn, selected difficulty, and a New Game action are visible.
- Easy chooses a random legal column.
- Normal takes an immediate winning move, otherwise blocks the human's immediate winning move,
  otherwise chooses a random legal column.
- Hard uses a deterministic depth-limited minimax search with a documented fixed depth and a
  deterministic tie-break rule. It must always return a legal column within ordinary browser use.

## Product invariants

- Human and computer moves use the same game-rule entry point.
- Difficulty changes only the computer's choice of a legal move. It never changes board size,
  move legality, gravity, win detection, or game completion.
- A move into a full column is rejected and leaves the game unchanged.
- After completion no move is legal until New Game.

## Boundaries

- Version 1 runs entirely in the browser: no account, server, database, network API, or remote
  multiplayer.
- The stack is intentionally not prescribed. The agent must make and justify the necessary
  implementation decisions.

## Implementation acceptance

The completed product must document how to install, test, build, and run it. Its automated tests
must cover horizontal, vertical, both diagonal wins, draw, rejection of a full column, no moves after
completion, and the fact that both actor types enter the same rules path.
