# Pilot #7 — Balash vs a clean agent on three evolving products (external run)

**Provenance.** This pilot was run by **Codex** (a separate agent/operator), not by this repository's
maintainers or in the sessions that produced pilots #1–#4. The Balash version under test was **pinned to
commit `8baab0bb03f1bb3c4a9eb53c8904c1d2c6a72896`**. The materials here are the experiment **protocol**
([`PROTOCOL.md`](PROTOCOL.md)) and the operator's **results** ([`RESULTS.md`](RESULTS.md)), both as
authored (Hebrew). Following the `pilot5-connect-four-codex` convention, the **raw run implementations
are not committed** — the load-bearing evidence is summarized below with `file:line`, and was
independently re-run before writing this note.

**A parallel, independent experiment — not a re-run of the same one.** The same three-domain
evolving-task *design* was also run separately under a **different harness and a different model** (Claude
/ Opus, both arms), with **blind judging completed** — recorded at
[`../evolving-task-balash-vs-clean/`](../evolving-task-balash-vs-clean). This folder is the **Codex** run
(older snapshot, **no blind judging**). Because the harness and model differ, the two are not a controlled
replication and their per-arm results are not directly comparable head-to-head; what matters is that both,
independently, surfaced the same three mechanisms — **convergent evidence across implementations**, with
the blind verdict living in the other folder.

## What it tested

Three *separate* evolving-product studies, each with two isolated arms — **Balash** (Guide→Worker,
asks a product question before building) vs **Direct** (one senior agent, builds directly). Each product
is revealed one stage at a time; neither arm sees the next stage. A hidden **Product Oracle** answers
clarifying questions word-for-word identically to whichever arm asks — so discovery value is measured
without handing Balash information Direct could not also obtain. Same model, tools, budget, and
environment per arm; **language was not dictated** and is treated as part of each method's own choice,
not a controlled variable.

| Experiment | Product | Evolution axis |
|---|---|---|
| **A — Inventory** | single-user stock tool → LAN web app → identity + roles | UI boundary, ownership of a stock rule, auth vs domain |
| **B — Annotation** | image-classification labeler → multi-project → detection → COCO | discovery under a thin card; project isolation; export formats |
| **C — Gateway** | Android app bridging `ntfy` ↔ a **regular** WhatsApp account | a **feasibility premise**, not a build task |

## The findings (three mechanisms, not one winner)

- **A — a late change exposed a durability boundary.** Mid-way through the web stage, the Balash arm
  found that a failed save after a mutation could split live state from disk, stopped, and introduced a
  *candidate → save → publish* commit path. Direct built faster and shipped a richer UI but self-decided
  more unstated behavior (edit/delete, username/password format policy, a `HOST=0.0.0.0` bind option).
- **B — a late change exposed persistence + ownership.** Balash kept work on disk and kept the three
  export formats (CSV, YOLO, COCO) as *separate projections* over one state — no speculative exporter
  framework. Direct shipped a faster UI that was **in-memory only** (work lost on refresh) and
  self-chose a normalized-CSV detection contract. Neither is a spec violation against Direct's own
  revealed contract — it is the cost of not asking.
- **C — a late change exposed a false foundational premise (strongest result).** Automating a *regular*
  WhatsApp account is prohibited by WhatsApp's terms. Balash asked one question (regular vs Business),
  and on "regular" **stopped** — did not design, build, or silently substitute another route. Direct
  built a `NotificationListenerService` POC that relies on that same unauthorized automation (no
  verified build). C0's success criterion — a *reasoned stop* — was set in advance.

## Independent verification (this repo's maintainer session)

The raw runs were provided and checked before curation:

- **Tests re-run and pass:** `inventory-balash` → 25/25, `annotation-balash` → 15/15 (`python -m unittest`).
- **The A durability finding is real in code**, not just documented: `inventory/application.py:46-53`
  rebuilds a private `candidate`, then `_commit` calls `store.save(...)` **before** publishing
  `self._catalog = candidate`; `inventory/persistence.py:71-78` writes via tempfile + `os.fsync` +
  `os.replace` (atomic).
- **Loopback vs exposure:** `inventory-balash` `browser.py:24` pins `LOOPBACK_HOST: Final = "127.0.0.1"`;
  `inventory-direct` `server.js:360` reads `process.env.HOST ?? "127.0.0.1"` (loopback default, widenable).
- **B projections, not a framework:** `annotation-balash` has separate `csv_output.py`, `yolo_output.py`,
  `coco_output.py` with no shared `Exporter` base/ABC; `annotation-direct` has no `localStorage`/`fetch`/
  server → in-memory only.
- **C stop is genuine:** `gateway-balash-ntfy` contains **no code** — only `.balash/state.md`
  (cursor `blocked`, last review `invalidated`) and `.balash/knowledge.md` classifying the account choice
  as a foundational decision; `gateway-direct-ntfy` contains a real Kotlin `NotificationListenerService`
  POC, unbuilt (no Gradle in env).

Everything about **code and behavior** checked out. What could **not** be verified is the blind-judging
step — see status.

## Status & soundness

This is an **initial audit, not a final experimental result**, and the operator says so explicitly (see
[`RESULTS.md`](RESULTS.md#מדדי-השיפוט-שהופעלו-בפועל)):

- **No blind judging.** The protocol calls for two opposite-disposition design judges plus a black-box
  product judge; the results are a single, non-blind operator synthesis. The "design advantage" claim is
  therefore the operator's reading, not a blind verdict.
- **No raw test-count metric.** 25-vs-8 is **not** used as a quality measure — it is not comparable
  across different languages/frameworks/scopes. The judging was qualitative, against each arm's *revealed
  contract* (criteria enumerated in `RESULTS.md`).
- **n = 1 per product; no full cost/time measurement.**
- **Self-run.** Designed, executed, and reported by the Balash side; needs external replication.

**Next round (per the protocol and this note):** replicate each product several times; add real
cost/time logging; and actually run the two blind design judges + product judge, retaining their outputs.
