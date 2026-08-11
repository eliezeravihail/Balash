package search

import (
	"bytes"
	"os"
	"path/filepath"
	"regexp"
	"runtime"
	"sort"
	"testing"
)

// runSearch is a small test helper: compiles pattern, runs Run over root
// and returns the sorted list of matched paths plus whatever was written to
// the warnings stream.
func runSearch(t *testing.T, pattern, root string) (matches []string, warnings string) {
	t.Helper()
	re, err := regexp.Compile(pattern)
	if err != nil {
		t.Fatalf("regexp.Compile(%q): %v", pattern, err)
	}
	var stderr bytes.Buffer
	var got []string
	err = Run(Options{Root: root, Pattern: re, Stderr: &stderr}, func(path string) {
		got = append(got, path)
	})
	if err != nil {
		t.Fatalf("Run: unexpected error: %v", err)
	}
	sort.Strings(got)
	return got, stderr.String()
}

func writeFile(t *testing.T, path string, content []byte) {
	t.Helper()
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, content, 0o644); err != nil {
		t.Fatal(err)
	}
}

func TestFilenameMatch(t *testing.T) {
	dir := t.TempDir()
	writeFile(t, filepath.Join(dir, "report.txt"), []byte("nothing interesting here"))
	writeFile(t, filepath.Join(dir, "notes.md"), []byte("nothing interesting here either"))

	matches, _ := runSearch(t, `report`, dir)
	want := []string{filepath.Join(dir, "report.txt")}
	if !equal(matches, want) {
		t.Errorf("matches = %v, want %v", matches, want)
	}
}

func TestContentMatch(t *testing.T) {
	dir := t.TempDir()
	writeFile(t, filepath.Join(dir, "a.txt"), []byte("the quick brown fox"))
	writeFile(t, filepath.Join(dir, "b.txt"), []byte("nothing to see"))

	matches, _ := runSearch(t, `quick`, dir)
	want := []string{filepath.Join(dir, "a.txt")}
	if !equal(matches, want) {
		t.Errorf("matches = %v, want %v", matches, want)
	}
}

func TestOrSemanticsNoDuplicate(t *testing.T) {
	dir := t.TempDir()
	// filename AND content both match "needle" - must appear exactly once.
	writeFile(t, filepath.Join(dir, "needle.txt"), []byte("contains needle too"))
	// only content matches
	writeFile(t, filepath.Join(dir, "other.txt"), []byte("has a needle inside"))
	// only filename matches
	writeFile(t, filepath.Join(dir, "needle.log"), []byte("no match here"))
	// neither matches
	writeFile(t, filepath.Join(dir, "plain.txt"), []byte("boring"))

	matches, _ := runSearch(t, `needle`, dir)
	want := []string{
		filepath.Join(dir, "needle.log"),
		filepath.Join(dir, "needle.txt"),
		filepath.Join(dir, "other.txt"),
	}
	if !equal(matches, want) {
		t.Errorf("matches = %v, want %v", matches, want)
	}
	// sanity: no duplicates
	seen := map[string]bool{}
	for _, m := range matches {
		if seen[m] {
			t.Errorf("duplicate match for %s", m)
		}
		seen[m] = true
	}
}

func TestBinaryFileSkippedForContentButNotFilename(t *testing.T) {
	dir := t.TempDir()
	binContent := append([]byte("headerneedle\x00"), []byte{1, 2, 3, 0, 4, 5}...)
	writeFile(t, filepath.Join(dir, "data.bin"), binContent)

	// content contains "needle" but file is binary -> must NOT match on content.
	matches, _ := runSearch(t, `needle`, dir)
	if len(matches) != 0 {
		t.Errorf("expected binary file content not to match, got %v", matches)
	}

	// filename matching must still work for the same binary file.
	matches, _ = runSearch(t, `data\.bin`, dir)
	want := []string{filepath.Join(dir, "data.bin")}
	if !equal(matches, want) {
		t.Errorf("matches = %v, want %v", matches, want)
	}
}

func TestSubdirectoriesWalked(t *testing.T) {
	dir := t.TempDir()
	writeFile(t, filepath.Join(dir, "sub", "deep", "target.txt"), []byte("x"))

	matches, _ := runSearch(t, `target`, dir)
	want := []string{filepath.Join(dir, "sub", "deep", "target.txt")}
	if !equal(matches, want) {
		t.Errorf("matches = %v, want %v", matches, want)
	}
}

func TestSymlinkToFileFollowedForContent(t *testing.T) {
	if runtime.GOOS == "windows" {
		t.Skip("symlinks require elevated privileges on windows")
	}
	dir := t.TempDir()
	target := filepath.Join(dir, "real.txt")
	writeFile(t, target, []byte("special-content-marker"))
	link := filepath.Join(dir, "link.txt")
	if err := os.Symlink(target, link); err != nil {
		t.Fatal(err)
	}

	matches, _ := runSearch(t, `special-content-marker`, dir)
	want := []string{link, target}
	if !equal(matches, want) {
		t.Errorf("matches = %v, want %v", matches, want)
	}
}

