package walk

// Deliberately does NOT import "regex-file-search/internal/match" — walk's
// traversal policy (symlink skip, per-entry error tolerance, calling the
// matcher exactly once per regular file) must be testable purely against
// the walk-defined FileMatcher interface, with no dependency on the real
// matching rule or regex compilation. This is exactly what the interface
// is for (see DESIGN.md §1.2).

import (
	"errors"
	"os"
	"path/filepath"
	"sync"
	"testing"
)

// recordingMatcher is a test-double FileMatcher. It records every path it
// is called with (so tests can assert what walk did and did not pass to
// it) and lets a test configure a per-path error/result.
type recordingMatcher struct {
	mu       sync.Mutex
	calls    []string
	errFor   map[string]error
	matchFor map[string]bool
}

func newRecordingMatcher() *recordingMatcher {
	return &recordingMatcher{
		errFor:   map[string]error{},
		matchFor: map[string]bool{},
	}
}

func (m *recordingMatcher) Match(path string) (bool, error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.calls = append(m.calls, path)
	if err, ok := m.errFor[path]; ok {
		return false, err
	}
	return m.matchFor[path], nil
}

func (m *recordingMatcher) callCount(path string) int {
	m.mu.Lock()
	defer m.mu.Unlock()
	n := 0
	for _, c := range m.calls {
		if c == path {
			n++
		}
	}
	return n
}

func (m *recordingMatcher) wasCalledWith(path string) bool {
	return m.callCount(path) > 0
}

// TestWalk_SymlinksNeverFollowedOrPassedToMatcher proves symlinks are
// never handed to the matcher — the sharpest possible check, since a
// symlink whose target would match is still never reported.
func TestWalk_SymlinksNeverFollowedOrPassedToMatcher(t *testing.T) {
	dir := t.TempDir()

	target := filepath.Join(dir, "real.txt")
	if err := os.WriteFile(target, []byte("hello"), 0o644); err != nil {
		t.Fatalf("WriteFile: %v", err)
	}

	link := filepath.Join(dir, "link.txt")
	if err := os.Symlink(target, link); err != nil {
		t.Fatalf("Symlink: %v", err)
	}

	// A symlink to a directory as well, to prove directory symlinks are
	// also never descended into.
	subdir := filepath.Join(dir, "sub")
	if err := os.Mkdir(subdir, 0o755); err != nil {
		t.Fatalf("Mkdir: %v", err)
	}
	dirLink := filepath.Join(dir, "sublink")
	if err := os.Symlink(subdir, dirLink); err != nil {
		t.Fatalf("Symlink (dir): %v", err)
	}

	fm := newRecordingMatcher()
	var results []Result
	err := Walk(dir, fm, func(r Result) {
		results = append(results, r)
	})
	if err != nil {
		t.Fatalf("Walk: %v", err)
	}

	if fm.wasCalledWith(link) {
		t.Errorf("matcher was called with symlink path %q; symlinks must never be passed to the matcher", link)
	}
	if fm.wasCalledWith(dirLink) {
		t.Errorf("matcher was called with symlink-to-directory path %q; must never be descended into", dirLink)
	}
	if !fm.wasCalledWith(target) {
		t.Errorf("matcher was never called with the real regular file %q", target)
	}

	for _, r := range results {
		if r.Path == link || r.Path == dirLink {
			t.Errorf("Result reported for symlink path %q; symlinks must produce no Result", r.Path)
		}
	}
}

// TestWalk_OneErroringEntryDoesNotAbortTraversal proves that when the
// matcher fails for one file (simulating an unreadable/erroring file —
// the same shape of failure a real permission error would produce
// through Matcher.Match), Walk still visits every other regular file in
// the tree instead of stopping early.
func TestWalk_OneErroringEntryDoesNotAbortTraversal(t *testing.T) {
	dir := t.TempDir()

	var paths []string
	for _, name := range []string{"a.txt", "b.txt", "c.txt", "d.txt"} {
		p := filepath.Join(dir, name)
		if err := os.WriteFile(p, []byte("x"), 0o644); err != nil {
			t.Fatalf("WriteFile: %v", err)
		}
		paths = append(paths, p)
	}

	fm := newRecordingMatcher()
	failingPath := paths[1] // b.txt
	fm.errFor[failingPath] = errors.New("simulated read failure")

	var results []Result
	err := Walk(dir, fm, func(r Result) {
		results = append(results, r)
	})
	if err != nil {
		t.Fatalf("Walk: %v", err)
	}

	if len(results) != len(paths) {
		t.Fatalf("got %d results, want %d — traversal must not stop after the erroring entry", len(results), len(paths))
	}

	seen := map[string]Result{}
	for _, r := range results {
		seen[r.Path] = r
	}
	for _, p := range paths {
		r, ok := seen[p]
		if !ok {
			t.Errorf("no Result reported for %q", p)
			continue
		}
		if p == failingPath {
			if r.Err == nil {
				t.Errorf("Result for erroring path %q has nil Err, want the simulated error", p)
			}
		} else if r.Err != nil {
			t.Errorf("Result for %q has unexpected Err: %v", p, r.Err)
		}
	}
}

// TestWalk_MatcherCalledExactlyOnceOnPerRegularFile proves the matcher is
// invoked exactly once for every regular file in the tree — no more (no
// duplicate work), no less (nothing silently skipped) — and never for
// the directories themselves.
func TestWalk_MatcherCalledExactlyOnceOnPerRegularFile(t *testing.T) {
	dir := t.TempDir()

	sub := filepath.Join(dir, "sub")
	if err := os.Mkdir(sub, 0o755); err != nil {
		t.Fatalf("Mkdir: %v", err)
	}

	files := []string{
		filepath.Join(dir, "top.txt"),
		filepath.Join(sub, "nested1.txt"),
		filepath.Join(sub, "nested2.txt"),
	}
	for _, p := range files {
		if err := os.WriteFile(p, []byte("content"), 0o644); err != nil {
			t.Fatalf("WriteFile: %v", err)
		}
	}

	fm := newRecordingMatcher()
	visitCount := 0
	err := Walk(dir, fm, func(r Result) {
		visitCount++
	})
	if err != nil {
		t.Fatalf("Walk: %v", err)
	}

	for _, p := range files {
		if got := fm.callCount(p); got != 1 {
			t.Errorf("matcher called %d times for %q, want exactly 1", got, p)
		}
	}
	if fm.wasCalledWith(dir) {
		t.Errorf("matcher was called with the root directory path itself")
	}
	if fm.wasCalledWith(sub) {
		t.Errorf("matcher was called with a subdirectory path itself")
	}
	if visitCount != len(files) {
		t.Errorf("visit called %d times, want exactly %d (once per regular file)", visitCount, len(files))
	}
}
