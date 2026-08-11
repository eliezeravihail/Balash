// Package walk owns directory traversal: which files are candidates for
// matching, and how bad entries (permission errors, symlinks) are
// tolerated. It never decides whether a file "matches" beyond delegating
// to a FileMatcher — the matching rule itself lives in package match, not
// here.
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
