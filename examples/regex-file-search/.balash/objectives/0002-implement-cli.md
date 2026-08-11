# Objective 0002 — implement-cli

**Kind:** implementation

**Status:** reviewed

**Objective:** Implement the compiled Go CLI conforming exactly to the design agreed in objective
0001 (`DESIGN.md`), producing a working binary and a test suite that exercises the design's binding
decisions — not a redesign, a fill-in-the-shape build.

**Why now:** Objective 0001 was reviewed **met** (reproduced, not just read) — the design is sound and
concrete enough to build against. This objective turns it into real, tested, buildable software, which
is the whole point of the design → implement rhythm: implementation fills in an already-sound shape.

**Exit criteria:**
- [x] `go build ./...` succeeds from a clean checkout and produces a working binary.
- [x] Unit tests exist and pass for `match` covering: filename match short-circuits before any content
      read (observable, not just structural), content match via regex, binary files excluded from
      content matching, no match when neither side matches.
- [x] Unit tests exist and pass for `walk` covering: symlinks are never followed/passed to the matcher,
      one erroring entry does not abort traversal of the rest of the tree, the matcher is called
      exactly once per regular file — using a test-double `FileMatcher`, per the 0001 design's stated
      reason for that interface, without importing `match` into the `walk` tests.
- [x] The package boundaries from `DESIGN.md` are preserved exactly: `match` owns the match rule,
      `walk` owns traversal, `main`/CLI touches only `match.New`, `walk.Walk`, and `walk.Result` — no
      regex or file-reading logic duplicated into `walk` or `main`.
- [x] The binary, run against a real directory tree, reports exactly the files whose name or content
      matches a given regex and nothing else (the Guide reproduced this directly, not on report).

**Preserve:**
- Every invariant and non-goal in `.balash/knowledge.md`, including the accepted line-oriented
  content-match tradeoff from 0001 — do not silently change it to whole-file matching.
- Go, stdlib only.
- The three-package boundary from `DESIGN.md` — this objective conforms to it, it does not redesign it.

**Do not optimize for:**
- Extra CLI flags/features beyond `<pattern> [root]`, performance/parallel traversal, packaging or
  release tooling, cross-platform installers, a config file.

## Worker handoff

ROLE
You are the implementation Worker — a senior engineer as capable as the Guide. This is an
**implementation** objective conforming to a design already agreed and reviewed (objective 0001,
`DESIGN.md`) — the deliverable is real, working, tested code that fills in that shape. Do not redesign
the package boundaries; if you find the design genuinely cannot be implemented as agreed, stop and
report the conflicting evidence instead of quietly changing it.

DESIGN GOAL
Conform to the `match`/`walk`/`main` design in `DESIGN.md` — implement it as real Go source under
`/home/user/Balash/examples/regex-file-search/`, with tests that exercise its binding decisions
(short-circuit, symlink skip, per-entry error tolerance, binary exclusion), and make it build and run
as a compiled binary.

BEHAVIOR IT MUST SATISFY
- CLI usage: `regex-file-search <pattern> [root]` (root defaults to `.`), prints one matching file path
  per line to stdout.
- A file is reported iff its filename matches `<pattern>` (RE2 syntax) or its content matches it
  (line-oriented, per the 0001 tradeoff) — never neither, never only one check attempted when it should
  have checked both (i.e. don't skip the content check just because it's convenient — only skip it when
  the filename already matched, per the agreed short-circuit).
- One unreadable/erroring file or directory must not abort the search of the rest of the tree; exit
  with a non-zero status if any error occurred, after completing the rest of the walk.
- Symlinks are never followed.

WHY NOW
Objective 0001 (design) was reviewed met; this is the next step in the design → implement rhythm.

WHAT "GOOD" AIMS AT
`references/design-principles.md` in the balash-guide skill this project follows — the target, not a
checklist. For an *implementation* objective, the review lens is correctness and conformance to the
agreed design (see `references/objective-selection.md` and `references/review.md`), not fresh design
judgment. Track fidelity explicitly: maintain your own TODO with one item per binding design decision
from `DESIGN.md` (the short-circuit location, the `FileMatcher` interface being consumer-defined in
`walk`, symlink handling, error tolerance, the `Result` struct shape) and one item per required
test/evidence item below, and check each off before returning — a single quietly-dropped decision is
exactly how an implementation drifts from a sound design.

