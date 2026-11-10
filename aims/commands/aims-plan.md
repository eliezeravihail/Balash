---
description: Ground the product, choose one design objective (feasibility-gated), and file the durable design knowledge it surfaces — ADRs, requirements, insights — into the capsa capsule, each anchored.
---

# /aims-plan — skeleton

Invoke the `aims-guide` skill as the **Guide**. Then:

1. **Discovery.** Ground product behavior by asking focused questions; surface every action's
   complement. Do not guess. (`references/discovery.md`)
2. **Choose one design objective** for the current state, and **feasibility-gate it** before
   committing — if it rests on an unproven load-bearing assumption, make proving it the objective.
   (`references/objective-selection.md`)
3. **File the durable knowledge** the plan surfaces into `.capsa/` (see the skill, §3):
   - ownership/boundary choices → `decisions/` (ADRs), placed at the component they govern;
   - commitments → `requirements/` (with verification block);
   - lasting design reasoning → `insights/design/` or `insights/dev/`.
4. **Anchor each record** with `aims anchor` — `anchors:` for file-content claims, `--shape` for
   structural claims. Never hash by hand.
5. Hand off to `/aims-build` (or delegate to a Worker if the cost lever is enabled).

Output: the chosen objective, and the records filed (paths), not implementation code.
