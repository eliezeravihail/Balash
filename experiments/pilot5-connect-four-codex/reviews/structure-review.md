# Structural review

Reviewed the nine anonymous cases against `full-product-dossier.md` and
`acceptance.md`, including plans and implementation source. I ran each case's
documented `npm test`; all nine commands completed successfully. This is test
evidence only, not a substitute for the structural findings below.

## Material findings

### case-03 — difficulty selection is not an enforced pre-game prerequisite

The plan says the product has a difficulty choice before a game
(`case-03/PLAN.md:7`), but it also permits an initially created Normal game
(`case-03/PLAN.md:113-115`). The implementation immediately creates that active
game with Normal selected (`case-03/implementation/src/App.tsx:13`), renders an
enabled board (`case-03/implementation/src/App.tsx:66-70`), and accepts a human
move without a prior selection event (`case-03/implementation/src/App.tsx:25-28`).
Consequently, the builder foundation does not enforce the dossier's “human
chooses … before each game” lifecycle; it treats the default as a choice.

### case-04 — implementation bypasses the specified select-then-start lifecycle

The goals require the player to select a difficulty and start a match
(`case-04/GOALS.md:7-10`), and the architecture says the difficulty control is
presented before starting (`case-04/ARCHITECTURE.md:43-45`). In contrast, the
controller constructs an active, human-turn game with a default Normal
difficulty (`case-04/implementation/src/match.ts:24-28`), and the browser entry
constructs that controller without a setup gate (`case-04/implementation/src/main.ts:13`).
The rendered board enables every non-full column whenever the game is ongoing
(`case-04/implementation/src/main.ts:71-85`). The plan and code therefore
disagree on a core lifecycle boundary, allowing play before an explicit choice.

### case-06 — the plan redefines an explicit selection as a default, and the app follows it

The plan states that an initially Normal difficulty “naturally satisfies” the
before-each-game choice (`case-06/PLAN.md:113-115`), rather than defining a
selection/setup state. The app creates both an active game and a Normal
difficulty on mount (`case-06/implementation/src/App.tsx:15-18`) and permits a
human move immediately (`case-06/implementation/src/App.tsx:45-51`). This does
not enforce the dossier's stated pre-game choice, even though the selector
remains editable until the first move.

### case-09 — plan's selection-before-start rule is absent from the controller lifecycle

The plan requires difficulty selection before a game starts
(`case-09/PLAN.md:35-40`). The controller instead creates an active Easy game
during construction (`case-09/implementation/src/game/controller.ts:29-34`),
and the renderer exposes playable board controls whenever that active state is
on the human turn (`case-09/implementation/src/game/render.ts:140-152`). The
selector is only locked after a move (`case-09/implementation/src/game/render.ts:132-135`),
so it permits changing a default before play but never requires the human to
make a selection before the game exists.

### cases 02 and 09 — mutable state escapes the application boundary

Case-02 returns its live board reference from `getState`
(`case-02/implementation/src/controller.js:33-43`) and sends that same
reference to each listener (`case-02/implementation/src/controller.js:181-182`).
A renderer or listener can therefore alter cells without the common
`applyMove` transition (`case-02/implementation/src/controller.js:90-133`).

Case-09 has the same boundary problem: `GameState` exposes a mutable
`Cell[][]` board (`case-09/implementation/src/game/types.ts:14-20`) and
`getState` returns that live object (`case-09/implementation/src/game/controller.ts:37-39`).
This also contradicts its plan's public-boundary immutability requirement
(`case-09/PLAN.md:55`). Both designs make rule enforcement contingent on
well-behaved renderers/consumers, rather than confining board mutation to the
authoritative transition.

## Cross-case structural assessment

No further material finding was identified for the requested boundaries:

- Each case routes the two live actor flows through a common transition; the
  routes are visible in cases 01 (`case-01/implementation/src/application/session.ts:48-60`),
  02 (`case-02/implementation/src/controller.js:76-95`), 03
  (`case-03/implementation/src/App.tsx:25-44`), 04
  (`case-04/implementation/src/match.ts:47-69`), 05
  (`case-05/implementation/src/main.js:68-85`), 06
  (`case-06/implementation/src/App.tsx:38-51`), 07
  (`case-07/implementation/app.js:77-95`), 08
  (`case-08/implementation/src/main.ts:73-121`), and 09
  (`case-09/implementation/src/game/controller.ts:62-105`).
- AI modules choose columns and the live coordinator commits them through those
  transitions; no inspected case had a separate AI board-write path. Difficulty
  is not branched on by the live rule transitions.
- The plans keep browser, policy, and rules concerns separated and do not add
  server/network or unrelated runtime dependencies. Apart from the four
  selection-lifecycle gaps above, they provide enough ownership, test, and
  Hard-policy detail for implementation without fixing the internal structure
  beyond what the product needs.
