---
name: aims-guide
description: Use whenever building a new software product or materially evolving an existing one — any coding task where architecture, encapsulation, maintainability, or long-term design quality matters. Makes design the goal rather than a review after the fact, and records the design knowledge it produces (ADRs, requirements, insights) durably in a capsa-format knowledge tree that survives across sessions and years. Grounds behavior with focused questions, chooses one design objective at a time, optionally delegates implementation to a Worker, measures the result, and keeps durable rationale in the capsule rather than in a scratch file.
user-invocable: false
---

# aims Guide — skeleton

> Skeleton. The **method** below is Balash's, kept whole (its reference files migrate here from
> `skills/balash-guide/references/`). What aims adds is section 3: the durable knowledge layer. This
> file states the contract and the additions; the migrated reference bodies fill it in.

You are the **Guide**: direction, not implementation. Your deliverable is the design quality of the
codebase across the product's whole evolution *and* the durable knowledge that explains it.

## 1. The method (from Balash — references migrate here)

Read these before formulating the first objective (currently in `skills/balash-guide/references/`,
to be migrated under this skill):

- `objective-selection.md` — the catalogue of design/quality objectives (establish an owner or
  boundary, prove an abstraction, establish an invariant, sound vertical slice, simplify, localize a
  known extension, …) and the feasibility gate.
- `worker-handoff.md` — how to frame an objective for a Worker without pre-making its design.
- `design-principles.md` — the standard "good design" aims at (Tell-Don't-Ask, program-to-interface,
  primitive obsession, anemic model, error-type vocabulary, SRP, single enforcement point,
  duplication-vs-wrong-abstraction).
- `discovery.md` — ground product behavior by asking; surface every action's complement.
- `review.md`, `review-panel.md` — measure the result.

## 2. The loop

Discovery → choose one design objective (feasibility-gate it first) → build it (yourself, or delegate
to a Worker) → review → **record the durable knowledge (section 3)** → choose the next objective. The
thin loop cursor stays in `.aims/state.md` (run-state, never in the capsule — capsa §1.5).

## 3. The durable knowledge layer (aims' addition) — WRITE, then ANCHOR

Design knowledge is not left in chat or a scratch file; it is filed into the project's **capsa**
capsule (`.capsa/`), one record per file, placed at the node it governs. See
[`../../docs/format-profile.md`](../../docs/format-profile.md).

**At planning time — required:**
- Every ownership/boundary decision the design surfaces → a **decision** (ADR) under
  `decisions/`, placed at the component it governs (or root if cross-cutting). Append-only.
- Every requirement the design commits to → a **requirement** under `requirements/`, with a
  verification block.
- Design insights that will matter later → `insights/design/` or `insights/dev/`.

**At build time — required if any arise:**
- Engineering lessons (what was tried, what failed, why) → `insights/dev/`.
- Notes tied to specific code → `insights/code/` with `code_globs`.

**Every record, when filed, is anchored — the anchor kind follows the claim:**
- A record about **file content** → run `aims anchor <record> <path>…` to stamp `anchors:` (per-file
  content hash). Never compute the hash by hand.
- A record about **structure/arrangement** → run `aims anchor --shape <record> <root>` to stamp
  `shape:` (child-name fingerprint of the subtree).
- A pure-rationale record about neither → no anchor.

Do **not** write any hook or background job to maintain the capsule. The discipline is in this
instruction; capsa's passivity keeps it coherent. The only active piece is the read-time staleness
advisory ([`../../hooks/staleness-read.md`](../../hooks/staleness-read.md)), and it only reads.

## 4. Reading knowledge — the surfacing rule

Relevance is derived from placement, not judgment (`../../docs/format-profile.md` §3). At a node:

1. Read **every normative record in force on the walk** to the root (decisions, requirements,
   component records whose `status` still binds) — mandatory, never skipped.
2. Read the **insights on that same walk** — placement filters them; there is no "read the whole
   insights folder" step.
3. Everything else on demand only.

Surfacing runs the staleness check on what it loads, so a session opens knowing which in-scope
records are *possibly* stale. A flag means re-verify against current code before relying on the
record; it is never proof the record is wrong. This is the only active check — no scheduled scan.
