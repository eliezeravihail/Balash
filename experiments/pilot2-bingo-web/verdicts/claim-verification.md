# Scrutiny of the blind judges — claim verification against source (pilot #2, bingo)

Private key: X = balash-arm (design-first), Y = direct-arm (plain session).

Both judges' verdicts rest on one decisive, checkable claim. Per the charter, a verdict is not a
result until its load-bearing claims are verified in the actual code.

| # | Claim | Direction | Verified? | Evidence |
|---|---|---|---|---|
| 1 | Y (Direct) makes NO within-batch distinctness guarantee — builds exactly `cardCount` cards from per-card sub-seeds and can return two identical cards; no fingerprint check, no truncation | against Y (decisive) | **YES** | `bingo.js` `generateCards` loops `cardCount` times calling `buildCard(words,resolved,seed,i)` with sub-seed `seed+'::card::'+i`; returns them verbatim. No dedup/fingerprint/ceiling anywhere in the card path. |
| 2 | The `seen`/dedupe logic Y *does* have is for the WORD LIST, not cards | context | **YES** | `bingo.js:70` `const seen = new Set()` is inside `parseWords` (input cleaning), unrelated to card distinctness |
| 3 | X (Balash) enforces distinctness (reject-and-redraw on `fingerprint`) and reports truncation | for X | **YES** | `src/core/cardset.js`: `maxDistinctCards` ceiling, `target=min(requestedCount,ceiling)`, fingerprint-collision reject-redraw, `isTruncated`/`producedCount` |
| 4 | X's core is genuinely DOM-free | for X | **YES** | grep of `src/core/` for document/window/Math.random/Date/localStorage → empty |
| 5 | X is over-built in spots: triplicated `Symbol` construction-token guards; `WordList.supports()` is dead code | **against X** | **YES** | `Symbol(` present in gridsize.js, seed.js, wordlist.js; `supports()` defined but never called by `generate()` |

## Reading

All five load-bearing claims verify, in both directions — the decisive point against Y, the strengths
of X, AND the over-engineering both judges docked X for. Neither judge confabulated. The decisive
finding is a real, source-confirmed design gap with a product consequence (two players can receive
identical bingo cards), not a stylistic preference for more types.
