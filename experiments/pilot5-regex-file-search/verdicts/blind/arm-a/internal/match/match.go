// Package match owns the single decision "does this file match a compiled
// search pattern" — by filename or by content, with filename checked first
// so content is only read when the filename check did not already satisfy
// the match. No other package re-implements this OR check.
package match

import (
	"bufio"
	"io"
	"os"
	"path/filepath"
	"regexp"
)

const (
	sniffLen     = 8000    // bytes inspected for the binary heuristic (git/file(1)-sized)
	maxLineBytes = 1 << 20 // per-line cap so one huge line can't grow memory unboundedly
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
