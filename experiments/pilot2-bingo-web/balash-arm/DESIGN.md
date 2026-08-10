# Deterministic Printable Bingo-Card Generator — Design

A static, backend-free web page: paste a word list, get a batch of printable bingo cards.
Same seed + same words + same settings → byte-identical cards, every time. No gameplay —
generation for print only.

## 1. Domain model

The domain is a small pure core with three real types. Each owns its own invariants; none
knows about the DOM, the browser, or how a card is drawn.

- **`WordList`** — a validated collection of playable words. Construction is the *only* place
  input rules live: it trims whitespace, drops blanks, collapses case-insensitive duplicates
  (keeping first spelling), and preserves supply order. It exposes `size` and a read-only
  ordered view, and it *decides* whether it can support a given grid (it is asked
  `supports(gridSize)`, not asked for its raw count so a caller can compare). A `WordList`
  that survives construction is by definition clean — downstream code never re-validates.

- **`GridSize`** — a value type wrapping the allowed set {3, 4, 5} with derived `cellCount`
  (9/16/25). It is not a bare `int`; it is the single answer to "how big is a card," and it
  is only obtainable through the selection rule (below), so an out-of-range size is
  unrepresentable.

- **`Card`** — one card: an immutable `GridSize` plus its cell contents in row-major order.
  It knows its own layout (dimensions, iteration by row) and can report its "fingerprint"
  (the ordered contents) so a `CardSet` can reason about distinctness. It carries no render
  logic — it *is* the data-with-rules, and it refuses to exist with the wrong number of cells.

- **`CardSet`** — the batch: the resolved `GridSize`, the `Seed` that produced it, and the
  ordered `Card`s. It owns the batch-level guarantee about how distinct cards are (§4). This
  is the shareable, reproducible unit — a `CardSet` is fully described by (words, settings,
  seed).

- **`Seed`** — a value type over the reproducibility token (see §5). Owns parse/format and
  the "same seed means same output" contract; never a loose string in the core.

Anemic-model check: every type above answers "what does it *do*," not just "what does it
hold." `WordList` validates and judges grid support; `GridSize` derives geometry; `Card`
enforces cell count and reports its fingerprint; `CardSet` enforces batch distinctness.

## 2. Boundaries — the one seam that matters

```
  UI / input layer  ──►  GENERATION CORE (pure)  ──►  Renderer (DOM/print)
   (reads the page)       words+settings+seed →         (CardSet → printable
                          CardSet                         HTML; print CSS)
```

The **generation core** (`WordList`, `GridSize`, the selection rule, the deterministic RNG,
`generate()` → `CardSet`) is pure: no `document`, no `window`, no dates, no `Math.random`.
Its only inputs are the values handed to it; its only output is a `CardSet`. This is the real
seam — a completely different output (a PDF writer, a plain-text dump, an SVG exporter, a test
harness that just diffs fingerprints) could sit behind it with zero core changes, because the
core hands back a `CardSet` and asks nothing about how it will be shown.

The **renderer** reads a `CardSet` and emits print-oriented HTML; page breaks and card sizing
live in a print stylesheet. It only *reads* the domain (tell-don't-ask: it asks a `Card` to
iterate its rows; it does not pull raw arrays and compute geometry itself).

The **UI layer** is the only code that touches the page: it reads the textarea and settings,
constructs the domain values, calls `generate()`, and asks the renderer to paint. It is
deliberately thin and holds no domain rules.

Determinism boundary: the seed→cards mapping lives *entirely* inside the core, driven by one
seeded RNG. Nothing non-deterministic is allowed in the core, so reproducibility is a property
of a single guarded path (principle 9), not something scattered across the app.

## 3. Grid-size selection rule (one owner)

Owner: a single pure function `selectGridSize(wordCount) → GridSize`, the *only* producer of
a `GridSize`. The rule, by supplied word count *n* (after cleaning):

- **n < 9** → not enough for even the smallest card → generation is refused with a clear,
  concept-level error ("Need at least 9 words for a 3×3 card; you have N"). The core returns a
  typed failure, not an exception the UI has to decode.
- **9 ≤ n < 16** → **3×3**
- **16 ≤ n < 25** → **4×4**
- **n ≥ 25** → **5×5** (largest supported; extra words are allowed and simply widen the pool
  each card samples from — see §4).

Rationale: bigger word lists earn bigger cards; the largest card that the list can *fully*
fill is chosen. "More than enough" is a feature (a deeper pool → more distinct cards), not an
error. The thresholds and the {3,4,5} ceiling are the two product knobs most likely to change,
and they live in exactly one function.

