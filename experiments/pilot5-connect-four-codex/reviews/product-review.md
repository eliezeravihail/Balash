# Independent product and acceptance review

## Execution evidence

For every anonymous case, I ran its documented commands from `implementation/`:

```sh
npm install && npm test && npm run build
```

All nine commands exited 0. Test totals were: case-01 15, case-02 12, case-03 17,
case-04 13, case-05 11, case-06 19, case-07 11, case-08 13, and case-09 16.
Each documented `npm run dev` also printed its ready/running URL before an intentional
three-second timeout stopped the persistent development server. There was therefore no
install, test, build, or start-command failure to record.

## Findings

### Difficulty is not always a human choice before a game

The dossier requires the human to choose Easy, Normal, or Hard *before each game*.
The following cases create an immediately playable game with a default difficulty,
without a user selection:

- **case-03:** `App` initializes a Normal game (`case-03/implementation/src/App.tsx:13`),
  and its board accepts human clicks whenever the initial state is human/active
  (`case-03/implementation/src/App.tsx:25-28`,
  `case-03/implementation/src/App.tsx:66-70`).
- **case-04:** `MatchController` creates a game and defaults its difficulty to Normal
  (`case-04/implementation/src/match.ts:24-29`); the application constructs that controller
  immediately (`case-04/implementation/src/main.ts:13`) and enables all non-full cells in
  the human's active game (`case-04/implementation/src/main.ts:71-85`).
- **case-06:** the initial state is a playable game while the separate difficulty state defaults
  to Normal (`case-06/implementation/src/App.tsx:15-18`); input is available on the initial
  human turn (`case-06/implementation/src/App.tsx:45-52`,
  `case-06/implementation/src/components/Board.tsx:19-22`).
- **case-09:** the controller defaults to Easy (`case-09/implementation/src/game/controller.ts:29-34`)
  and is constructed without an explicitly chosen option (`case-09/implementation/src/main.ts:8-14`).
  The renderer enables the board in that active human state (`case-09/implementation/src/game/render.ts:140-153`).

Two more cases require a Start/New Game click but still allow that click to begin a
Normal game that the application preselected, rather than one the human selected:

- **case-05:** Normal is marked selected in the initial markup
  (`case-05/implementation/index.html:20-26`), and Start directly uses that control value
  (`case-05/implementation/src/main.js:88-93`).
- **case-07:** Normal is checked by default (`case-07/implementation/index.html:18-27`),
  `selectedDifficulty()` falls back to Normal (`case-07/implementation/app.js:17-18`),
  and New Game starts that value (`case-07/implementation/app.js:69-75`).

Even where initial selection is required, the following New Game implementations carry the
previous selection into the next game without a new choice: case-02
(`case-02/implementation/src/controller.js:59-63`), case-03
(`case-03/implementation/src/App.tsx:16-23`, `case-03/implementation/src/App.tsx:71-73`),
case-04 (`case-04/implementation/src/main.ts:47-49`), case-05
(`case-05/implementation/src/main.js:95-105`), case-06
(`case-06/implementation/src/App.tsx:54-59`), case-07
(`case-07/implementation/app.js:69-75`), and case-09
(`case-09/implementation/src/game/controller.ts:41-47`).

This behavior is not covered by the independent protocol's required UI evidence, which
only asks that difficulty selection be visible. It is also not protected by an automated
test in these cases. The only implementations that reset to an explicit difficulty choice
for every New Game are case-01 (`case-01/implementation/src/application/session.ts:25-42`)
and case-08
(`case-08/implementation/src/main.ts:24-43`).

## Requirement evidence and remaining coverage limits

Source establishes the required visible UI in all cases: each renders a difficulty control,
a seven-column/six-row board, status/result information, and a New Game action. The relevant
rendering evidence is:

| Case | Source evidence for visible controls and board |
| --- | --- |
| case-01 | `case-01/implementation/src/ui/render.ts:30-63`, `case-01/implementation/src/ui/render.ts:67-89` |
| case-02 | `case-02/implementation/src/main.js:17-53`, `case-02/implementation/src/main.js:56-75` |
| case-03 | `case-03/implementation/src/App.tsx:53-74`, `case-03/implementation/src/components/Board.tsx:17-44` |
| case-04 | `case-04/implementation/src/main.ts:15-32`, `case-04/implementation/src/main.ts:71-89` |
| case-05 | `case-05/implementation/index.html:18-42`, `case-05/implementation/src/main.js:33-62` |
| case-06 | `case-06/implementation/src/App.tsx:61-79`, `case-06/implementation/src/components/Board.tsx:15-33` |
| case-07 | `case-07/implementation/index.html:18-35`, `case-07/implementation/app.js:36-67` |
| case-08 | `case-08/implementation/index.html:20-39`, `case-08/implementation/src/main.ts:132-159` |
| case-09 | `case-09/implementation/src/game/render.ts:51-129`, `case-09/implementation/src/game/render.ts:132-156` |

The passing suites contain rule tests for horizontal, vertical, both diagonal wins, a draw,
full-column rejection, and terminal rejection; they also contain either a shared-transition
test or a direct trace for human and computer moves. Representative complete acceptance
evidence is: case-01 `src/domain/game.test.ts:18-63` and
`src/application/session.test.ts:16-26`; case-02 `test/game.test.js:21-70` and
`test/controller.test.js:21-57`; case-03 `src/game/game.test.ts:9-66` and
`src/App.test.tsx:53-60`; case-04 `src/game.test.ts:21-63` and
`src/match.test.ts:6-22`; case-05 `test/game.test.js:21-94`; case-06
`tests/rules.test.ts:9-75` and `tests/App.test.tsx:36-47`; case-07
`test/connect-four.test.js:97-158`; case-08 `tests/game.test.ts:22-92` and
`src/main.ts:73-121`; and case-09 `tests/rules.test.ts:30-105` and
`tests/controller.test.ts:20-79`.

The automated coverage is weaker at the browser boundary in cases 01, 02, 04, 05, 07, and
08: their test suites do not execute the rendered UI. Source is sufficient to establish the
controls listed above, but it would not catch regressions in their DOM wiring or presentation.
For the difficulty-selection finding, case-03's UI test explicitly treats the default Normal
game as the initial playable state (`case-03/implementation/src/App.test.tsx:26-31`), and
case-06's UI test likewise begins play before selection is required
(`case-06/implementation/tests/App.test.tsx:22-33`); neither detects the dossier violation.
