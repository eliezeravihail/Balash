#!/usr/bin/env python3
"""Balash UserPromptSubmit hook.

Fires on every user turn. If the current project is a Balash project (it has a
`.balash/state.md`), it injects a short reminder of the current design objective
into the model's context — so the goal stays present even when the conversation
drifts onto something unrelated, and even across context compaction. On any
project without that file it stays completely silent and never blocks the turn.

Schema contract: `assets/state-template.md` and `assets/objective-template.md` are the
AUTHORITATIVE shape of the two files this hook reads, and it depends on the headings/
markers named there:
  - `.balash/state.md`: `## Mode`, `## Loop cursor`, `## Active objective` (a path under
    `.balash/objectives/`, relative to the project root).
  - the file `## Active objective` points at: `**Kind:**` and `**Objective:**` markers in
    its top matter (before the first `## ` heading).
`state.md` deliberately carries no objective content itself — it only points at the
objective file that does. That template, not this parser, owns the schema; the skill that
writes these files and this hook that reads them are two sides of the same contract.
Because a drifted file (a renamed heading, a hand-edit, a pointer to a missing file) would
otherwise make the goal stop being injected *silently*, this hook does NOT stay silent on a
filled state file it cannot structurally recognize: it says so, so the drift is visible
rather than a goal that quietly evaporates. It still never blocks the turn.

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
    """Split a markdown doc into {heading: [content lines]}, dropping HTML comments.

    The "" key holds the top-matter lines before the first "## " heading — that is where
    an objective file's `**Kind:**` / `**Objective:**` markers live.
    """
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
    # The value is on a following line. Accept the first prose line, but stop at the next
    # field marker (**...:**) or a heading — an empty field must read as empty, not spill
    # into the next field or a checkbox placeholder.
    for line in lines[i + 1:]:
        s = line.strip()
        if not s:
            continue
        if s.startswith("**") or s.startswith("-") or s.startswith("#"):
            return ""  # hit the next field / a list placeholder → unset
        return s
    return ""


def _marker_value(lines: list[str], marker: str) -> str:
    """Find `**marker:**` among `lines` and return its value (inline or on the next line)."""
    needle = f"**{marker.lower()}:**"
    for i, line in enumerate(lines):
        s = line.strip()
        if s.lower().startswith(needle):
            after = s.split("**", 2)[-1].strip()  # value inline after the marker
            return after if after else _value_after_marker(lines, i)
    return ""


def _cursor(sections: dict[str, list[str]]) -> str:
    return _first_real(sections.get("loop cursor", []))


def _mode(sections: dict[str, list[str]]) -> str:
    # auto | stepped. Absent/unrecognized reads as auto (the default).
    value = _first_real(sections.get("mode", [])).lower()
    return "stepped" if value.startswith("stepped") else "auto"


def _active_objective_path(sections: dict[str, list[str]]) -> str:
    return _first_real(sections.get("active objective", []))


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
            state_text = fh.read()
    except Exception:
        return 0

    state_sections = _sections(state_text)
    cursor = _cursor(state_sections)
    mode = _mode(state_sections)
    active_path = _active_objective_path(state_sections)

    # Drift guard #1: the loop-control anchors live under "## Loop cursor" (and "## Mode"). If a
    # filled state file lacks that heading entirely, the schema has drifted from
    # assets/state-template.md and the hook can no longer tell where the loop is parked — surface
    # that loudly instead of silently degrading to the generic "no objective" nudge (which reads as
    # "nothing to do" rather than "the state file is broken"). A genuinely empty/whitespace file is
    # not drift.
    has_content = any(line.strip() for line in state_text.splitlines())
    if "loop cursor" not in state_sections and has_content:
        _emit(
            "[balash-guide] .balash/state.md exists but its structure is not recognized: the "
            "'## Loop cursor' heading is missing, so this hook cannot tell where the loop is parked "
            "and nothing is being injected this turn. The state file's headings have likely drifted "
            "from the schema in assets/state-template.md — realign them (headings/markers are the "
            "contract between the skill that writes state.md and this hook that reads it)."
        )
        return 0

    objective = ""
    kind = ""
    broken_pointer = False
    if active_path:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(state_path)))
        obj_abspath = os.path.normpath(os.path.join(project_root, active_path))
        try:
            with open(obj_abspath, "r", encoding="utf-8") as fh:
                obj_text = fh.read()
            obj_top = _sections(obj_text).get("", [])
            objective = _marker_value(obj_top, "objective")
            kind = _marker_value(obj_top, "kind")
        except Exception:
            broken_pointer = True

    # Drift guard #2: state.md names an Active objective file this hook can't read (missing, moved,
    # or unparsable). Say so rather than silently falling back to "no current objective" — that
    # would misreport a real, in-flight objective as absent.
    if broken_pointer:
        _emit(
            f"[balash-guide] .balash/state.md points 'Active objective' at '{active_path}', but that "
            "file could not be read. The goal is NOT being injected this turn — check the path, or "
            "that the objective file matches the schema in assets/objective-template.md."
        )
        return 0

    if objective:
        lines = [
            "[balash-guide active] This project carries a durable design objective in "
            f"{active_path} (pointed to by .balash/state.md) — treat those files, not this "
            "conversation, as the source of truth for what is being built.",
            f"Current objective ({kind or 'kind unset'}): {objective}",
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
            "Before any code work this turn, reconcile with .balash/state.md and the objective file "
            "it points at, and keep this objective in view even if the request is unrelated; do not "
            "let it drop. When a Worker reports an objective met, measure the evidence yourself "
            "rather than trusting the report — the loop directs and measures, it does not police."
        )
        _emit("\n".join(lines))
    else:
        _emit(
            "[balash-guide active] .balash/state.md exists but no Active objective is set. "
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
