# Blind design review A — pure OO/design-quality reviewer (pilot #2, bingo)

Private key: X = balash-arm (design-first), Y = direct-arm (plain).

Same product, same spine (parse words → size grid → seeded mulberry32 → shuffle → render → print),
both DOM-free cores, both headless-tested. Difference is entirely how concepts are shaped:
X = a pure `src/core/` of 8 named-concept modules (WordList, Seed, GridSize, Card, CardSet, Rng,
GenerationError, Result) wired by generate.js; Y = two files (bingo.js free functions + app.js).

Per question (X / Y):
1. SRP: X strong (textbook). Y mostly good but `resolveSettings` does 4 jobs incl. message-authoring; `renderCard` mixes DOM+caption+heading.
2. Gen/DOM seam: X strong + real (returns CardSet value; render is a pure string-builder; a 2nd injected rng seam the test exploits). Y separated but coarser/leakier — app.js recomputes geometry from bare fields; seed-minting nondeterminism sits INSIDE the "pure" module.
3. Real types owning rules: X strong (token-gated WordList/GridSize/Card/CardSet/Seed → illegal states unrepresentable). Y weak — bare bags; rules live in free functions.
4. Tell-don't-ask: X tells (card.rows(), WordList.supports). Y asks (pulls card.cells/size, recomputes).
5. Rule ownership: X each rule one home. Y free-space rule computed in 3 places; **batch-distinctness rule lives NOWHERE**.
6. Bad input / can't-make-N-distinct: X typed Result + truncation as first-class data. Y ad-hoc {ok,error} string; "can't make that many" NOT handled at all.
7. Change one rule: X one place. Y usually, but free-space touches 3 sites, seed-sharing spread across 2 fns + a string literal.
8. Metz test: X's abstractions mostly earn their keep; over-built in the triplicated Symbol-token guards + overflow cap (cosmetic). Y under-abstracted exactly where a Card/CardSet was needed → the distinctness guarantee evaporated (a rule with no home — the more dangerous miss).

Best/worst — X best: partial-success as a first-class enforced outcome (CardSet reject-redraw + isTruncated). X worst: triplicated Symbol-token guards (speculative). Y best: right-sized 2-file simplicity + clean DOM boundary. Y worst: batch distinctness left to an unenforced sub-seed convention, no home for it.

VERDICT: **X better designed. Confidence high (~8/10), "not a close call."** X wins on structure, responsibility division, and object/seam shape. Deductions against X (token guards, overflow cap) are cosmetic; Y's simplicity crosses into a missing abstraction at the one place it mattered.
