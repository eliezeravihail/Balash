# Plan: Balash → aims — a design method on a capsa-format knowledge layer

Status: plan (agreed direction; not yet built)

## What this merges, and why

Two projects by the same author solve halves of one problem:

- **Balash** is a *design-quality method*: make design the goal — discovery, a feasibility gate,
  ownership/encapsulation principles, a subtractive pass, an optional Guide→Worker split, a review
  panel. It is strong at producing good design *in a session*, but it has **no instrumentation for
  long-term development**: the design knowledge it generates (why a boundary is where it is, what was
  deliberately cut, which invariant is load-bearing) does not durably accumulate across the years a
  project actually lives.
- **aims** contributes the missing half: *durable, long-lived documentation discipline* — knowledge
  that survives compaction and hands the next session (or the next year) the rationale, not just the
  code. But aims' original mechanism for this — a self-maintaining "memory tree" with
  marker/consolidation/lint/doctor machinery — is heavier than the job needs.
- **capsa** turns out to be the right *storage layer* for that durable knowledge: a **passive file
  format** (a `.capsa/`-style tree of Markdown+YAML records), not a program — no hooks, no daemon,
  nothing to run or maintain. Its core rule, *placement = scope*, is exactly what the knowledge layer
  needs.

**Direction:** one system, **named `aims`** (AI Manager System, and "aims/goals" — Balash's own thesis
is that the design *aim* is what we manage). aims will open in its own home as the fuller system the
author is planning; Balash's method converts into it.

- **Balash's method is the design brain** — kept whole (discovery, feasibility gate, ownership,
  subtractive pass, review panel, `design-principles.md`).
- **A capsa-format tree is the durable knowledge layer** — where ADRs, requirements, and insights live,
  addressed and placement-scoped.
- **Guide→Worker is demoted to an optional cost lever** — one strong Guide model can hand off execution
  to a cheaper Worker; that is its *only* justification (a prior experiment showed a single agent
  running the method reaches the same design decisions as the split), so it is off by default and used
  only when the cost math pays.

## The documentation model (the core decision)

