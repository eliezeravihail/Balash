# Bingo Card Generator

A standalone static site that turns a list of words into a batch of
**printable** bingo cards. No backend, no build step, no third-party libraries.

The site does **not** run a game — there is no caller, no number drawing, no
marking, and no win detection. It only generates cards for printing.

## Run it

Just open `index.html` in a browser, or serve the folder:

```
python3 -m http.server 8000
# then open http://localhost:8000/
```

Paste words (one per line), pick options, click **Generate cards**, then
**Print** (or your browser's print command). Each card prints on its own page.

## How it works

- **Grid size adapts to the word count.** Auto mode picks the largest grid that
  fits: 3x3 needs 9 words, 4x4 needs 16, 5x5 needs 25. Fewer than 9 distinct
  words is an error; extra words are drawn from as a larger pool. You can also
  force a specific size.
- **Free center space** (optional) applies to odd grids (3x3, 5x5); it drops the
  word requirement by one and stamps a `FREE` cell in the middle.
- **Deterministic.** The same seed + words + settings always reproduce the exact
  same set of cards. The seed is shown and editable, so a card set is shareable
  by its seed.
- **A batch of distinct cards.** Each card uses a per-card sub-seed derived from
  the master seed and its index. When the word pool is larger than one card, the
  subset of words differs between cards; when it's exactly one card's worth,
  distinctness comes from the arrangement.

## Files

- `bingo.js` — pure, DOM-free generation logic (PRNG, parsing, sizing rules,
  validation, card building). Works in node and the browser.
- `app.js` — form/DOM wiring and card rendering.
- `index.html` / `styles.css` — UI and print layout.
- `test/bingo.test.js` — headless tests (node stdlib only).

## Test

```
node test/bingo.test.js
# or: npm test
```
