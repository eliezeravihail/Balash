// Package search implements the directory-walking / matching logic used by
// the regexfilesearch command-line tool: report every file under a root
// whose base filename matches a regular expression, or whose content
// matches the same expression.
package search

import (
	"bufio"
	"bytes"
	"fmt"
	"io"
	"io/fs"
	"os"
	"path/filepath"
	"regexp"
)

// sniffLen is how many leading bytes of a file we inspect to decide whether
// it looks like a binary file. 8000 mirrors the heuristic used by git and
// common grep implementations: "binary" == contains a NUL byte in the
// leading chunk.
const sniffLen = 8000

// Options configures a single Run.
type Options struct {
	// Root is the directory (or single file) to search. Defaults to "."
	// when empty.
	Root string
	// Pattern is the compiled regular expression matched against both
	// base filenames and file content.
	Pattern *regexp.Regexp
	// Stderr receives non-fatal warnings (unreadable files, broken
	// symlinks, directories we could not read, ...). Defaults to
	// os.Stderr when nil.
	Stderr io.Writer
}

// Run walks the directory tree rooted at opts.Root and invokes emit(path)
// once for every regular file whose base name or whose content matches
// opts.Pattern (a file only needs to satisfy one of the two — it's an OR).
//
// Problems with individual entries (a file that can't be opened, a symlink
// that can't be resolved, a subdirectory that can't be read, ...) are
// reported to opts.Stderr and otherwise skipped so the walk can continue.
// Run only returns a non-nil error when the root itself can't be walked at
// all (e.g. it doesn't exist).
//
// Symlinks are never followed for the purposes of descending into
// directories (this avoids symlink cycles). A symlink whose target is a
// regular file has its target's content read for content matching; a
// symlink that is broken, or that points at a directory, is still eligible
// for a filename match but is skipped for content matching.
func Run(opts Options, emit func(path string)) error {
	stderr := opts.Stderr
	if stderr == nil {
		stderr = os.Stderr
	}
	root := opts.Root
	if root == "" {
		root = "."
	}

	return filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			if path == root {
				// The root itself is unusable (doesn't exist, no
				// permission, ...); nothing sensible to search.
				return err
			}
			fmt.Fprintf(stderr, "warning: %s: %v\n", path, err)
			if d != nil && d.IsDir() {
				return filepath.SkipDir
			}
			return nil
		}

		if d.IsDir() {
			return nil
		}

		nameMatch := opts.Pattern.MatchString(d.Name())
		if nameMatch {
			emit(path)
			return nil
		}

		readable, reason := contentReadable(path, d)
		if !readable {
			if reason != "" {
				fmt.Fprintf(stderr, "warning: %s: %s\n", path, reason)
			}
			return nil
		}

		matched, err := contentMatches(path, opts.Pattern)
		if err != nil {
			fmt.Fprintf(stderr, "warning: %s: %v\n", path, err)
			return nil
		}
		if matched {
			emit(path)
		}
		return nil
	})
}

// contentReadable decides whether path's content should even be looked at:
// symlinks to directories (or broken symlinks) are skipped, along with any
// non-regular file (devices, sockets, pipes, ...). It follows symlinks (via
// os.Stat) purely to classify the target; Run never descends into
// symlinked directories.
func contentReadable(path string, d fs.DirEntry) (ok bool, reason string) {
	if d.Type()&fs.ModeSymlink != 0 {
		target, err := os.Stat(path)
		if err != nil {
			return false, "broken or inaccessible symlink, skipping content check: " + err.Error()
		}
		if target.IsDir() {
			return false, ""
		}
		if !target.Mode().IsRegular() {
			return false, ""
		}
		return true, ""
	}
	if !d.Type().IsRegular() {
		// devices, sockets, named pipes, etc. - not something we want
		// to try to "read" as text content.
		return false, ""
	}
	return true, ""
}

// contentMatches reports whether re matches somewhere in path's content.
// Files that look binary (a NUL byte in the first sniffLen bytes) are
// treated as non-matching on content, matching the common convention that
// tools like grep use to avoid dumping/scanning binary garbage; such files
// can still match by filename.
func contentMatches(path string, re *regexp.Regexp) (bool, error) {
	f, err := os.Open(path)
	if err != nil {
		return false, err
	}
	defer f.Close()

	r := bufio.NewReaderSize(f, sniffLen)
	sniff, _ := r.Peek(sniffLen) // short/EOF error ignored: sniff still holds what was read
	if bytes.IndexByte(sniff, 0) != -1 {
		return false, nil // looks binary; skip content matching
	}

	data, err := io.ReadAll(r)
	if err != nil {
		return false, err
	}
	return re.Match(data), nil
}
