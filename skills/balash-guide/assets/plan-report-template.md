# Plan report — <objective in a few words>

<!-- The plan round's report: a concise executive summary for a technical manager, written at the END of
     a plan phase (after the objective and Worker handoff are drafted, before anything is built). Its job
     is to let a human see, in one read, what this round decided and why — the dependencies it rests on,
     the real deliberations, the decisions taken, and the architecture chosen — and to comment before the
     build begins.

     This is NOT one of the three durable design docs. GOALS.md / BASE-DEPENDENCIES.md / ARCHITECTURE.md
     stay clean facts + rationale, no history, no discussion. This report is the opposite by design: it
     is the ONE place the round's *deliberations* — the dilemmas, the roads not taken — are surfaced, for
     review. It is regenerated each plan round (the current round only); past rounds live in git history,
     committed alongside the code they planned. Keep it tight: substance over ceremony, not a form to
     fill in. Cite the design docs and file:line rather than restating them; a section with nothing real
     to say gets one honest line, not padding. -->

## Objective this round

<!-- What this round sets out to build, framed as the design/quality outcome (the feature is the
     constraint, not the goal), and **why now** — the evidence from the product/repo that makes it the
     priority. One short paragraph. -->

## Requirements it rests on

<!-- The product goals / grounded facts this objective serves — point into GOALS.md rather than
     restating. What must stay true regardless of how it's built. -->

## Dependencies

<!-- The foundational substrate this round stands on (point to BASE-DEPENDENCIES.md; note whether any of
     it was newly set this round and, if so, by which path — the user set it, or the user was asked and
     handed it back). Any confined/replaceable dependency this objective introduces, and the boundary it
     sits behind (that belongs in ARCHITECTURE.md — cite it). -->

## Deliberations

<!-- The heart of the report: the real dilemmas of this round. For each open question that mattered —
     what was asked, what the candidate answers were, which was chosen, and **why this one over that one**
     ("Y not chosen because Z"). Include the decisions handed to the user and their answer, and the
     judgment calls you made where a reasonable engineer could have gone the other way. If a tempting
     default was rejected (an auto-start, a preselected value, a carried-over choice), say so and why.
     This is where a reviewer catches a decision they disagree with before it is built. -->

## Decisions

<!-- The decisions this round settled, as facts: the product decisions resolved (now recorded in
     GOALS.md) and the architecture decisions taken (now in ARCHITECTURE.md). Cite where each landed. A
     decision here should trace to a deliberation above or to a stated requirement. -->

## Chosen architecture

<!-- The seams, boundaries, and interfaces this objective introduces or touches — the shape the Worker
     will build against. Point to ARCHITECTURE.md for the durable version; here, say what changed or was
     added this round and why it sits where it does. Name what is explicitly the Worker's to design
     (internal class breakdown, incidental libraries) versus what this round fixed. -->

## How we'll know it's right (exit criteria)

<!-- The exit criteria the build will be measured against — derived adversarially (the edge/break cases,
     the invariants a new interaction could violate, the falsifier for any lifecycle rule). This is the
     bar the review phase will hold the Worker's result to. -->

## Preserve / do not optimize for

<!-- What must not be damaged (behavior, decisions, constraints), and the tempting-but-irrelevant local
     goals the Worker should NOT chase. -->
