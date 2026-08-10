# Pilot #2 — design-first (Balash) vs. a plain session, on a web product

The second pilot of the current thesis, on a deliberately **different domain** from
[pilot #1](../design-first-vs-direct/) (a Python CLI): here both arms built the same standalone
**static-web printable bingo-card generator** (paste a word list → a deterministic batch of printable
cards; no gameplay). It follows the same method — product information held constant across arms, both
final codebases judged blind by two reviewers with **opposite** dispositions, then the judges
scrutinized against source (see [`../design-first-vs-direct/CHARTER.md`](../design-first-vs-direct/CHARTER.md)).

The Balash arm is the real deliverable and was shipped as a draft PR to the product's own repository
(`MazeForge`); the plain-session arm was built only for this comparison.

## Contents

- [`FINDINGS.md`](FINDINGS.md) — the result and the **cross-pilot synthesis** (what pilots #1 and #2
  agree on now that N = 2 on two different domains).
- [`balash-arm/`](balash-arm) — the design-first condition: the shipped code plus its `DESIGN.md` (the
  design objective's artifact, produced and evaluated before implementation). `node test/core.test.js` → 19 pass.
- [`direct-arm/`](direct-arm) — the plain-session condition. `node test/bingo.test.js` → 13 pass.
- [`verdicts/`](verdicts) — the two blind reviews (OO-quality prior; pro-simplicity/YAGNI prior) and
  [`claim-verification.md`](verdicts/claim-verification.md) (every load-bearing judge claim checked
  against the source).

## Result

**Both blind judges chose the Balash arm** — ~8/10 (OO prior) and ~65% (pro-simplicity prior, "actively
looking to punish X for its file count"). Robust to disposition, as in pilot #1.

The decisive, source-verified difference: the **plain arm can silently hand two players identical bingo
cards** — the within-batch distinctness guarantee has no home; it builds cards from per-card sub-seeds
and hopes they differ. The Balash arm owns and enforces it (reject-and-redraw on a card fingerprint,
plus honest truncation reporting when the word pool is too shallow). Both judges also docked the Balash
arm for real over-engineering at the edges (triplicated construction-token guards, a dead method) — it
is sound at the center, ceremony at the seams.

See `FINDINGS.md` for the mechanism (why making design the goal surfaced the guarantee the feature
framing let evaporate) and the honest limits (still N = 2, one operator).
