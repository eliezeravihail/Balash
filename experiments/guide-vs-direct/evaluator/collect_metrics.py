#!/usr/bin/env python3
"""Collect low-interpretation repository metrics for one experiment snapshot.

This intentionally avoids a single quality score. It records facts useful for later
blinded review. Run from any directory; pass the repository path.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
from collections import defaultdict
from pathlib import Path

EXCLUDE_DIRS = {'.git', '.venv', 'venv', '__pycache__', '.pytest_cache', 'node_modules', 'build', 'dist'}
TEST_MARKERS = {'tests', 'test'}


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def py_files(repo: Path):
    for p in repo.rglob('*.py'):
        rel = p.relative_to(repo)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        yield p, rel


def is_test(rel: Path) -> bool:
    name = rel.name.lower()
    return any(part.lower() in TEST_MARKERS for part in rel.parts[:-1]) or name.startswith('test_') or name.endswith('_test.py')


def module_name(rel: Path) -> str:
    parts = list(rel.with_suffix('').parts)
    if parts[-1] == '__init__':
        parts = parts[:-1]
    return '.'.join(parts)


def import_graph(repo: Path):
    files = list(py_files(repo))
    modules = {module_name(rel): rel for _, rel in files if not is_test(rel)}
    graph: dict[str, set[str]] = defaultdict(set)
    syntax_errors = []
    for p, rel in files:
        if is_test(rel):
            continue
        src_mod = module_name(rel)
        try:
            tree = ast.parse(p.read_text(encoding='utf-8'), filename=str(rel))
        except Exception as e:
            syntax_errors.append({'file': str(rel), 'error': str(e)})
            continue
        for n in ast.walk(tree):
            candidates = []
            if isinstance(n, ast.Import):
                candidates.extend(a.name for a in n.names)
            elif isinstance(n, ast.ImportFrom) and n.module:
                candidates.append(n.module)
            for c in candidates:
                for m in modules:
                    if c == m or c.startswith(m + '.') or m.startswith(c + '.'):
                        if m != src_mod:
                            graph[src_mod].add(m)
    return modules, graph, syntax_errors


def cycles(graph: dict[str, set[str]]):
    found = set()
    stack = []
    visiting = set()
    visited = set()

    def dfs(n):
        visiting.add(n); stack.append(n)
        for m in graph.get(n, ()):
            if m in visiting:
                i = stack.index(m)
                cyc = tuple(stack[i:] + [m])
                # canonical rotation for dedupe
                body = cyc[:-1]
                rots = [body[i:] + body[:i] for i in range(len(body))]
                canon = min(tuple(r) for r in rots)
                found.add(canon)
            elif m not in visited:
                dfs(m)
        stack.pop(); visiting.remove(n); visited.add(n)

    for n in list(graph):
        if n not in visited:
            dfs(n)
    return [list(c) for c in sorted(found)]


def diff_metrics(repo: Path, stage: int):
    tag = f'stage-{stage-1}'
    if stage == 1:
        code, out = run(['git', 'show', '--format=', '--numstat', 'HEAD'], repo)
    else:
        code, out = run(['git', 'diff', '--numstat', tag, 'HEAD'], repo)
    if code != 0:
        return {'available': False, 'error': out}
    rows = []
    for line in out.splitlines():
        parts = line.split('\t')
        if len(parts) != 3:
            continue
        a, d, path = parts
        try: a_n = int(a)
        except: a_n = None
        try: d_n = int(d)
        except: d_n = None
        rows.append({'path': path, 'added': a_n, 'deleted': d_n})
    prod = [r for r in rows if not (r['path'].startswith('tests/') or '/tests/' in r['path'] or Path(r['path']).name.startswith('test_'))]
    return {
        'available': True,
        'files_changed': len(rows),
        'production_files_changed': len(prod),
        'added_lines': sum(r['added'] or 0 for r in rows),
        'deleted_lines': sum(r['deleted'] or 0 for r in rows),
        'files': rows,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('repo', type=Path)
    ap.add_argument('--stage', type=int, required=True)
    args = ap.parse_args()
    repo = args.repo.resolve()

    files = list(py_files(repo))
    prod = [(p, r) for p, r in files if not is_test(r)]
    tests = [(p, r) for p, r in files if is_test(r)]
    modules, graph, syntax_errors = import_graph(repo)

    loc = {}
    for p, rel in prod:
        try:
            loc[str(rel)] = len(p.read_text(encoding='utf-8').splitlines())
        except Exception:
            pass

    test_code, test_out = run(['python', '-m', 'unittest', 'discover', '-s', 'tests', '-v'], repo)
    if test_code != 0 and not (repo / 'tests').exists():
        test_out = 'No tests/ directory found; unittest discovery not run meaningfully.'

    data = {
        'stage': args.stage,
        'repository': str(repo),
        'production_python_files': len(prod),
        'test_python_files': len(tests),
        'production_loc': sum(loc.values()),
        'largest_production_files': sorted(loc.items(), key=lambda x: x[1], reverse=True)[:10],
        'module_fan_out': {m: len(ds) for m, ds in sorted(graph.items(), key=lambda x: (-len(x[1]), x[0]))},
        'import_cycles': cycles(graph),
        'syntax_errors': syntax_errors,
        'stage_diff': diff_metrics(repo, args.stage),
        'unittest': {'exit_code': test_code, 'output_tail': '\n'.join(test_out.splitlines()[-80:])},
    }
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