RELEVANT CONTEXT / PRESERVE / NON-GOALS
- Read `.balash/knowledge.md` and `DESIGN.md` (both in this example's directory) before writing code.
- The design's package layout, type names, and function signatures in `DESIGN.md` are binding — this
  is an implementation objective, not a design one. Fill gaps the design didn't specify (arg parsing,
  `go.mod` module name, test file layout, a short usage README) using ordinary Go conventions.
- No new CLI flags, no config file, no performance tuning, no packaging — see Do-not-optimize-for above.

RETURN TO GUIDE
- Confirmation that `go build ./...` and `go test ./...` both succeed, with the exact commands you ran.
- A short account of any point where the design under-specified something you had to decide (e.g. exact
  flag parsing, error message wording) and what you chose.
- Result: met | partially_met | invalidated | blocked, against the exit criteria above.
- Any new facts or risks discovered.
Do not paste full source files into your final message — the Guide will read them from disk.

## Result

Delivered: `go.mod` (module `regex-file-search`), `internal/match/{match.go,match_test.go}`,
`internal/walk/{walk.go,walk_test.go}`, `main.go`, `README.md`. Package boundary matches `DESIGN.md`
exactly (confirmed independently below, not taken on report) — `walk_test.go` explicitly documents
that it does not import `match`. Underspecified points filled per ordinary Go convention: `parseArgs`
takes 1–2 positional args (pattern, optional root defaulting to `.`), no flag parsing library needed;
invalid regex or wrong arg count exits 2 with a usage/error message on stderr; any per-file error
during the walk still lets the walk finish, then the process exits 1.

## Review

**Reproduced directly, not taken on report** — the Guide built and ran the delivered code itself
before reading the Worker's own completion account:

- `cd examples/regex-file-search && go build ./...` — succeeds, no changes needed.
- `go vet ./...` — clean.
- `go test ./... -v` — all 7 tests pass: `TestMatch_FilenameShortCircuit`,
  `TestMatch_ContentMatch`, `TestMatch_BinaryExcluded`, `TestMatch_NoMatch`,
  `TestWalk_SymlinksNeverFollowedOrPassedToMatcher`,
  `TestWalk_OneErroringEntryDoesNotAbortTraversal`,
  `TestWalk_MatcherCalledExactlyOnceOnPerRegularFile`.
- Compiled the binary (`go build -o rfs .`) and ran it against a fresh fixture directory containing a
  content-only match, a binary file with the same needle in its content, a filename-only match, and a
  symlink to the filename-match target:
  - `rfs needle <fixture>` → reported only the real content match; the binary file (NUL-prefixed,
    containing the literal needle) was correctly excluded.
  - `rfs hello <fixture>` → reported only the real file; the symlink pointing at it was **not**
    reported — proves symlinks are skipped in the shipped binary, not just in the design.
  - `rfs plain <fixture>` → filename match reported correctly.
  - `rfs '[' <fixture>` → invalid regex handled cleanly: `invalid pattern: error parsing regexp:
    missing closing ]: `[`` on stderr, exit code 2, no panic.
- Read `main.go`, `internal/walk/walk.go`, `internal/walk/walk_test.go` directly: `main` imports only
  `match`, `walk`, and stdlib (`bufio`, `errors`, `fmt`, `os`) — no `regexp`, no direct file I/O:
  boundary held. `walk_test.go` carries an explicit comment that it deliberately does not import
  `match`, and its own test double satisfies `walk.FileMatcher` — confirms the interface is actually
  exercised as a real seam, not merely declared.

**Exit criteria — measured:**
- [x] `go build ./...` succeeds — reproduced.
- [x] `match` unit tests (short-circuit, content match, binary exclusion, no-match) — reproduced, all
      pass.
- [x] `walk` unit tests (symlink skip, error tolerance, exactly-once matcher call) via a `match`-free
      test double — reproduced, all pass, import confirmed absent.
- [x] Package boundaries preserved exactly — reproduced via import inspection and the symlink/binary
      probes above (behavior, not just structure).
- [x] Real directory-tree run reports exactly the right files — reproduced against a fresh fixture,
      four scenarios, all correct including the invalid-regex edge case (not required by the exit
      criterion but a good sign of care).

**Reading: met.** All five exit criteria hold under direct reproduction. Objective 0002 — and with it,
the regex-file-search example — is complete: a real, working, compiled Go CLI whose design and
implementation both went through the Balash loop with independently reproduced (not self-reported)
review evidence at each step.