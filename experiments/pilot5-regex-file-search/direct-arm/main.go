// Command regexfilesearch searches a directory tree and reports every file
// whose name or content matches a given regular expression.
//
// Usage:
//
//	regexfilesearch <pattern> [root-directory]
//
// root-directory defaults to the current directory. Matching paths are
// printed to stdout, one per line.
package main

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"

	"regexfilesearch/internal/search"
)

func main() {
	os.Exit(run(os.Args, os.Stdout, os.Stderr))
}

// run contains all of main's logic, parameterized on args/stdout/stderr so
// it can be exercised from tests without touching the real process streams.
// args is the full os.Args-style slice, i.e. args[0] is the program name.
func run(args []string, stdout, stderr io.Writer) int {
	progName := "regexfilesearch"
	if len(args) > 0 {
		progName = filepath.Base(args[0])
	}
	cliArgs := args[1:]

	if len(cliArgs) < 1 || len(cliArgs) > 2 {
		fmt.Fprintf(stderr, "usage: %s <pattern> [root-directory]\n", progName)
		return 2
	}

	patternStr := cliArgs[0]
	root := "."
	if len(cliArgs) == 2 {
		root = cliArgs[1]
	}

	re, err := regexp.Compile(patternStr)
	if err != nil {
		fmt.Fprintf(stderr, "%s: invalid regular expression %q: %v\n", progName, patternStr, err)
		return 2
	}

	out := bufio.NewWriter(stdout)
	walkErr := search.Run(search.Options{
		Root:    root,
		Pattern: re,
		Stderr:  stderr,
	}, func(path string) {
		fmt.Fprintln(out, path)
	})
	if flushErr := out.Flush(); flushErr != nil {
		fmt.Fprintf(stderr, "%s: %v\n", progName, flushErr)
		return 1
	}
	if walkErr != nil {
		fmt.Fprintf(stderr, "%s: %v\n", progName, walkErr)
		return 1
	}
	return 0
}
