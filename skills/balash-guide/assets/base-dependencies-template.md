# Base Dependencies

<!-- The FOUNDATIONAL dependencies ONLY — the pervasive substrate the whole product stands on, whose
     replacement would rewrite essentially everything. The test is pervasiveness, not weight: if
     everything ends up standing on it, replacing it rewrites everything (numpy, scipy, cv2 are typical
     shapes of this). These, together with the framework's own domain types, are the ONLY things
     permitted to cross a public seam (references/design-principles.md §7). Decided at day zero, kept
     minimal, extended only rarely and deliberately.

     What does NOT belong here:
       * NOT the dependency manifest. Do not list every package — that only duplicates
         requirements.txt / package.json / go.mod, which is language-specific and blind to whether a
         dependency is foundational. The urge to "include everything" is the trap; this file is the
         small, curated base, nothing more.
       * NOT confined, replaceable dependencies (a model framework, a data loader, an augmentation
         library). Those live behind a boundary and are chosen late — record them in ARCHITECTURE.md
         as what sits behind which boundary, not here.

     Language-agnostic and standalone: assume no stack, point to no manifest. Facts + rationale, kept
     true. If the choice was not load-bearing, one line is enough. -->

## Foundational substrate

<!-- Each entry: the dependency — what stands on it / why it is foundational (pervasive, crosses seams)
     — and, only when the choice was load-bearing, why this one over the alternative ("Y not chosen
     because Z"). -->

-
