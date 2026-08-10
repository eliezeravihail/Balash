# Balash Guide State

This file stores durable engineering direction. Keep it short. Do not use it as a transcript or worker task log.

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

<!-- Real constraints, not generic quality wishes. -->

### Explicit non-goals

<!-- Things we deliberately do not design for yet. -->

## Durable decisions

<!-- Decision — reason — evidence/trade-off. -->

## Open Guide TODO

- [ ]

## Mode

<!-- auto | stepped. `auto` = the loop runs end to end, pausing only for open product decisions and the
     next product change. `stepped` = stop at every phase boundary (plan / build / review) and advance
     only on an explicit command; a returning Worker parks at executed:awaiting-review, it does NOT
     auto-advance. See references/modes.md. Default when unset: auto. -->

auto

## Loop cursor

<!-- Where the loop is parked right now, so any turn (a returning Worker, or a "balash next" / phase
     command from the human) can resume from exactly here. One line, kept current:
     needs-plan | planned:awaiting-build <objective> | awaiting-worker <objective> |
     executed:awaiting-review <objective> | reviewed:awaiting-decision <objective> |
     ready-to-choose-next | awaiting-human <named open decision> -->

## Current objective

**Kind:** <!-- design | implementation | refactoring — sets the review lens. -->

**Objective:**

**Why now:**

**Exit criteria:**
- [ ]

**Preserve:**
-

**Do not optimize for:**
-

## Last evaluated result

<!-- met | partially_met | invalidated | blocked, with brief evidence. -->
