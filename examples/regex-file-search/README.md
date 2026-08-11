# regex-file-search

A compiled command-line tool that searches a directory tree and reports every file whose **name**
or **content** matches a given regular expression.

## Build

```sh
go build -o regex-file-search .
```

Requires Go (stdlib only — no third-party dependencies) and produces a single static binary.

## Usage

```sh
./regex-file-search '<pattern>' [root]
```

- `<pattern>` — an RE2 regular expression (Go's `regexp` package syntax).
- `[root]` — optional directory to search; defaults to the current directory.

A file is printed (one path per line, to stdout) if either its filename matches `<pattern>` or its
content does (logical OR — either is enough). A file whose name already matches is never opened to
check its content.

```sh
./regex-file-search 'TODO' ./src
./regex-file-search '^config.*\.ya?ml$'
```

## Behavior notes

- Symlinks are never followed.
- Content matching is line-oriented (like `grep` without multiline mode): a pattern that spans a
  line break will not match via content, only via filename.
- Files that look binary (a NUL byte in the first bytes read) are skipped for content matching but
  are still eligible for a filename match.
- One unreadable file or directory does not stop the rest of the search; the tool exits non-zero if
  any error occurred, after finishing the walk, and prints the error to stderr.

## Package layout

- `internal/match` — owns the filename-or-content match decision (see `DESIGN.md`).
- `internal/walk` — owns directory traversal (symlink skip, per-entry error tolerance).
- `main.go` — CLI argument parsing and output only; depends on `match`/`walk` through their public
  boundary (`match.New`, `walk.Walk`, `walk.Result`).

See `DESIGN.md` for the full design and its reasoning.

## Tests

```sh
go test ./...
```
