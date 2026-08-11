# Connect Four implementation plan

## 1. Product and implementation decisions

Build a single-page, browser-only Connect Four game using **React 18, TypeScript, Vite, Vitest, and React Testing Library**. This stack gives a compact static production build, a responsive declarative UI, and fast unit/component tests. Use plain CSS (one application stylesheet) rather than a component framework so the visual presentation has no network or third-party runtime dependency.

The game rules will live in a pure TypeScript domain module, completely independent of React. The UI and the computer opponent must both call the same `applyMove` function; no component may write board cells directly. This is the key design choice for enforcing the shared-rules-path invariant.

All state is in memory; do not add a server, persistence, login, API calls, analytics, or remote-multiplayer code.

## 2. Project bootstrap and file layout

Create the application with Vite's `react-ts` template, then add test dependencies:

```text
connect-four/
├── package.json
├── vite.config.ts                 # Vite plus Vitest/jsdom configuration
├── tsconfig.json
├── index.html
├── src/
│   ├── main.tsx                   # React entry point
│   ├── App.tsx                    # application state orchestration and page layout
│   ├── styles.css                 # responsive visual styling and accessible focus states
│   ├── game/
│   │   ├── types.ts               # shared types and constants
│   │   ├── rules.ts               # pure board creation, legal moves, move application, outcome logic
│   │   ├── ai.ts                  # Easy, Normal, and Hard legal-column selection
│   │   └── evaluation.ts          # Hard-mode heuristic only (kept separate from rules)
│   ├── components/
│   │   ├── Board.tsx              # 7-column grid and column controls
│   │   ├── Cell.tsx               # presentational piece/cell
│   │   ├── GameStatus.tsx         # turn/result/difficulty text
│   │   └── DifficultyPicker.tsx   # difficulty selector and New Game action
│   └── test/
│       └── setup.ts               # Testing Library matcher setup
└── tests/
    ├── rules.test.ts
    ├── ai.test.ts
    └── App.test.tsx
```

Install `vitest`, `jsdom`, `@testing-library/react`, `@testing-library/jest-dom`, and `@testing-library/user-event` as development dependencies. Add scripts:

```json
{
  "dev": "vite",
  "build": "tsc -b && vite build",
  "preview": "vite preview",
  "test": "vitest run",
  "test:watch": "vitest"
}
```

Configure Vitest with `environment: 'jsdom'`, a setup file, and test discovery for `tests/**/*.test.{ts,tsx}`. Keep TypeScript strict mode enabled.

## 3. Domain model and rules API

Use these explicit types in `src/game/types.ts`:

```ts
export const ROWS = 6;
export const COLUMNS = 7;
export type Player = 'human' | 'computer';
export type Cell = Player | null;
export type Board = readonly (readonly Cell[])[]; // rows indexed top (0) to bottom (5)
export type Difficulty = 'easy' | 'normal' | 'hard';
export type GameResult = { kind: 'playing' } | { kind: 'won'; winner: Player; line: readonly Position[] } | { kind: 'draw' };
export interface Position { row: number; column: number }
export interface GameState { board: Board; turn: Player; result: GameResult; moveCount: number }
```

Represent the board as six immutable row arrays, top to bottom. Each row always contains exactly seven cells. `createGame()` returns an empty board with `turn: 'human'`, `{ kind: 'playing' }`, and `moveCount: 0`.

Expose the following pure functions from `rules.ts`:

| Function | Contract |
| --- | --- |
| `createGame()` | Creates the initial valid state. |
| `getLegalColumns(board)` | Returns ascending, non-full column indices (0–6). |
| `isLegalMove(state, column)` | True only while playing and for a legal integer column. |
| `applyMove(state, column, actor)` | The **only** mutation transition: returns a new state after a legal current-turn move, otherwise returns the original state object unchanged. |
| `findDropRow(board, column)` | Finds the lowest empty row or returns `null` for a full/invalid column. |
| `findWinningLine(board, lastMove)` | Detects a contiguous four-or-more run through the supplied latest piece in all directions. |
| `getResult(board, lastMove)` | Returns win, draw, or playing after a valid move. |

`applyMove` must validate, in this order: game is playing; actor equals `state.turn`; column is an integer from 0 through 6; column has an empty cell. On rejection, return the exact original state and do not alter turn/result/move count. On acceptance, clone only the changed row and board, insert at `findDropRow`, call `getResult`, increment the count, and set `turn` to the opposing player only if the result remains `playing`.

