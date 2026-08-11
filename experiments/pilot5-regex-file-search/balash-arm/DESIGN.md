# Design — regex-file-search (objective 0001: match-ownership-boundary)

Status: design only. No implementation is committed by this document (that is objective 0002's
job); signatures below are the shape the implementation must fill in.

## 1. The design

Three packages, one responsibility each, wired together only by `main`:

```
main (CLI/output)
  ├── imports match   (owns: does one file match?)
  └── imports walk    (owns: which files exist, tolerating bad entries?)

match  — does NOT import walk
walk   — does NOT import match (depends on a narrow interface it defines itself)
```

### 1.1 `match` — owns the match decision

```go
package match

import (
    "bufio"
    "io"
    "os"
    "path/filepath"
    "regexp"
)

// Matcher decides whether a single file matches a compiled search
// pattern, by filename or by content. It is the only place the
// filename-OR-content rule is evaluated. Content is read only when the
// filename check did not already satisfy the match.
type Matcher struct {
    pattern *regexp.Regexp
}

// New compiles pattern (RE2 syntax, per Go's regexp package) into a
// reusable, concurrency-safe Matcher. Returns an error for an invalid
// pattern — the same error regexp.Compile would give, so the CLI layer
// can surface it as-is.
func New(pattern string) (*Matcher, error) {
    re, err := regexp.Compile(pattern)
    if err != nil {
        return nil, err
    }
    return &Matcher{pattern: re}, nil
}

// Match reports whether the regular file at path matches: filename match
// short-circuits before any content is read. Callers (the walker) are
// responsible for only calling Match on regular files — Match does not
// re-check that path names a directory/symlink/etc.
func (m *Matcher) Match(path string) (bool, error) {
    if m.pattern.MatchString(filepath.Base(path)) {
        return true, nil // short-circuit: never opens the file
    }
    return m.matchContent(path)
}

func (m *Matcher) matchContent(path string) (bool, error) {
    f, err := os.Open(path)
    if err != nil {
        return false, err
    }
    defer f.Close()

    binary, err := looksBinary(f)
    if err != nil {
        return false, err
    }
    if binary {
        return false, nil // binary files are never content-matched
    }

    sc := bufio.NewScanner(f)
    sc.Buffer(make([]byte, 0, 64*1024), maxLineBytes)
    for sc.Scan() {
        if m.pattern.Match(sc.Bytes()) {
            return true, nil
        }
    }
    return false, sc.Err()
}

const (
    sniffLen     = 8000    // bytes inspected for the binary heuristic (git/file(1)-sized)
    maxLineBytes = 1 << 20 // per-line cap so one huge line can't grow memory unboundedly
)

// looksBinary applies the standard "NUL byte in the first chunk" binary
// heuristic and rewinds f to the start on success so the caller can then
// read the file from byte 0.
func looksBinary(f *os.File) (bool, error) {
    buf := make([]byte, sniffLen)
    n, err := f.Read(buf)
    if err != nil && err != io.EOF {
        return false, err
    }
    for _, b := range buf[:n] {
        if b == 0 {
            return true, nil
        }
    }
    _, err = f.Seek(0, io.SeekStart)
    return false, err
}
```

