# Vendored: capsa

This directory contains **capsa**, vendored verbatim and unmodified, under its own name.
aims uses capsa as its durable knowledge format; it is included here so aims stays
self-contained and so the grammar aims writes against is pinned and auditable.

- **Source:** https://github.com/eliezeravihail/capsa
- **Version pinned:** `0.8.0` (project format) inheriting core `0.6.0`
- **License:** MIT (see `LICENSE` in this directory) — © 2026 eliezeravihail
- **Files vendored:**
  - `core/PRINCIPLES.md` — the shared grammar (placement, addresses, links, tombstones,
    verification, manifest, versioning)
  - `project/SPEC.md` — the project format (record types: requirements, plans, decisions,
    discussions, issues, dependencies, releases, charter, insights, components, interfaces,
    milestones, lines)

capsa is a **passive file format** — data, not a program. Nothing in this directory runs.

## What aims uses, and what aims adds

aims does **not** use all of capsa. The subset aims relies on, and the two consumer-side
fields aims layers on top (permitted by capsa's "unknown frontmatter keys are preserved"
rule), are defined in [`../../docs/format-profile.md`](../../docs/format-profile.md). The
vendored spec is the source of truth for the grammar; the profile is the source of truth
for aims' use of it.

To update the vendored copy, replace the files from the pinned upstream tag and bump the
version above — never hand-edit them here.
