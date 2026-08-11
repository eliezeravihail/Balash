package main

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func writeFile(t *testing.T, path string, content []byte) {
	t.Helper()
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, content, 0o644); err != nil {
		t.Fatal(err)
	}
}

func TestRunUsageErrors(t *testing.T) {
	cases := [][]string{
		{"prog"},
		{"prog", "a", "b", "c"},
	}
	for _, args := range cases {
		var out, errOut bytes.Buffer
		code := run(args, &out, &errOut)
		if code != 2 {
			t.Errorf("args=%v: exit code = %d, want 2", args, code)
		}
		if !strings.Contains(errOut.String(), "usage") {
			t.Errorf("args=%v: stderr = %q, want it to mention usage", args, errOut.String())
		}
	}
}

func TestRunInvalidRegex(t *testing.T) {
	var out, errOut bytes.Buffer
	code := run([]string{"prog", "("}, &out, &errOut)
	if code != 2 {
		t.Errorf("exit code = %d, want 2", code)
	}
	if !strings.Contains(errOut.String(), "invalid regular expression") {
		t.Errorf("stderr = %q, want mention of invalid regular expression", errOut.String())
	}
}

func TestRunNonexistentRoot(t *testing.T) {
	var out, errOut bytes.Buffer
	missing := filepath.Join(t.TempDir(), "nope")
	code := run([]string{"prog", "x", missing}, &out, &errOut)
	if code != 1 {
		t.Errorf("exit code = %d, want 1", code)
	}
	if errOut.String() == "" {
		t.Errorf("expected an error message on stderr")
	}
}

func TestRunEndToEnd(t *testing.T) {
	dir := t.TempDir()
	writeFile(t, filepath.Join(dir, "alpha.txt"), []byte("nothing"))
	writeFile(t, filepath.Join(dir, "beta.txt"), []byte("contains gopher"))
	writeFile(t, filepath.Join(dir, "gopher.log"), []byte("empty"))

	var out, errOut bytes.Buffer
	code := run([]string{"prog", "gopher", dir}, &out, &errOut)
	if code != 0 {
		t.Fatalf("exit code = %d, want 0; stderr=%q", code, errOut.String())
	}

	lines := strings.Split(strings.TrimRight(out.String(), "\n"), "\n")
	want := map[string]bool{
		filepath.Join(dir, "beta.txt"):   true,
		filepath.Join(dir, "gopher.log"): true,
	}
	if len(lines) != len(want) {
		t.Fatalf("got %d matches (%v), want %d", len(lines), lines, len(want))
	}
	for _, l := range lines {
		if !want[l] {
			t.Errorf("unexpected match line: %q", l)
		}
	}
}

func TestRunDefaultsRootToCurrentDirectory(t *testing.T) {
	dir := t.TempDir()
	writeFile(t, filepath.Join(dir, "onlyhere.txt"), []byte("x"))

	cwd, err := os.Getwd()
	if err != nil {
		t.Fatal(err)
	}
	defer os.Chdir(cwd)
	if err := os.Chdir(dir); err != nil {
		t.Fatal(err)
	}

	var out, errOut bytes.Buffer
	code := run([]string{"prog", "onlyhere"}, &out, &errOut)
	if code != 0 {
		t.Fatalf("exit code = %d, want 0; stderr=%q", code, errOut.String())
	}
	if strings.TrimSpace(out.String()) != filepath.Join(".", "onlyhere.txt") {
		t.Errorf("stdout = %q, want ./onlyhere.txt", out.String())
	}
}