`Matcher` is a **concrete type, not an interface**. Nothing in this design anticipates a second
matching strategy (that's exactly the non-goal list: no plugin matcher system, no multi-regex).
An `IMatcher` wrapping the one concrete `Matcher` would be the "`ICat`" trap the design-principles
doc warns about — decorative, not a real abstraction.

### 1.2 `walk` — owns traversal

```go
package walk

import (
    "io/fs"
    "path/filepath"
)

// FileMatcher decides whether the file at path matches. Walk depends on
// this narrow, single-method interface — defined here, by the consumer —
// not on any concrete matcher type, so traversal is testable and
// compiles without ever importing regexp or touching file content.
type FileMatcher interface {
    Match(path string) (bool, error)
}

// Result is the outcome of attempting to check one file. When Err is
// non-nil the file could not be checked (permission error, read error,
// mid-walk I/O failure, etc.) and Matched is meaningless; Walk continues
// regardless of Err on any single entry.
type Result struct {
    Path    string
    Matched bool
    Err     error
}

// Walk walks the tree rooted at root and calls visit once for every
// regular file it attempts to check. It never follows symlinks (so it
// cannot loop on a link cycle) and never lets one unreadable file or
// directory stop the walk — such entries are reported through
// Result.Err instead of aborting. Walk owns exactly this traversal
// policy (which entries are candidates, how failures are tolerated); it
// never itself decides whether a file "matches" beyond delegating to
// matcher.
func Walk(root string, matcher FileMatcher, visit func(Result)) error {
    return filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
        if err != nil {
            visit(Result{Path: path, Err: err})
            return nil // one bad entry must not abort the rest of the tree
        }
        if d.Type()&fs.ModeSymlink != 0 {
            return nil // never follow symlinks; never pass one to matcher
        }
        if d.IsDir() {
            return nil // descend; nothing to report for the directory itself
        }
        if !d.Type().IsRegular() {
            return nil // skip devices, sockets, named pipes, etc.
        }
        matched, mErr := matcher.Match(path)
        visit(Result{Path: path, Matched: matched, Err: mErr})
        return nil
    })
}
```

### 1.3 `main` — owns CLI/output only

```go
package main

import (
    "bufio"
    "fmt"
    "os"

    "regex-file-search/internal/match"
    "regex-file-search/internal/walk"
)

func main() {
    pattern, root, err := parseArgs(os.Args[1:]) // positional: <pattern> [root=.]
    if err != nil {
        fmt.Fprintln(os.Stderr, "usage: regex-file-search <pattern> [root]")
        os.Exit(2)
    }

    matcher, err := match.New(pattern)
    if err != nil {
        fmt.Fprintln(os.Stderr, "invalid pattern:", err)
        os.Exit(2)
    }

    out := bufio.NewWriter(os.Stdout)
    exitCode := 0

    err = walk.Walk(root, matcher, func(r walk.Result) {
        switch {
        case r.Err != nil:
            fmt.Fprintf(os.Stderr, "%s: %v\n", r.Path, r.Err)
            exitCode = 1
        case r.Matched:
            fmt.Fprintln(out, r.Path)
        }
    })
    out.Flush()
    if err != nil {
        fmt.Fprintln(os.Stderr, "search failed:", err)
        exitCode = 1
    }
    os.Exit(exitCode)
}
```

`main` calls exactly two entry points — `match.New` and `walk.Walk` — plus the `walk.Result`
struct's fields. It never imports `regexp`, never calls `os.Open`/`os.ReadDir` itself, and never
re-derives "does this match" from pieces. That is the whole boundary contract.

## 2. Reasoning

**Why this three-way split.** Each package has exactly one reason to change (Single
Responsibility, principle 8): `match` changes if the matching *rule* changes (case sensitivity,
binary heuristic, what counts as a short-circuit); `walk` changes if traversal *policy* changes
(how errors are surfaced, whether hidden files are skipped, whether symlinks are ever followed);
`main` changes if CLI *surface* changes (flags, output format, exit codes). A naive single-file
version tangles these — e.g. the walker deciding to skip content-reading because it peeked the
filename itself, duplicating the OR check outside `match`. Keeping them separate is what makes
0002 "fill in the shape" instead of "figure out the shape while also writing it."

**Why the short-circuit lives inside `Matcher.Match`, not in `walk`.** This is the load-bearing
decision. The alternative — `walk` opens the file (or stats it) and hands a reader to the matcher,
which only evaluates — looks tidier but is wrong: it would force `walk` to ask "does the filename
already match?" *before* deciding whether to open the file, which means half of the match rule
(the short-circuit condition) now lives in the walker. That is precisely the drift the objective
warns against ("no other layer can silently reimplement or diverge from the matching rule"). By
giving `Matcher.Match` the *path* (not a pre-opened reader) and letting it decide internally
whether to call `os.Open` at all, the short-circuit policy and the I/O it controls stay in the
same place, and `walk` never needs to know the short-circuit exists.

**Why the short-circuit is safe.** Regex matching is a pure predicate over bytes — evaluating it
has no side effect. `nameMatches OR contentMatches` is a boolean OR whose left operand is already
known before the right operand's *only* purpose (an I/O side effect: reading the file) is invoked.
Short-circuiting an OR on a true left operand never changes the OR's truth value, and it happens
to also skip the one operation with a real cost (and a real failure mode — permission errors,
binary content) that wasn't needed to know the answer. There is no way for this short-circuit to
produce a different verdict than always evaluating both sides, because both sides use the exact
same compiled `*regexp.Regexp` — one object, two call sites (`MatchString` on the base name,
`Match` on each line) — so there is structurally no way for the "name rule" and "content rule" to
drift apart into two different patterns.

**What a second correct `Matcher` implementation must preserve.** Anyone reimplementing this
matcher (different binary-detection heuristic, different content-scanning strategy, whatever) must
keep: (a) the `Match(path string) (bool, error)` contract — one path in, one match verdict + error
out; (b) the OR semantics — report a match if *either* check succeeds, using the *same* pattern for
both; (c) the short-circuit — must not perform file I/O when the filename alone already matches,
since that I/O is externally observable (permission errors on files that would otherwise never be
opened, e.g. a matching filename inside a directory the user can list but not read); (d) treating a
binary file as "no content match, but still eligible for a filename match" rather than an error or
a crash; (e) surfacing I/O failures as a returned `error`, never a panic, so `walk`'s per-file
error tolerance keeps working unmodified.

**Why `walk.FileMatcher` is an interface but `match.Matcher` is not.** This is not a contradiction;
it's the Go idiom of interfaces belonging to the consumer, not the producer. The interface is
*narrow* (one method) and *consumer-defined* (declared in `walk`, not `match`), which is exactly
what makes it non-decorative under principle 2's test: "what would a second, legitimately different
implementation look like?" Here the answer is concrete and present, not speculative — a test double
used today to unit-test `walk`'s traversal policy (symlink skip, error tolerance, "call the matcher
exactly once per regular file") without needing real regex compilation or real file content, and
without `walk_test.go` importing `match` at all. Subtractive check: delete `FileMatcher` and take a
concrete `*match.Matcher` parameter instead — `walk` would compile and run identically, but `walk`
would now import `match`, and testing `walk`'s traversal policy would require constructing real
`*match.Matcher` values and real files on disk for every traversal-policy test case, coupling
traversal tests to matching behavior they don't care about. The interface's job is exactly to
prevent that coupling — it is the concrete expression of "kept independent of directory traversal"
from the objective, at the level of what packages import what.

**Subtractive check on `walk.Result`.** Delete it and have `visit` take `(path string, matched
bool, err error)` as three parameters instead of one struct — functionally equivalent, but the
call site loses the ability to name and pass around "one file's outcome" as a value (e.g. collect
results, or extend later without changing the callback signature). It's a small domain type
(principle 4, avoiding primitive obsession for what is actually one cohesive piece of data), kept
deliberately flat — three fields, no methods — because it carries data across the walk→CLI boundary
and has no behavior of its own to enforce; that's a legitimate "just data" boundary type, not the
anemic-model smell (principle 5 concerns a *domain* type that should have behavior; a package- boundary
transfer record is a different thing).

**Subtractive check on `match.New` returning `*Matcher` (not exposing `*regexp.Regexp`
directly).** If `match` just exported the compiled `*regexp.Regexp` and let `walk`/`main` call
`MatchString`/read files themselves, the short-circuit and binary-skip logic would have nowhere to
live except duplicated at each call site — which is exactly the "no single owner" failure mode the
objective is designed against. `Matcher` earns its existence by being the one place that logic runs.

**Design-principles pass, briefly, on what does/doesn't apply at this scale:**
- *Tell, Don't Ask* (1): `walk` tells the matcher "does this path match" and gets a verdict; it
  never asks for regex internals or file bytes to decide itself. Satisfied by construction.
- *Interface segregation* (3): `FileMatcher` has exactly the one method `walk` calls — nothing to
  segregate further.
- *Primitive obsession* (4): the regex pattern itself is deliberately left a `string` at the CLI
  boundary (`match.New(pattern string)`) rather than given its own type — a compiled pattern has no
  extra rules beyond "is it valid RE2," which `regexp.Compile`'s own error already enforces; a
  wrapper type here would carry no behavior beyond what `*regexp.Regexp` already is. This is a case
  where the principle doesn't force a new type, and I can say why: there's no validation rule
  *beyond* compilation, and only one thing in the system ever produces or consumes it.
- *Leaky abstractions / boundary vocabulary* (7): the only types crossing the `match`⇄`walk`⇄`main`
  seams are stdlib primitives (`string`, `bool`, `error`) and one small domain type (`Result`) —
  never a `*regexp.Regexp`, `*os.File`, or `fs.DirEntry` escapes its owning package.
- *God object* (8) / *feature envy* (6): each package's exported surface is one to two functions;
  none reaches into another's internals to do its own job.
- Explicitly **not forced**: no interface for `Matcher` itself (no second implementation is real or
  anticipated — see 1.1); no generic "output sink" interface for `main` (there is exactly one output
  mode — stdout/stderr — and no requirement to swap it); no config/strategy object for the binary
  heuristic or line-length cap (single hardcoded constants with a stated reason, revisit only if a
  real second need shows up).

## 3. New facts and risks discovered

- **`filepath.WalkDir` requires `io/fs`**, not just the five packages the objective names
  (`regexp`, `path/filepath`, `os`, `bufio`, `io`) — its callback signature is
  `func(path string, d fs.DirEntry, err error) error` and `fs.SkipDir`/`fs.ModeSymlink` live in
  `io/fs`. This is still standard library, so it doesn't violate "stdlib only," but 0002 should
  expect an `io/fs` import (plus `fmt`/`os.Args`/similar for the CLI layer) alongside the five named
  packages — the objective's list was clearly illustrative of the matching+traversal core, not an
  exhaustive import whitelist.
- **`regexp.Regexp.MatchReader` is a UTF-8-rune-based API, not byte-based** — it takes an
  `io.RuneReader`, and Go's docs note malformed UTF-8 is decoded as a run of `utf8.RuneError`
  replacement runes rather than matched byte-for-byte. I initially considered `MatchReader` over a
  `bufio.Reader` to match patterns across the whole file in one streaming pass (no line-splitting,
  no multi-line-pattern limitation) but rejected it once this surfaced: a non-UTF-8 text file (e.g.
  Latin-1) could silently fail to content-match literal byte patterns, or match unpredictably. The
  design instead uses `bufio.Scanner` + `regexp.Match` on `[]byte` per line, which is byte-exact
  regardless of encoding. **Known, accepted limitation from this choice:** a pattern intended to
  match across a line break (e.g. `(?s)foo.*bar` spanning two lines) will not match via the content
  check, matching common line-oriented tools (grep without `-P`/multiline mode) rather than
  whole-file semantics. This is worth a one-line callout in 0002 or user-facing docs but is not a
  blocker — it wasn't a requirement, and the alternative (`io.ReadAll` the whole file into memory)
  trades this away for unbounded per-file memory, which is worse for the stated non-goals.
- **`bufio.Scanner`'s default token size is 64KiB per line** — a file with one very long line (e.g.
  minified JS, a single-line log) would otherwise fail with `bufio.ErrTooLong` on the *first*
  matching attempt. The design raises this via `sc.Buffer(..., maxLineBytes)` with an explicit,
  named cap (1MiB) rather than leaving the stdlib default in place silently; a file with an even
  longer single line still fails cleanly (`sc.Err()` propagates as a per-file `error`, tolerated by
  `walk` like any other unreadable file) rather than hanging or panicking.
