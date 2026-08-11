// Command regex-file-search walks a directory tree and reports every file
// whose name or content matches a given regular expression.
//
// Usage:
//
//	regex-file-search <pattern> [root]
//
// root defaults to the current working directory. Matching files are
// printed one path per line to stdout.
package main

import (
	"bufio"
	"errors"
	"fmt"
	"os"

	"regex-file-search/internal/match"
	"regex-file-search/internal/walk"
)

func main() {
	pattern, root, err := parseArgs(os.Args[1:]) // positional: <pattern> [root=.]
	if err != nil {
		fmt.Fprintln(os.Stderr, "usage: regex-file-search <pattern> [root]")
		os.Exit(2)
	}

	matcher, err := match.New(pattern)
	if err != nil {
		fmt.Fprintln(os.Stderr, "invalid pattern:", err)
		os.Exit(2)
	}

	out := bufio.NewWriter(os.Stdout)
	exitCode := 0

	err = walk.Walk(root, matcher, func(r walk.Result) {
		switch {
		case r.Err != nil:
			fmt.Fprintf(os.Stderr, "%s: %v\n", r.Path, r.Err)
			exitCode = 1
		case r.Matched:
			fmt.Fprintln(out, r.Path)
		}
	})
	out.Flush()
	if err != nil {
		fmt.Fprintln(os.Stderr, "search failed:", err)
		exitCode = 1
	}
	os.Exit(exitCode)
}

// parseArgs interprets the CLI's positional arguments: a required regex
// pattern, followed by an optional root path that defaults to the
// current directory. It is intentionally minimal — no flags — per the
// design's non-goal of extra CLI surface.
func parseArgs(args []string) (pattern, root string, err error) {
	switch len(args) {
	case 1:
		return args[0], ".", nil
	case 2:
		return args[0], args[1], nil
	default:
		return "", "", errors.New("expected 1 or 2 positional arguments: <pattern> [root]")
	}
}
