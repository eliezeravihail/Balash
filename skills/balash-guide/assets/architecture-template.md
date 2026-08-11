# Architecture

<!-- How our own code is structured — durable facts + rationale, not a discussion, not history, not a
     session-recovery log. Insights are integrated: a structural decision and its reason ("Y not chosen
     because Z") belong next to the decision. Keep it true. Where the structure is already enforced in
     code (a boundary that imports can't cross, a type, a test), POINT to it rather than restating it —
     a prose copy of enforced structure drifts and lies, which is the very failure this split exists to
     avoid. -->

## Boundaries & seams

<!-- Each seam: what it separates, and the payload that crosses it. Only foundational deps + the
     framework's domain types may cross (see BASE-DEPENDENCIES.md). Point to where it is enforced in
     code (module layout, a no-cross-import test). -->

## Key structural decisions

<!-- Decision + rationale, including rejected alternatives: "chose X; Y not chosen because Z." -->

## Invariants

<!-- Structural rules that must hold across implementations (e.g. "normalization has a single owner").
     Product-rule invariants belong in GOALS.md; structural ones here. Point to the test that guards
     each, where one exists. -->

## Likely change axes

<!-- Expected independent variation that justifies a seam — with the evidence/reason, not speculation. -->

## Confined dependencies

<!-- Heavy but replaceable deps and which boundary confines each. NOT foundational — those are in
     BASE-DEPENDENCIES.md. This is where a late-chosen model/data/augmentation library is recorded. -->