- **`filepath.WalkDir`'s error-argument contract**: when the callback receives `err != nil`, `d`
  may be nil/unpopulated for that entry — the callback must handle the error *before* touching `d`,
  and returning `nil` (as opposed to `fs.SkipDir` or the error itself) is what lets traversal
  continue with the rest of the tree. This is exactly the "one bad file/directory must not abort
  the rest" requirement, and it's satisfied for free by `filepath.WalkDir`'s existing semantics
  rather than needing custom recovery logic in `walk`.
- **Symlinks are identified without extra stat calls**: `fs.DirEntry.Type()` inside `WalkDir`'s
  callback is derived from the directory read itself (`Lstat`-equivalent, not following the link),
  so checking `d.Type()&fs.ModeSymlink != 0` reliably detects a symlink — including a symlink to a
  directory — without an extra syscall and without ever resolving/following it. No cycle risk is
  introduced.
- **The binary-sniff re-reads the file's first bytes twice** (once raw into the sniff buffer, then
  again from offset 0 once `bufio.Scanner` starts) — a small, deliberate simplification; avoided
  because it needed either the sniff buffer to be re-fed into the scanner (extra plumbing) or a
  `bufio.Reader.Peek` + no-rewind approach that complicates the "return to matchable state"
  contract. Given the explicit non-goal of not tuning performance, this is an acceptable, clearly
  bounded (≤8000 bytes) redundant read.