## 4. How cards differ, and the distinctness guarantee

Each card is an independent random draw of `cellCount` words from the `WordList`, then a random
arrangement of those words into the grid — both draws come from the same seeded stream, so the
whole batch is a deterministic function of the seed.

Guarantee, stated honestly and owned by `CardSet`:
- Within a single `CardSet`, no two cards are *identical* (same words in the same positions).
  The generator rejects-and-redraws a card whose fingerprint collides with one already in the
  set.
- We do **not** guarantee cards share no words, and we do not guarantee global uniqueness across
  different `CardSet`s or seeds — with a small pool that is combinatorially impossible and
  promising it would be a lie.
- If the pool is too shallow to produce the requested number of distinct cards (e.g. exactly 9
  words, 3×3, asking for many cards), the core stops at the maximum distinct count it can
  actually produce and reports how many it made and why. It never loops forever and never
  returns duplicates to hit a count.

Card count is a user setting (default e.g. 8) with a sane cap; the "how many can I actually
make distinct" ceiling is the core's business, surfaced as a result fact.

## 5. Seed: surfacing and sharing

- The seed is a short human-typable/​copyable token (a `Seed` value type owning its
  format). On first generate, if the user left it blank, the core is given a freshly minted
  seed by the UI (the *only* nondeterministic act, and it happens *outside* the core, then is
  fed in) and that seed is displayed prominently.
- The full reproducible state is (words, settings, seed). Sharing is by round-tripping all
  three: the URL query string encodes seed + settings, and the seed field is always shown and
  copyable. Re-running with the same three reproduces the exact `CardSet`. (Whether the word
  list itself rides in the URL or is re-pasted is an open question — see §8.)
- Because determinism lives in one seeded RNG inside the core, "shareable by seed" is a direct
  consequence of the architecture, not a bolted-on feature.

## 6. Bad-input handling (as decisions)

All input hygiene is `WordList`'s construction responsibility — one owner, so the rules can't
drift between the UI and the core:
- **Blanks / whitespace-only lines** → dropped silently.
- **Duplicates** (case-insensitive, post-trim) → collapsed to one; the UI *may* report how many
  were merged so the user isn't surprised the pool shrank.
- **Too few words (< 9)** → a typed, concept-level failure from `selectGridSize`, shown to the
  user in their terms.
- Leading/trailing whitespace trimmed; internal spacing preserved.

The core returns typed outcomes (a `CardSet`, or a named failure carrying the reason and
numbers); the UI translates those into messages. No raw exceptions cross the seam.

## 7. Module / responsibility skeleton (names only)

Core (pure, no DOM):
- `wordlist` — `WordList`: validate/clean/dedupe input; judge grid support.
- `gridsize` — `GridSize` value type + `selectGridSize(n)`: the size rule, sole `GridSize` source.
- `seed` — `Seed` value type: format/parse; reproducibility contract.
- `rng` — small seeded PRNG (e.g. a well-known 32-bit generator): the only randomness source.
- `card` — `Card`: immutable cells + geometry + fingerprint.
- `cardset` — `CardSet`: the batch and its distinctness guarantee.
- `generate` — `generate(words, settings, seed) → Result<CardSet, GenerationError>`: the core
  entry point; wires pool sampling + arrangement + distinctness through the seeded RNG.

Edges (impure):
- `render` — `CardSet` → printable HTML; delegates layout to `Card`.
- `print.css` — page-break / card-sizing rules for physical printing.
- `app` — reads the page + URL, builds domain values, mints a seed if blank, calls `generate`,
  invokes `render`, shows seed + any input-cleaning notices.

## 8. Open product questions

1. **Word list in the share link?** Encoding words in the URL makes a card set fully
   reproducible from one link but bloats the URL and is lossy for long lists. Alternative:
   share seed+settings only, and rely on the user pasting the same list. Which is the product's
   sharing story?
2. **Default and max card count** per batch (print/paper expectations).
3. **Free-space center cell** on odd grids (3×3, 5×5) — classic bingo has one; do we? It changes
   how many words a card needs and interacts with the size rule.
4. **Case/locale for duplicate detection** — is case-insensitive collapse right for all
   intended languages, and how are non-Latin scripts treated?
5. **Same words per card, or partitioned pool** when the list is large — should every card draw
   from the whole pool (words may repeat across cards) or should we try to spread usage?
