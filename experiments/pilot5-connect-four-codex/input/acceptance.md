# Independent acceptance protocol

The evaluator must use the project's documented install, test, build, and run commands.

Required evidence:

1. The project installs, tests, and builds using its documented commands.
2. Tests prove horizontal, vertical, both diagonals, draw, full-column rejection, and no moves after
   game completion.
3. One test or precise code citation proves that the human and computer submit moves through the same
   game-rule entry point.
4. The browser UI visibly supports difficulty selection, a playable 7 × 6 board, turn/result display,
   and New Game.
5. The computer chooses only legal moves at every difficulty.

Record each failure as a concrete command failure, failing test, reproducible interaction, or
`file:line` citation. Do not assign a composite score.
