package match

import (
	"os"
	"path/filepath"
	"testing"
)

// TestMatch_FilenameShortCircuit proves — observably, not just
// structurally — that a filename match never reads the file's content.
// It does this by pointing Match at a path that does not exist on disk
// at all: if Match ever tried to open it, matchContent would return an
// error (or Match would return that error), not a clean true/nil. Since
// the filename ("needle.txt") matches the pattern, Match must report a
// match without ever attempting os.Open.
func TestMatch_FilenameShortCircuit(t *testing.T) {
	m, err := New(`needle`)
	if err != nil {
		t.Fatalf("New: %v", err)
	}

	// Deliberately non-existent path/directory: any attempt to os.Open
	// this would fail, which would surface as a non-nil error (or a
	// false result) if the short-circuit were not really happening.
	nonExistentPath := filepath.Join(t.TempDir(), "this-dir-does-not-exist", "needle.txt")

	matched, err := m.Match(nonExistentPath)
	if err != nil {
		t.Fatalf("Match returned error %v; a filename match must short-circuit before any file I/O", err)
	}
	if !matched {
		t.Fatalf("Match() = false, want true (filename %q should match pattern)", filepath.Base(nonExistentPath))
	}
}

// TestMatch_ContentMatch verifies a file whose name does not match is
// still reported as a match when its content does.
func TestMatch_ContentMatch(t *testing.T) {
	m, err := New(`needle`)
	if err != nil {
		t.Fatalf("New: %v", err)
	}

	path := writeTempFile(t, "plain.txt", "hello\nthere is a needle in here\ngoodbye\n")

	matched, err := m.Match(path)
	if err != nil {
		t.Fatalf("Match: %v", err)
	}
	if !matched {
		t.Fatalf("Match() = false, want true (content contains %q)", "needle")
	}
}

// TestMatch_BinaryExcluded verifies a file that looks binary (a NUL byte
// in its first chunk) is never content-matched, even though its bytes
// contain the pattern — but is still eligible for a filename match, per
// the design's stated contract for a correct Matcher implementation.
func TestMatch_BinaryExcluded(t *testing.T) {
	m, err := New(`needle`)
	if err != nil {
		t.Fatalf("New: %v", err)
	}

	// Content contains the literal pattern, but the leading NUL byte
	// marks it as binary — content matching must be skipped.
	content := "\x00binary data containing needle in it"
	path := writeTempFile(t, "blob.dat", content)

	matched, err := m.Match(path)
	if err != nil {
		t.Fatalf("Match: %v", err)
	}
	if matched {
		t.Fatalf("Match() = true, want false: binary file content must not be matched")
	}
}

// TestMatch_NoMatch verifies a file matches neither by filename nor by
// content reports false, with no error.
func TestMatch_NoMatch(t *testing.T) {
	m, err := New(`needle`)
	if err != nil {
		t.Fatalf("New: %v", err)
	}

	path := writeTempFile(t, "plain.txt", "hello\ngoodbye\n")

	matched, err := m.Match(path)
	if err != nil {
		t.Fatalf("Match: %v", err)
	}
	if matched {
		t.Fatalf("Match() = true, want false: neither filename nor content contains the pattern")
	}
}

func writeTempFile(t *testing.T, name, content string) string {
	t.Helper()
	dir := t.TempDir()
	path := filepath.Join(dir, name)
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		t.Fatalf("WriteFile: %v", err)
	}
	return path
}
