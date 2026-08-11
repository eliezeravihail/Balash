# Connect Four

A browser-only, one-player Connect Four game. You play red circles; the computer plays gold diamonds. There is no backend, account, network API, or persistence.

## Install, test, build, and run

```bash
npm install
npm test
npm run build
npm run dev
```

`npm run dev` prints the local URL to open in a browser. `npm run build` writes a deployable static site to `dist/`; use `npm run preview` to inspect that build locally.

Choose Easy, Normal, or Hard before dropping the first piece. Easy chooses a random legal column. Normal takes a direct win or blocks an immediate human win. Hard uses a deterministic depth-5 alpha-beta minimax search; equal scores retain the first center-first candidate in the fixed order `3, 2, 4, 1, 5, 0, 6`.

All player moves, including computer simulations, use the same `applyMove` game-rule transition. A column that is full, an out-of-turn move, and every move after the game ends are rejected without changing game state.
