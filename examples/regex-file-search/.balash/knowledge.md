# Balash Product Knowledge

Durable, cross-session product knowledge — the Guide's decision log. This file is append-first: when
a fact or decision is superseded, say so next to it rather than deleting it.

## Product purpose

A compiled command-line tool that searches files under a directory tree and reports every file whose
**name** matches a given regex **or** whose **content** matches that same regex (logical OR — a file
is reported if either side matches; the two are not required to match together).

## Core scenarios

- A user runs the tool with a regex and a root path (or the current directory by default). The tool
  walks the tree and prints, one per line, the path of every file where the filename matches the regex
  or the file's content contains a match for the regex. — source: user request.

## Product knowledge

### Grounded product facts

- The output artifact must be a compiled program, not an interpreted script. — source: user request
  ("תוכנה מתקמפלת").
- A file counts as a match if its **filename** matches the regex **or** its **content** matches the
  regex — an inclusive OR over two independent checks, not a combined/AND condition. — source: user
  request ("בשם הקובץ או תכולתו (זה או זה)").
- This is a filesystem search tool over "the computer" (a directory tree), not a single-file utility.
  — source: user request.

### Open product decisions

None — this is a demo/example run authorized to proceed on Guide-made defaults for anything not
stated by the user (see "Technical freedoms" and "Explicit non-goals" below) rather than pausing for
clarification.

### Technical freedoms

- Implementation language: Go (stdlib `regexp`/RE2, `path/filepath`, `os`, `bufio` cover the whole
  problem; compiles to a single static binary; easy for a Worker to write correctly and test).
- Regex flavor: whatever the chosen language's standard regex engine supports (RE2 syntax under Go) —
  not guaranteed PCRE-compatible.
- Case sensitivity, output format (one path per line to stdout), and CLI flag naming.
- Whether unreadable files/directories are skipped silently or reported to stderr — either is fine as
  long as one bad file doesn't abort the whole search.

## Product forces

### Likely change axes

- None identified for this v1 scope — this is a small, single-purpose demo tool, not a product
  expected to grow flags/features across many future changes. Do not build speculative extension
  points (e.g. a plugin matcher system, a config file format) for this.

### Invariants

- A file is reported **iff** its filename matches the regex or its content matches the regex — never
  neither, never only "close enough."
- One unreadable, binary, or otherwise problematic file must not abort the search of the rest of the
  tree.

### Constraints

- Must run as a single compiled binary with no required runtime installation beyond the OS (rules out
  needing a JVM/Python/Node runtime present on the target machine).

### Foundational dependencies (day-zero)

- Go's standard library only (`regexp`, `path/filepath`, `os`, `bufio`, `io`) — the whole problem
  (regex matching + tree traversal + file reading) is covered by stdlib. No third-party dependency is
  pervasive enough to qualify as foundational, so none is adopted. Decided by the Guide (does not
  materially change product-visible behavior).

### Explicit non-goals (v1, Guide-decided defaults for this demo)

- Does not default to scanning the entire filesystem from `/` — takes a root path argument, defaulting
  to the current working directory. Scanning arbitrary system-wide roots is the caller's choice via the
  argument, not the tool's default behavior.
- Does not attempt content-matching inside binary files — a file that looks binary (a NUL byte in the
  first chunk read, the common heuristic) is skipped for the content check but still checked by
  filename. Avoids nonsense matches and pathological slow reads on large binaries.
- Does not follow symlinks during traversal (avoids link cycles).
- No multi-regex, filename-only/content-only flags, parallelism/performance tuning, or config file —
  none of these were asked for; adding them would be speculative for this demo.

## Durable decisions

- Language/runtime: Go, stdlib only. — reason: compiled-binary requirement + no external dependency
  needed for this problem. — objective: (day-zero, before 0001).
- Root path defaults to cwd; symlinks not followed; binary files skipped for content matching. — reason:
  safe, unsurprising defaults for a demo tool the user did not further specify. — objective: (day-zero,
  before 0001).

## Open Guide TODO

- [ ]