For win detection, inspect four direction pairs starting from the just-dropped cell: horizontal `(0,1)`, vertical `(1,0)`, descending diagonal `(1,1)`, and ascending diagonal `(1,-1)`. Count matching owner pieces forward and backward; when a run is at least four, return four consecutive positions including the latest move (prefer the first deterministically discovered direction/run). This supports highlighted winning cells while meeting all win rules. A full board after a non-winning move is a draw.

Do not independently encode gravity, full-column checks, or win detection in the UI or AI.

## 4. Computer-opponent design

Expose one public function from `ai.ts`:

```ts
chooseComputerColumn(state: GameState, difficulty: Difficulty, random?: () => number): number | null
```

It may only be called when `state.turn === 'computer'` and the game is playing. Return `null` otherwise. In every mode, derive choices from `getLegalColumns(state.board)` and validate the final return against that list; this guarantees that AI never returns an illegal/full column.

- **Easy:** choose `Math.floor(random() * legalColumns.length)`. The optional random function defaults to `Math.random`; inject a deterministic stub in tests.
- **Normal:** inspect legal columns in ascending order. First, simulate `applyMove(state, column, 'computer')` and return the first that wins for computer. If none, create a simulated state with turn set to human solely for threat analysis and find the first human immediate win, returning that column to block it. Otherwise use the Easy selection method. Simulations use `applyMove`, never raw board writes.
- **Hard:** use deterministic, depth-limited minimax with alpha-beta pruning. Set fixed search depth to **5 plies** (computer move plus four subsequent half-moves). At each node, generate moves using `getLegalColumns`, ordered center-first as `[3, 2, 4, 1, 5, 0, 6]` filtered to legal choices. Apply every simulated move through `applyMove`.
  - Terminal score: computer win `+1_000_000 + remainingDepth`; human win `-1_000_000 - remainingDepth`; draw `0`.
  - At the depth limit, calculate a stable heuristic: center-column occupancy (computer positive, human negative) plus open windows of four containing no opponent pieces, weighted 1/10/100 for one/two/three pieces. Iterate windows in a fixed horizontal, vertical, diagonal order.
  - At every equal score, retain the first move in the specified center-first order. This is the documented tie-break rule.
  - If a defensive time guard is desired, use a generous `performance.now()` budget and return the best completed root move; however, do not make ordinary behavior time-dependent. Depth five with alpha-beta on 7×6 is bounded and should be comfortably interactive. The default implementation should rely only on the fixed depth for reproducibility.

Keep the `evaluation.ts` heuristic pure and test it separately only if it contains enough logic to merit direct tests. The outcome functions, rather than heuristic scores, decide every terminal game result.

## 5. React state flow and UI

`App` owns `game: GameState` and `difficulty: Difficulty` (`'normal'` initially). Difficulty selection is enabled only before the first move; this naturally satisfies “chosen before each game”. The selected difficulty remains visible throughout a game, but changes are disabled once `moveCount > 0`. `New Game` creates a fresh game and re-enables selection.

On a human column activation:

1. Return immediately unless the state is playing and it is the human turn.
2. Call `applyMove(currentGame, column, 'human')` once.
3. Commit the returned state. If rejected (same state), make no UI change.
4. If it remains a playing game with computer turn, schedule one short `setTimeout` (about 250 ms) to make the opponent's turn visually legible. During this pending state, all board controls are disabled.
5. In the callback, use the current game state, call `chooseComputerColumn`, then `applyMove(game, selectedColumn, 'computer')` if a column was returned. Commit the result. Clear the timeout on unmount and when starting a new game so a stale AI turn cannot modify a reset board.

Use a safe functional state update in the callback, rechecking `turn`, result, and a per-game sequence/token before applying the delayed computer move. This avoids stale closure/race behavior when a user starts a new game during the delay.

The `Board` renders visually as six rows of seven circular cells. Each column has an accessible button (for example, `aria-label="Drop piece in column 4"`) spanning/associated with its cells; this works with mouse, touch, and keyboard. A column control is disabled when any of the following are true: the game is complete, it is computer's turn, an AI turn is pending, or that column is full. `Cell` uses distinct visual classes for human and computer pieces, an empty-state appearance, and a winning-cell highlight when `result.kind === 'won'` and its position is in `line`.

Show, at all times:

