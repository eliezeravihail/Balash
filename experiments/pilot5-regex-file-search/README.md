# Pilot #5 — regex-file-search: design-first (Balash) vs. a plain direct build

Same product (a compiled Go CLI: report files whose name or content matches a regex), same language
held constant across arms, built by two independent Worker delegations and compared blind on
architecture/encapsulation/interfaces/cleanliness only (not features, not a bug hunt).

- [`FINDINGS.md`](FINDINGS.md) — the result, the reproduced evidence, and honest limits.
- [`balash-arm/`](balash-arm) — the design-first build (source copied from
  [`../../examples/regex-file-search/`](../../examples/regex-file-search/), which carries the full
  `.balash/` record of the loop that produced it).
- [`direct-arm/`](direct-arm) — a single plain feature request, no design framing.
- [`verdicts/blind/`](verdicts/blind) — the anonymized copies (`arm-a`/`arm-b`, source only, no
  README/DESIGN.md) actually shown to the blind reviewer.

**Result:** the blind reviewer picked Arm A (balash-arm), on a reproducible structural fact — its
`match`/`walk` split lets each side be unit-tested with zero dependency on the other, which
`direct-arm`'s fused traversal+matching closure cannot claim — while also surfacing real weaknesses in
the winning arm (no `main.go` test coverage). See `FINDINGS.md` for the full evidence and this pilot's
limits (single reviewer, not opposite-disposition cross-checked, N=1).
