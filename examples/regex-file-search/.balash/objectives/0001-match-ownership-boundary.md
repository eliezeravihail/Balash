# Objective 0001 — match-ownership-boundary

**Kind:** design

**Status:** reviewed

**Objective:** Establish one clear owner for "does this file match" (the filename-or-content
predicate), kept independent of how the tree is walked and how results are reported — so matching
logic exists in exactly one place, content is read only when the filename check didn't already
satisfy the match, and traversal/CLI concerns cannot silently duplicate or drift from the matching
rule.

**Why now:** This is the first objective of a new product. The problem statement bundles three
naturally distinct responsibilities — (a) deciding whether a single file matches, (b) walking a
directory tree while tolerating bad entries, (c) parsing CLI input and printing results — and a naive
first pass reliably tangles them (e.g. the walker re-implementing the OR check inline, or reading
every file's content even when the filename already matched). Establishing the ownership boundary now
is what makes objective 0002 (implementation) a fill-in-the-shape exercise instead of a redesign.

**Exit criteria:**
- [ ] One clear owner exists for the filename-or-content match rule, independent of tree traversal and
      of CLI/output code.
- [ ] The design short-circuits: a file whose name already matches does not have its content read.
- [ ] Traversal concerns (skip symlinks, tolerate one unreadable/bad entry without aborting the rest)
      are owned separately from the match predicate itself.
- [ ] The CLI/output layer depends on the matcher+walker through a boundary; it does not reach into
      regex or file-reading internals directly.
- [ ] The design is concrete enough to implement in Go against stdlib only, without the Guide having
      prescribed exact type or function names.

**Preserve:**
- The OR invariant: a file is reported iff its filename matches the regex or its content matches the
  regex (`.balash/knowledge.md` Invariants).
- Go, standard library only — no third-party dependency.
- The stated explicit non-goals (no multi-regex, no filename-only/content-only flags, no config file,
  no parallelism tuning) — do not design speculative extension points for these.

**Do not optimize for:**
- Performance/parallel traversal, exhaustive cross-platform edge cases, CLI flag richness beyond a
  regex and an optional root path, packaging or distribution.

## Worker handoff

ROLE
You are the implementation Worker — a senior engineer as capable as the Guide. The design is the
deliverable here, not working behavior. Do not redefine project priorities. If evidence invalidates
the objective, report it instead of expanding scope.

DESIGN GOAL (a quality outcome, not a feature)
Establish one clear owner for "does this file match" (filename-or-content, one regex), kept
independent of directory traversal and of CLI/output — so the match rule lives in exactly one place,
content is read only when necessary, and no other layer can silently reimplement or diverge from the
matching rule.

BEHAVIOR IT MUST SATISFY (a constraint on the design, not the thing to optimize)
- Given a regex and a root path, walking a directory tree must be able to determine, for each regular
  file, whether it matches: filename matches the regex, OR file content matches the regex.
- A file whose name already matches must not have its content read (short-circuit).
- One unreadable file/directory, or one symlink, must not abort traversal of the rest of the tree.
- The design must be implementable in Go using only the standard library (`regexp`, `path/filepath`,
  `os`, `bufio`, `io`).

WHY NOW
First objective of a new product; the three responsibilities above are naturally distinct and a naive
pass reliably tangles them (see Why now above).

WHAT "GOOD" AIMS AT
The standard is `references/design-principles.md` in the balash-guide skill this project was built
with (Guide: attach its content or a summary if the Worker cannot read it directly) — the target the
design should reach, not a checklist. Where a principle doesn't apply at this small a scale, it's fine
not to force it; be able to say why. This is a small tool — do not over-build. Prefer a boundary you
can name a real reason for over a speculative one.

RELEVANT CONTEXT / PRESERVE / NON-GOALS
- Grounded facts, invariants, and explicit non-goals in `.balash/knowledge.md` — read it.
- Go, stdlib only, is a settled day-zero decision, not open for reconsideration here.
- The modules, types, and functions are yours to choose. Design for what's here, not imagined futures
  (no plugin matcher system, no config format, no multi-regex support).

RETURN TO GUIDE
- The design: what owns the match decision, what owns traversal, what owns CLI/output, and how they
  relate — concrete enough to implement against (real function/type shapes are welcome, but this is
  still a design deliverable, not the final implementation).
- Your reasoning: why this boundary, what a second correct implementation of the matcher would still
  need to preserve, where the short-circuit lives and why it's safe.
- Result: met | partially_met | invalidated | blocked, against the design goal above.
- Any new facts or risks discovered (e.g. a Go stdlib limitation that changes the shape).

## Result

Worker self-reported **met**. Design document: `DESIGN.md` (repo root of this example). Three
packages — `match` (owns the filename-or-content decision, short-circuit inside `Matcher.Match`),
`walk` (owns traversal: symlink skip, per-entry error tolerance via `Result.Err`, consumer-defined
`FileMatcher` interface for testability without importing `match`), `main` (CLI/output, touches only
`match.New`/`walk.Walk`/`walk.Result`). New facts surfaced: `filepath.WalkDir` needs `io/fs` in
addition to the five packages the handoff named (still stdlib); `regexp.MatchReader` was rejected in
favor of line-oriented `bufio.Scanner` + byte-exact `regexp.Match` for UTF-8 safety, with the
disclosed tradeoff that a pattern spanning a line break won't content-match (grep-like, not
whole-file, semantics) — flagged for 0002/docs, not a blocker.

