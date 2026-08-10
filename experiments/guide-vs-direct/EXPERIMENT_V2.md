# Experiment v2 — Direct vs Guide

## Hypothesis

A user should only need to describe the product they want. A Guide that is optimized for discovering and maintaining the right engineering objective can translate that ordinary product description into better-directed coding work than giving the same product request directly to a coding agent.

The advantage, if it exists, should become clearest as the product evolves through requirements that were not revealed during the first version.

## Conditions

Only two conditions are used.

### Direct

The coding agent receives the user's product request verbatim and builds it normally.

### Balash Guide

The Guide receives the same request verbatim. It may ask only product questions that can change an engineering objective. It owns unresolved goal TODO, selects one objective at a time, delegates to a Worker, evaluates evidence, and repeats.

The user is not expected to know how to ask for clean architecture, choose patterns, identify extension points, or formulate engineering goals.

## Evolution sequence

1. Persistent CLI task manager for human team members.
2. AI agents become assignees and can execute tasks through a fake/test provider.
3. A second storage backend is added and selectable at startup.
4. Task prerequisites are added and become a lifecycle invariant.

Each stage is hidden until the preceding stage is complete. **The exact same evolving requirement is then shown to both conditions.**

## Primary observation

Not "which repository looks prettier after stage 1?"

Instead:

> Which development process produces a codebase that can absorb the later product changes locally, coherently, and without either large corrective refactors or speculative framework-building?

## Secondary observation

Measure the burden moved onto the user. A Guide that only succeeds by asking the user to make architectural decisions has failed the product goal even if its code is good.