The main doubt this plan resolves: **documentation coupled to each source file (aims' original) vs. a
central folder the tool owns (Balash's).** Both are the wrong axis:

- *Coupled to a source file* is fragile: code moves/renames/splits and the note is orphaned; an insight
  about a **boundary** belongs to no single file; a requirement that spans files has nowhere to live.
- *A central folder* bloats: over time it becomes a monolith every session must read in full, unable to
  tell relevant from irrelevant.

capsa dissolves the binary with a third shape: **one record per file, in a containment tree, where the
record's placement in the tree *is* its scope.**

- **One fact, one file** — no monolith to read whole.
- **Placement = scope** — a record applies to the node holding it and everything beneath; relevance is
  *derived from the path* (walk from the node you are touching up to the root), never by reading
  everything and filtering by hand. This is coupled to the **project's structure** (a subtree = a
  component), not to a single source file.
- **Single home** — each fact lives in exactly one record; edges reference by address, never duplicate.
- **Passive** — the format has no machinery; it is data, tool-agnostic, survives any tool and years of
  churn.

### Writing records — explicit instruction, no write hook

Records are written by the **method**, not by background machinery:

- At **planning** time the method requires recording **ADRs** (ownership/boundary decisions the design
  surfaces) and design **insights**.
- At **build** time it requires recording **insights** *if any arise*.

There is no write hook and no consolidation machinery. The bet — validated by capsa's passivity and by
the prior evolving-task experiment (the method itself drives good docs) — is that in-context
instruction at documentation time is enough. Adding machinery to keep a mutable store coherent would be
*patching a problem the method already prevents*.

### Staleness — one read-time signal, and the anchor follows the claim

The one hard question: how does a reader know a record has drifted from the code it describes? The
answer is a single principle — **the anchor must match the ontology of the claim** — giving three
tiers, only the first two of which live in the passive layer:

| The record claims about… | Anchor | Drift = | Catches out-of-band edits? |
|---|---|---|---|
| **file content** ("this function does X") | `anchors: [{path, hash}]` — whole-file content hash, a **list** (0..n) | the file changed | yes — the hook re-reads the actual file |
| **arrangement / structure** ("we split core/ and api/") | **placement** (the node the record sits at) + a **shape fingerprint** (the set of child names under that node) | the shape changed (moved / renamed / merged) | yes — the hook re-reads the actual tree |
| **a content invariant** ("nothing under core/ does I/O") | just `anchors:` on the files that embody the rule — no new mechanism | a governed file changed → re-verify against the rule | yes — the hook re-reads the actual file |

**Tier 1 — file records.** Anchor to the specific files the record is about, one content hash each
(whole-file: a stable address; line ranges drift and are rejected). The read-time hook recomputes each
anchor and warns per-file which one drifted.

**Tier 2 — structural records.** A claim about arrangement has no file to hash. Its anchor is its
*placement* plus a **shape fingerprint** — the child-name set of its subtree (names, not contents).
This is deliberately **content-blind**, and that is *correct, not a gap*: editing a file's internals
under a "we split core/api" record does not make the split false, so a content signal there would be a
false-positive storm (exactly the whole-directory hash the design rejected). A structural claim is
threatened only by a structural change, and the shape fingerprint catches precisely that — including a
manual reorg done outside the method.

**Content invariants are not a third mechanism.** "core stays pure" is a record that *claims about
file content*, so it takes a Tier-1 `anchors:` list on the specific files that carry the rule. When
one changes, the hook flags "re-verify", the reader opens the rule and checks the change against it —
**detection reuses the hash we already have.** The only thing `anchors:` can't do is decide
*automatically* whether the change actually broke the rule; that verdict needs code re-analysis, so
automatic **enforcement** is the one optional extra — a separate, **opt-in** fitness-function emitting
capsa `X-` findings, never built into the passive layer. One honest caveat: an invariant spanning a
whole subtree, anchored to every file, regresses to the noisy whole-directory hash the design
rejected — so anchor a broad invariant to the few files that embody it, or accept detection-only, or
wait for the opt-in scanner.

**The one active mechanism (read side).** A single hook, firing when the agent reads a record:
recompute the anchor for that record's tier (content hash / shape fingerprint), compare to the stored
value, and if it differs inject an **advisory** note — *"the source this record describes changed since
it was written; re-verify"* — into the read result. It **never blocks and never auto-invalidates**
(a change is possible-staleness, not proven falsehood). Because it re-reads the *actual* file/tree, it
catches drift regardless of whether the edit went through aims or was done by hand or another tool.

**The write side of the anchor.** The hash / shape is stamped by a small, explicit, idempotent command
the method calls *at the moment it files a record* — e.g. `aims anchor <record> <path>…` — **not** a
hook. The agent never computes a hash by hand (unreliable); the command does it. Nothing runs in the
background.

Net: **aims = the Balash method + a capsa-format knowledge tree + exactly one read-time staleness
hook + one write-time `anchor` command.** No memory subsystem, no consolidation, no doctor.

## The cut (what aims' machinery loses)

- **Remove the memory-tree subsystem** (`mark`, `consolidate`, `find-dirty`, `lint`, `doctor`,
  `check-refs`, `classify-inbox`, `new-node`, `readme-sync`, `_lib`) — the heaviest, most speculative
  piece, and one that partly reversed itself. capsa's placement-addressed, one-fact-per-file grammar
  needs none of it: relevance is structural (a tree walk), not computed; there is no mutable store to
  keep coherent.
- **Remove the memory hooks** (`post-edit-marker`, the memory half of `stop-consolidate`).
- **Keep** only: a light **session-start surfacing** (walk from the working node, surface in-scope
  records) and the single **read-time staleness** hook above.

## What is kept from Balash

The entire design method, unchanged: discovery + design objective, the feasibility gate, ownership/
encapsulation, the subtractive pass, the review panel, and `references/design-principles.md`. What
changes is only *where the knowledge it produces lands* (a capsa tree) and *that it now persists across
sessions and years*. Guide→Worker stays available but optional (cost lever only).

## capsa adoption — settled: capsa lives in aims

capsa is a format, and aims is a *consumer* of it (capsa explicitly permits a consumer to add
mechanism on top — the read-time hook — and to enforce more via `X-` findings, without forking the
format). **Decision: capsa is developed inside aims from here on** (`aims/vendor/capsa/`), and the
original standalone repository is retired — there is no external upstream to sync from, so no
"external dependency vs. vendored subset" tension and no migration path to maintain. Editing the
grammar is done here, as a reviewed design act that bumps the version.

The one invariant that keeps this safe: **an aims capsule stays a conforming capsa capsule.** The
`anchors:`/`shape:` fields remain ordinary unknown keys (which capsa preserves and ignores), so the
format stays readable by any capsa tool and the grammar never has to learn aims' additions.

Record-type mapping (initial): `decisions/` (ADRs), `requirements/`, `insights/` (dev · design).
Anchors ride as an `anchors:` block (tier 1) and a `shape:` fingerprint (tier 2); provenance uses
capsa's `anchored_to` / `learned_from` link vocabulary. Placement carries scope; nothing declares its
own scope.

## Verification (how we will know the cut was safe)

1. Rebuild on this basis and confirm ADRs / requirements / insights are produced **from in-context
   method instruction alone**, with the machinery gone.
2. The read-time hook demonstrably fires on (a) a file-content edit under a tier-1 record and (b) a
   manual directory reorg under a tier-2 record — including edits made *outside* the method — and stays
   silent on a content edit under a tier-2 record (no false-positive storm).
3. A content-invariant record anchored to its files is flagged by the same hook when one changes
   (detection needs no new mechanism); automatic enforcement stays absent from the passive layer, and
   a sample opt-in fitness-function composes via `X-` findings without touching the format.

## Prior evidence this rests on

- `experiments/evolving-task-balash-vs-clean/` — the Balash *method* beat a no-method agent on final
  architecture across three evolving domains. Establishes the method is worth keeping.
- The Guide-vs-Worker experiment — a single agent running the method reached the same design decisions
  as the split at ~0.6× cost. Establishes the split is a cost lever, not a design-quality mechanism —
  hence "optional, off by default."