- Title/instructions identifying the human and computer colors.
- Easy, Normal, and Hard radio inputs with labels; the selected choice is exposed through normal checked state.
- Current turn while playing (including a concise “Computer is thinking…” during the delay).
- A result message: “You win”, “Computer wins”, or “Draw”.
- A clearly labeled `New Game` button.

Use semantic `main`, heading, `fieldset`/`legend` for difficulty, buttons for all game actions, and a live `role="status"` region for turn/result changes. CSS must provide visible focus indicators, high text/color contrast, non-color labels or patterns to distinguish pieces, responsive layout for narrow screens, and no fixed desktop-only width.

## 6. Automated-test plan

Use pure rules tests to construct positions solely by legal alternating `applyMove` calls. This both tests realistic game evolution and prevents accidental reliance on impossible board layouts.

`tests/rules.test.ts` must cover all acceptance cases explicitly:

1. **Horizontal win:** a legal sequence produces a four-across human win, result winner is human, and state is completed.
2. **Vertical win:** a legal sequence produces a four-high winner.
3. **Descending diagonal win:** a legal sequence produces `\\` four-in-a-row.
4. **Ascending diagonal win:** a legal sequence produces `/` four-in-a-row.
5. **Draw:** use a verified 42-move non-winning sequence that fills every cell; assert `kind === 'draw'`, no legal columns, and `moveCount === 42`.
6. **Full-column rejection:** fill one column legally without ending the game, attempt its next valid actor move, assert strict identity equality with pre-move state and deep equality of board, turn, result, and count.
7. **No moves after completion:** create a winning game, then attempt a move by each actor; assert each is the original completed state.
8. **Shared rule entry point:** spy/mock or instrument `applyMove` at the module boundary. Assert both a human interaction and an AI-selected computer move cause the same exported rule transition to be used; also assert the AI simulation is rules-based. If test tooling makes module spying brittle, inject an `applyMove` dependency into a small `createGameController`/AI adapter and assert calls instead. Do not satisfy this requirement merely by testing two duplicated move implementations.

Add focused edge tests for out-of-range/non-integer columns, wrong actor/turn rejection, and `getLegalColumns` order. Add `tests/ai.test.ts` cases with injected RNG: Easy returns a legal column; Normal chooses a direct winning move; Normal blocks an immediate human win; Hard returns a legal column on initial and constrained boards; Hard selects the documented first center-first candidate when scores tie. Avoid assertions that Hard always wins from arbitrary positions.

`tests/App.test.tsx` should render the app with fake timers or a zero-delay injectable scheduler. Verify initial difficulty/turn visibility, radio selection works before the first human move and is locked after it, a human click visibly places a piece then triggers one computer response, full/completed controls are disabled, result text is announced, and New Game restores an empty board and human turn. Do not make UI tests depend on uncontrolled randomness; inject/abstract the random source in the app/controller where needed.

Run the entire suite with `npm test`. Also run TypeScript/build verification via `npm run build`.

## 7. Implementation order

1. Scaffold Vite/TypeScript and package scripts; configure Vitest/jsdom and add the basic application entry/style import.
2. Implement the types, board factory, legal-move helpers, and immutable `applyMove` transition first.
3. Implement winning-line and draw detection, then write and pass all eight required rules tests (including a checked draw sequence) before building UI.
4. Implement Easy and Normal AI using only rules simulations, with deterministic tests.
5. Implement the ordered depth-5 alpha-beta Hard AI and its fixed heuristic/tie-break tests; confirm it consistently returns quickly and legally from opening and mid-game boards.
6. Build the accessible components and App state machine, including delayed AI scheduling and reset-token cleanup.
7. Add component/integration tests and complete responsive/focus/win-highlight styling.
8. Run lint/type/build/test commands, manually play one game at each difficulty, and correct any behavior found.

## 8. Build, test, and run handoff

Document these exact commands in `README.md`:

```bash
npm install
npm test
npm run build
npm run dev
```

`npm run dev` starts Vite's local development server and prints the local URL to open in a browser. `npm run build` produces a deployable static site in `dist/`; inspect it locally with `npm run preview`. The README should state that the game has no backend and that the fixed Hard search is depth 5 with center-first ordering `3,2,4,1,5,0,6` as its tie-break.

Final verification checklist:

- `npm test` passes, including every acceptance scenario listed above.
- `npm run build` exits successfully with no TypeScript errors.
- Each difficulty starts a fresh game and produces only legal computer moves.
- A full column and any completed board ignore further move attempts without state change.
- The page remains usable via keyboard and at a narrow mobile viewport.
