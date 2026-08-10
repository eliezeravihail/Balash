#!/usr/bin/env python3
"""Balash UserPromptSubmit hook.

Fires on every user turn. If the current project is a Balash project (it has a
`.balash/state.md`), it injects a short reminder of the current design objective
into the model's context — so the goal stays present even when the conversation
drifts onto something unrelated, and even across context compaction. On any
project without that file, or on any parsing trouble, it stays completely silent
and never blocks the turn.

Contract: reads the hook JSON on stdin, prints (on success) a JSON object with
`hookSpecificOutput.additionalContext`, and always exits 0.
"""

import json
import os
import sys


def _load_input() -> dict:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except Exception:
        return {}


def _project_dir(data: dict) -> str:
    # Prefer the hook-supplied cwd, then Claude's project env var, then process cwd.
    for candidate in (data.get("cwd"), os.environ.get("CLAUDE_PROJECT_DIR"), os.getcwd()):
        if candidate:
            return candidate
    return "."


def _find_state_file(project_dir: str) -> str | None:
    # The state file lives at <project>/.balash/state.md. Walk up a few levels so
    # the hook still works when the cwd is a subdirectory of the project root.
    here = os.path.abspath(project_dir)
    for _ in range(6):
        candidate = os.path.join(here, ".balash", "state.md")
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(here)
        if parent == here:
            break
        here = parent
    return None


def _sections(text: str) -> dict[str, list[str]]:
    """Split a markdown doc into {heading: [content lines]}, dropping HTML comments."""
    sections: dict[str, list[str]] = {}
    current = ""
    sections[current] = []
    in_comment = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if in_comment:
            if "-->" in line:
                in_comment = False
            continue
        stripped = line.strip()
        if stripped.startswith("<!--"):
            if "-->" not in stripped:
                in_comment = True
            continue
        if line.startswith("## "):
            current = line[3:].strip().lower()
            sections[current] = []
            continue
        sections.setdefault(current, []).append(line)
    return sections


def _first_real(lines: list[str]) -> str:
    for line in lines:
        if line.strip():
            return line.strip()
    return ""


def _value_after_marker(lines: list[str], i: int) -> str:
    # The objective value is on a following line. Accept the first prose line, but
    # stop at the next field marker (**...:**) — an empty objective must read as empty,
    # not spill into the next field or a checkbox placeholder.
    for line in lines[i + 1:]:
        s = line.strip()
        if not s:
            continue
        if s.startswith("**") or s.startswith("-") or s.startswith("#"):
            return ""  # hit the next field / a list placeholder → objective is unset
        return s
    return ""


def _objective(sections: dict[str, list[str]]) -> str:
    lines = sections.get("current objective", [])
    for i, line in enumerate(lines):
        s = line.strip()
        if s.lower().startswith("**objective:**"):
            after = s.split("**", 2)[-1].strip()  # value inline after the marker
            return after if after else _value_after_marker(lines, i)
    return ""


def _cursor(sections: dict[str, list[str]]) -> str:
    return _first_real(sections.get("loop cursor", []))


def _mode(sections: dict[str, list[str]]) -> str:
    # auto | stepped. Absent/unrecognized reads as auto (the default).
    value = _first_real(sections.get("mode", [])).lower()
    return "stepped" if value.startswith("stepped") else "auto"


def _emit(context: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }))


def main() -> int:
    data = _load_input()
    state_path = _find_state_file(_project_dir(data))
    if not state_path:
        return 0  # not a Balash project — stay silent

    try:
        with open(state_path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except Exception:
        return 0

    sections = _sections(text)
    objective = _objective(sections)
    cursor = _cursor(sections)
    mode = _mode(sections)

    if objective:
        lines = [
            "[balash-guide active] This project carries a durable design objective in "
            ".balash/state.md — treat that file, not this conversation, as the source of truth "
            "for what is being built.",
            f"Current objective: {objective}",
        ]
        if cursor:
            lines.append(f"Loop cursor: {cursor}")
        if mode == "stepped":
            lines.append(
                "Mode: stepped — advance only on an explicit balash phase command (plan / build / "
                "review); do NOT auto-advance the loop, and a returning Worker parks at "
                "executed:awaiting-review rather than being evaluated automatically."
            )
        lines.append(
            "Before any code work this turn, reconcile with .balash/state.md and keep this "
            "objective in view even if the request is unrelated; do not let it drop. When a "
            "Worker reports an objective met, verify the evidence yourself before believing it."
        )
        _emit("\n".join(lines))
    else:
        _emit(
            "[balash-guide active] .balash/state.md exists but no current objective is set. "
            "If this turn involves building or evolving software, (re)establish the design "
            "objective via the balash-guide skill before delegating to a Worker."
        )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Never break the user's turn because of this hook.
        sys.exit(0)
