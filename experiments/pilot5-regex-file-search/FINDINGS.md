# Findings: pilot #5 — regex-file-search, design-first (Balash) vs. a plain direct build

Same product, same language (Go, stdlib only, held constant across arms so the only variable is
process), built by two independent Worker delegations: **balash-arm** went through the full
`balash-guide` loop under the new `state.md`/`knowledge.md`/`objectives/` schema (a design objective,
reviewed met by direct reproduction, then an implementation objective conforming to it, also reviewed
met by direct reproduction — see `../../examples/regex-file-search/.balash/objectives/`). **direct-arm**
was built from a single plain feature request with no design framing, no ownership/boundary
constraint, no design-principles reference — the requirement stated as free text and nothing else.

Private key: **Arm A = balash-arm**, **Arm B = direct-arm**. The reviewer was given only the two
source trees, stripped of `README.md`/`DESIGN.md`/anything naming Balash, and explicitly instructed
not to search outside the two given directories.

## Result: the blind reviewer chose Arm A (balash-arm) on architecture, encapsulation, and interfaces

Both arms build clean (`go build`/`go vet`/`go test` all pass on both). The reviewer's verdict turned
on one reproducible, structural fact rather than taste:

> Arm A's `internal/walk/walk_test.go` tests all of traversal's policy (symlink skip, per-entry error
> tolerance, exactly-once matcher invocation) using a fake `FileMatcher`, with **zero** import of
> `regexp` or the `match` package. `internal/match/match_test.go` tests the entire match decision with
> **zero** directory traversal. Arm B cannot make either claim: every `search_test.go` case has to
> build a real directory tree and run the full `filepath.WalkDir` closure just to assert a matching
> outcome, because matching, traversal, symlink-target classification, and warning-formatting are
> fused into one ~50-line closure (`search.go:53-105`).

This was independently verified against source after the blind verdict (not taken on report): the
`match`-free import in `walk_test.go`, the fused decision logic in `search.go`'s `WalkDir` closure, and
every cited `file:line` were confirmed directly.

## The verdict is not one-sided — Arm A's real weaknesses, confirmed

- **Zero test coverage of `main.go`** (arg parsing, exit-code selection) in balash-arm — confirmed,
  no `main_test.go` exists anywhere in the arm. Arm B's `main_test.go` covers exactly this layer
  (usage errors, invalid regex, default root, end-to-end) and balash-arm has no equivalent.
- **A dangling doc reference**: `internal/walk/walk_test.go:8` says "see DESIGN.md §1.2" — confirmed
  present, and confirmed **unresolvable in the anonymized comparison copy**, because `DESIGN.md` was
  deliberately excluded from what the blind reviewer saw (it names the objective/process and would
  have de-blinded the comparison). **Important correction to the reviewer's framing**: this is an
  artifact of the blind-review methodology, not a real defect in the shipped product — `DESIGN.md`
  does exist alongside the real code at `../../examples/regex-file-search/DESIGN.md`, so the reference
  resolves fine for an actual reader of that repository. Recorded here for honesty, not held against
  balash-arm.

## Interpretation

Both are competent Go — this is not "the direct arm is bad code." The difference the reviewer
converged on is specifically the one the design objective (0001) explicitly set out to produce: a
testable seam between "does this file match" and "how do we walk the tree," reached by naming that as
the design goal *before* writing implementation code, rather than by discovering it might be a good
idea mid-implementation and not doing it. Arm B is a perfectly reasonable single-pass implementation of
the same requirement; it simply never had a moment where the ownership question was asked as its own
objective — matching logic and traversal logic grew together in one function because nothing forced
them apart.

## Honest limits of this run

- **Single reviewer, not opposite-disposition cross-checked.** Pilots #1–#4 used two blind reviewers
  with opposite priors (pure-OO vs. pro-simplicity/YAGNI) specifically to test whether a verdict is a
  taste artifact. This pilot ran one reviewer under the current `review-panel.md` discipline
  (reproduce-or-cite, no scores) and had its citations independently spot-verified by the Guide, but
  did not repeat the opposite-disposition check — a genuine gap if this needs to be load-bearing
  evidence rather than a demo answer to a direct question.
- **N=1 product**, a small CLI — the same caveat every prior pilot carries: this is suggestive, not a
  validated general result.
- The Guide (this session) both ran the balash-arm build *and* set up/read this comparison — not a
  fully independent operator, same confound noted in the main `README.md` §5.4.
