# aims

**Skeleton — v0.1.0.** aims makes design the goal of coding-agent work *and* makes the design
knowledge durable across the years a project actually lives. It merges Balash's design method with a
capsa-format knowledge layer.

> This is an initial skeleton scaffolded for review. Contracts and structure are in place; method
> bodies point at Balash's existing references, and the two active pieces (one hook, one command) are
> specified with stubs, not yet fully implemented. The plan behind it is
> [`docs/plans/aims-merge.md`](../docs/plans/aims-merge.md) in the Balash repo.

## The three layers

1. **The design method (the brain)** — discovery + a design objective, a feasibility gate,
   ownership/encapsulation principles, a subtractive pass, and a review panel. Kept whole from Balash.
   Entry point: [`skills/aims-guide/SKILL.md`](skills/aims-guide/SKILL.md).
2. **The durable knowledge layer** — the method writes ADRs, requirements, and insights into a
   **capsa** capsule (`.capsa/` in the project repo): one record per file, in a containment tree where
   **placement is scope**. Not coupled to a single source file (fragile); not one central folder that
   bloats (unreadable). Relevance is derived from the path. capsa is vendored under
   [`vendor/capsa/`](vendor/capsa/); the subset aims uses and the fields it adds are in
   [`docs/format-profile.md`](docs/format-profile.md).
3. **One advisory signal** — a single read-time hook recomputes a record's *anchor* and flags possible
   drift from the code it describes. It never blocks and never auto-invalidates. See
   [`hooks/staleness-read.md`](hooks/staleness-read.md).

## What aims deliberately does *not* have

- No memory/consolidation/doctor/lint machinery. capsa's passivity plus the method's
  documentation discipline keep design rationale current by construction.
- No write hook. Records are written by explicit method instruction (plan time: ADRs + insights;
  build time: insights if any), and anchors are stamped by an explicit command
  ([`tools/aims-anchor`](tools/aims-anchor.md)) the method calls when it files a record.
- No enforcement built into the format. Content invariants ("core stays pure") are an **opt-in**
  fitness-function that emits capsa `X-` findings, never part of the passive layer.

## The staleness model — the anchor follows the claim

| A record claims about… | Anchor | Drift = |
|---|---|---|
| **file content** | `anchors:` — whole-file content hash per file | the file changed |
| **arrangement / structure** | placement + `shape:` fingerprint (child-name set of the subtree) | the shape changed (moved / renamed / merged) |
| **a content invariant** ("core stays pure") | just `anchors:` on the files that embody it — detection needs no new mechanism | a governed file changed → re-verify |

A content invariant is not a third mechanism: it is `anchors:` on the files carrying the rule, so the
existing hash flags "re-verify" when they change. Only *automatic* enforcement (a verdict without a
human re-check) would need a code scanner, and that stays an opt-in fitness-function emitting capsa
`X-` findings — never part of the passive layer.

Because the hook re-reads the *actual* file or tree, it catches drift whether the change went through
aims or was made by hand or another tool.

## Commands

- `/aims-plan` — discovery + design objective; write the ADRs/requirements/insights the design
  surfaces, each anchored.
- `/aims-build` — execute the objective; write insights if any arise, anchored.
- `/aims-review` — the review panel over the result.

## Guide→Worker (optional)

aims can hand execution from a strong Guide model to a cheaper Worker model to save cost. This is its
*only* justification — a single agent running the method reaches the same design decisions as the
split — so it is **off by default** and used only when the cost math pays.

## Name

aims = AI Manager System, and "aims / goals": the design *aim* is what the system manages.