func TestSymlinkToDirectoryNotWalked(t *testing.T) {
	if runtime.GOOS == "windows" {
		t.Skip("symlinks require elevated privileges on windows")
	}
	dir := t.TempDir()
	realDir := filepath.Join(dir, "realdir")
	if err := os.MkdirAll(realDir, 0o755); err != nil {
		t.Fatal(err)
	}
	writeFile(t, filepath.Join(realDir, "inside.txt"), []byte("hello"))
	linkDir := filepath.Join(dir, "linkdir")
	if err := os.Symlink(realDir, linkDir); err != nil {
		t.Fatal(err)
	}

	// Pattern that would match the file inside realDir by content; it
	// should be found once via the real path but the symlinked directory
	// must not be descended into (no duplicate, no infinite loop).
	matches, _ := runSearch(t, `hello`, dir)
	want := []string{filepath.Join(realDir, "inside.txt")}
	if !equal(matches, want) {
		t.Errorf("matches = %v, want %v", matches, want)
	}
}

func TestBrokenSymlinkWarnsAndContinues(t *testing.T) {
	if runtime.GOOS == "windows" {
		t.Skip("symlinks require elevated privileges on windows")
	}
	dir := t.TempDir()
	link := filepath.Join(dir, "dangling")
	if err := os.Symlink(filepath.Join(dir, "does-not-exist"), link); err != nil {
		t.Fatal(err)
	}
	writeFile(t, filepath.Join(dir, "ok.txt"), []byte("fine"))

	matches, warnings := runSearch(t, `fine`, dir)
	want := []string{filepath.Join(dir, "ok.txt")}
	if !equal(matches, want) {
		t.Errorf("matches = %v, want %v", matches, want)
	}
	if warnings == "" {
		t.Errorf("expected a warning about the broken symlink, got none")
	}
}

func TestSymlinkNameCanStillMatchByFilename(t *testing.T) {
	if runtime.GOOS == "windows" {
		t.Skip("symlinks require elevated privileges on windows")
	}
	dir := t.TempDir()
	link := filepath.Join(dir, "findme-broken")
	if err := os.Symlink(filepath.Join(dir, "nope"), link); err != nil {
		t.Fatal(err)
	}

	matches, _ := runSearch(t, `findme`, dir)
	want := []string{link}
	if !equal(matches, want) {
		t.Errorf("matches = %v, want %v", matches, want)
	}
}

func TestUnreadableFileWarnsAndContinues(t *testing.T) {
	if runtime.GOOS == "windows" {
		t.Skip("permission bits work differently on windows")
	}
	if os.Geteuid() == 0 {
		t.Skip("running as root: permission bits are not enforced, can't test unreadable files")
	}
	dir := t.TempDir()
	blocked := filepath.Join(dir, "blocked.txt")
	writeFile(t, blocked, []byte("secret-needle"))
	if err := os.Chmod(blocked, 0o000); err != nil {
		t.Fatal(err)
	}
	defer os.Chmod(blocked, 0o644)
	writeFile(t, filepath.Join(dir, "readable.txt"), []byte("secret-needle too"))

	matches, warnings := runSearch(t, `secret-needle`, dir)
	want := []string{filepath.Join(dir, "readable.txt")}
	if !equal(matches, want) {
		t.Errorf("matches = %v, want %v", matches, want)
	}
	if warnings == "" {
		t.Errorf("expected a warning about the unreadable file, got none")
	}
}

func TestNonexistentRootReturnsError(t *testing.T) {
	re := regexp.MustCompile(`.`)
	err := Run(Options{Root: filepath.Join(t.TempDir(), "does-not-exist"), Pattern: re}, func(string) {})
	if err == nil {
		t.Fatal("expected an error for a nonexistent root, got nil")
	}
}

func TestUnreadableSubdirectoryWarnsAndContinues(t *testing.T) {
	if runtime.GOOS == "windows" {
		t.Skip("permission bits work differently on windows")
	}
	if os.Geteuid() == 0 {
		t.Skip("running as root: permission bits are not enforced, can't test unreadable directories")
	}
	dir := t.TempDir()
	blockedDir := filepath.Join(dir, "blocked")
	if err := os.MkdirAll(blockedDir, 0o755); err != nil {
		t.Fatal(err)
	}
	writeFile(t, filepath.Join(blockedDir, "secret.txt"), []byte("x"))
	if err := os.Chmod(blockedDir, 0o000); err != nil {
		t.Fatal(err)
	}
	defer os.Chmod(blockedDir, 0o755)
	writeFile(t, filepath.Join(dir, "visible.txt"), []byte("findme"))

	matches, warnings := runSearch(t, `findme`, dir)
	want := []string{filepath.Join(dir, "visible.txt")}
	if !equal(matches, want) {
		t.Errorf("matches = %v, want %v", matches, want)
	}
	if warnings == "" {
		t.Errorf("expected a warning about the unreadable directory, got none")
	}
}

func TestDefaultRootIsCurrentDirectory(t *testing.T) {
	dir := t.TempDir()
	writeFile(t, filepath.Join(dir, "here.txt"), []byte("x"))

	cwd, err := os.Getwd()
	if err != nil {
		t.Fatal(err)
	}
	defer os.Chdir(cwd)
	if err := os.Chdir(dir); err != nil {
		t.Fatal(err)
	}

	re := regexp.MustCompile(`here`)
	var got []string
	if err := Run(Options{Pattern: re}, func(path string) { got = append(got, path) }); err != nil {
		t.Fatalf("Run: %v", err)
	}
	if len(got) != 1 || got[0] != filepath.Join(".", "here.txt") {
		t.Errorf("got %v, want a single match for ./here.txt", got)
	}
}

func equal(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	sort.Strings(a)
	sort.Strings(b)
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}
