---
description: Execute the chosen design objective (directly, or via a Worker), then file any insights that arose into the capsa capsule, each anchored.
---

# /aims-build — skeleton

Invoke the `aims-guide` skill. Build the objective chosen in `/aims-plan`, keeping the design as the
goal and the feature behavior as a constraint the design must satisfy. Then:

1. **Implement** the objective (yourself, or hand it to a Worker subagent framed around the design
   outcome — the optional cost lever).
2. **File insights if any arose** into `.capsa/` (see the skill, §3):
   - engineering lessons (what was tried, what failed, why) → `insights/dev/`;
   - notes tied to specific code → `insights/code/` with `code_globs`.
   Do not manufacture insights; file them only when there is something durable to record.
3. **Anchor each record** with `aims anchor` (`anchors:` for file-content claims, `--shape` for
   structural). Never hash by hand.
4. Update the loop cursor in `.aims/state.md` (run-state — never in the capsule).

Output: the built change and the records filed (paths).