## Review

**Not just read — reproduced.** Pasted the design's sketched `match`/`walk`/`main` code verbatim into
a throwaway Go module and ran it for real, rather than accepting the Worker's self-report:

- `go build ./...` and `go vet ./...` — clean. The design is not just plausible prose; it compiles as
  given (one addition needed: a trivial `parseArgs` stub, which the objective never asked the design
  to specify — arg parsing is 0002's job).
- Fixture probe, `needle` pattern: `other.log` (content match) reported; `blob.dat` — a file
  containing the literal string "needle" but starting with a NUL byte — **not** reported. Confirms the
  binary heuristic and that content-matching is genuinely skipped for it, not just documented as such.
- Fixture probe, `plain` pattern: `plain.txt` reported by filename. Code-level confirmation the
  short-circuit branch (`filepath.Base` check before any `os.Open`) is the one that fires — no content
  I/O is reachable before it returns.
- Fixture probe, `hello` pattern, with `link.txt` a symlink to `plain.txt` (whose content matches
  "hello"): only `plain.txt` reported, **not** `link.txt`. This is the sharpest probe — it proves
  `d.Type()&fs.ModeSymlink` skip actually prevents the walk from ever calling `Match` on the symlink,
  not merely that the design document claims it does.
- Permission-error tolerance (exit code 1, `walk` continuing past a bad entry) was verified by code
  reading only — `filepath.WalkDir`'s documented contract (`err != nil` on the callback → returning
  `nil` continues the walk; `d` may be unpopulated) — not by a live reproduction, because this sandbox
  runs as `root`, where `chmod 000` does not actually deny access. Not a defect in the design; a
  sandbox limitation. 0002 should still carry a unit test for this path using a `walk.FileMatcher` test
  double that returns an error, which doesn't need real permission denial to exercise.

**Exit criteria — measured, not self-reported:**
- [x] One clear owner for the match rule, independent of traversal/CLI — confirmed by import graph
      (`match` imports neither `walk` nor is imported for logic by `main` beyond `New`/`Match`) and by
      the binary-exclusion probe above (the rule only ever executes inside `Matcher`).
- [x] Short-circuit: filename match skips content read — confirmed structurally (single `if` before
      any `os.Open`) and did not need a probe beyond the code path being unreachable otherwise.
- [x] Traversal (symlink skip, per-entry error tolerance) owned separately from matching — confirmed
      by the symlink probe (proves behavior, not just placement) and by code reading for error
      tolerance.
- [x] CLI/output touches the boundary only — confirmed: `main.go`'s only imports are `match`, `walk`,
      stdlib `bufio`/`fmt`/`os`; no `regexp`, no `os.Open`/`os.ReadDir`.
- [x] Concrete enough to implement without the Guide prescribing names — the sketch already compiles;
      0002 has an unambiguous shape to fill in (arg parsing, tests, packaging) rather than a redesign.

**Subtractive pass (independent of the Worker's own, which reached the same conclusions on
`FileMatcher`, `Result`, and the deliberately-not-introduced `Matcher` interface):** agreed with all
three calls. Nothing in the design reads as ceremony for this scale — no interface exists without a
present, named consumer; the one struct (`Result`) is a flat boundary-transfer type, not a
faux-domain object.

**Reading: met.** All five exit criteria hold under reproduction, not just under the Worker's
narrative. Proceeding to objective 0002 (implementation) with this design as the agreed shape; the
line-oriented content-match limitation is carried forward as a documented, accepted tradeoff rather
than reopened.
