# Balash Product Knowledge

Durable, cross-session product knowledge — the Guide's decision log. This file is **append-first**:
when a fact or decision is superseded, say so next to it (what changed, and ideally when/why) rather
than deleting it, so this file reads like a history of the product's understanding, not a mutable
scratchpad. It carries no loop-control flags (those live in `.balash/state.md`) and no single
objective's content (Kind/Exit criteria/handoff/result/review live in `.balash/objectives/`).

## Product purpose

<!-- One or two sentences. -->

## Core scenarios

<!-- Only scenarios that materially shape engineering decisions. -->

## Product knowledge

### Grounded product facts

<!-- Fact — source: request | repository | user answer. -->

### Open product decisions

<!-- Must be empty of material items before delegation. -->

### Technical freedoms

<!-- Choices the Worker may make without asking the user. -->

## Product forces

### Likely change axes

<!-- Expected independent variation, with a reason/evidence. -->

### Invariants

<!-- Rules that must remain true across implementations. -->

### Constraints

<!-- Real constraints, not generic quality wishes. Record "none identified — <why>" as a deliberate
     entry rather than leaving this empty: an empty section is indistinguishable from "not checked
     yet", and this file is the record that it *was* checked. -->

### Foundational dependencies (day-zero)

<!-- The very-infrastructural substrate everything is built on (numpy, scipy, cv2 ...): replacing it
     would rewrite everything. Decided up front (by the Guide unless it materially affects the
     product), kept minimal, extended only rarely. These + the framework's own domain types are the
     ONLY things allowed to cross a public seam (design-principles §7). Heavy but replaceable deps
     (model / data / augmentation libraries) are NOT listed here — they're confined behind a boundary
     and chosen later. Record "none — <why>" as a deliberate entry rather than leaving this empty. -->

### Explicit non-goals

<!-- Things we deliberately do not design for yet. -->

## Durable decisions

<!-- Decision — reason — evidence/trade-off — the objective (file under .balash/objectives/) it was
     made under, if any. Append; annotate rather than delete when a later decision supersedes one. -->

## Open Guide TODO

- [ ]
