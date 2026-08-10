# Blind design review B — pro-simplicity / YAGNI reviewer (pilot #2, bingo)

Private key: X = balash-arm (design-first), Y = direct-arm (plain). Reviewer prior: distrust
abstraction that doesn't pay for itself; extra layering guilty until proven innocent.

Same spine; honest behavioral diffs: X adds shareable-URL reproduction + a hard within-batch
distinctness guarantee with truncation reporting; Y adds a free-center option + manual size override
and makes NO distinctness guarantee. X ~10 core modules; Y two files.

1. Maintain: to hold in head, **Y wins** (bingo.js readable in 5 min). To change safely, **X wins**
   (the two hard requirements — determinism containment, "how many distinct cards can I make" — each
   have one clear owner). X ceremony that does NOT earn keep: the Symbol construction-token guards
   (gridsize/seed/wordlist); `WordList.supports()` is dead code; GridSize-as-full-frozen-class is heavy.
2. Defects under Y's flatness: `resolveSettings` braids normalize+validate+resolve; geometry leaks
   into DOM (app.js recomputes gridTemplateColumns from bare size); **the big one — no distinctness
   guarantee and nowhere for it to live**: 9 words→3×3 can yield two identical cards, undetected; the
   passing "cards differ" test passes probabilistically, not by construction.
3. X load-bearing (keep): cardset.js (the single most valuable module in either), card.js
   (fingerprint+rows), rng.js (injected seam), errors/result, the threshold table. Ceremony (cut):
   the Symbol tokens, WordList.supports(), the heavy GridSize class wrapper.
4. Specifics: gen/DOM seam edge X (small). Grid-size rule: slight edge X (exactly one owner).
   Determinism: tie (both reproducible), X marginally more explicit. "Can't make N distinct": **clear
   edge X, substance not tidiness** — Y doesn't address it at all.
5. VERDICT: **X better designed, moderate ~65%** — said "as someone actively looking to punish X for
   its file count." Win is NOT "X looks disciplined"; it's that the two genuinely hard requirements
   each have a correct single owner in X, and Y punts distinctness with no clean home. A batch product
   that can silently hand two players identical cards has a real design gap.
   WHAT WOULD FLIP IT TO Y: if within-batch distinctness were NOT a real requirement (read "printable
   cards" as decoration), X's CardSet/fingerprint/ceiling apparatus stops earning its keep, its edge
   shrinks to the token ceremony, and Y's two clean files win. Verdict hinges on whether distinctness
   is real; judged that it is.
