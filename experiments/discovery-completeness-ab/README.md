# A/B — the discovery **complement rule** (the root fix for the A2 affordance-omission class)

## The story this closes

Pilot #6 kept losing a real affordance — "a person on the waitlist cannot see or leave the queue." The
first fix put a **counterweight in the subtractive pass** (review) that tried to *infer* the missing
affordance from the built design. It validated for **read** affordances but
[**failed for mutation affordances**](../subtractive-counterweight-ab/mutation-affordance-limit) (cancel,
remove): inferring "the user probably needs to undo this" is indistinguishable from the "a future change
might want it" reasoning the subtractive pass exists to *reject*, so the counterweight never fired for
them.

That failure pointed at the real mistake: **fixing the problem downstream (review) instead of preventing
it upstream (discovery).** A needed affordance goes missing because it was never made an **explicit
requirement**. Good planning states it — "add *and* remove," "join, *see*, *and* leave" — and then the
design builds it and the subtractive pass never touches it. So the fix belongs in discovery, and it is
an **ask**, not a guess (Balash's founding principle). The counterweight was removed; this rule replaces
it.

## The rule (added to `references/discovery.md`)

> **Every action implies its complement.** A usage scenario as first stated runs forward only — "add,"
> "join," "book" — and omits the inverse action and the sight of the state the user was placed in. For
> the scenario as described these are *requirements*. For each action and each user-facing state, **ask**
> whether its complement is in scope; a confirmed complement is a stated requirement, a confirmed
> exclusion is a recorded non-goal — but it may not stay unstated.

## Method

Two forward-only product requests, stated the way a user would and **deliberately omitting** the
complements: a **shopping cart** ("add items and check out") and the **pilot-#6 waitlist** ("join when
full; auto-promote on cancel"). Blind agents run the discovery/plan phase using only the method file and
output REQUIREMENTS / OPEN QUESTIONS / NON-GOALS. Only the method text differs — `discovery-old.md`
(no rule) vs `discovery-new.md` (with it). n = 2 per arm. Scored: did discovery **surface the complement
as an explicit requirement or grounding question?**

## Result

**Cart** — complements: remove item, edit quantity, view cart before checkout.

| arm | remove | edit qty | view cart |
|---|---|---|---|
| OLD | 2/2 | 2/2 | ~1/2 (often only implied) |
| NEW | 2/2 | 2/2 | **2/2 explicit** |

**Waitlist (pilot #6)** — complements: leave/cancel entry, see your position, decline/undo the
auto-promoted booking, notification of promotion.

| arm | leave | see position | decline promotion | notify |
|---|---|---|---|---|
| OLD | 2/2 | **1/2** | 2/2 | 2/2 |
| NEW | 2/2 | **2/2** | 2/2 | 2/2 |

## Reading

1. **The layer is right.** Even *without* the rule, discovery already surfaces most complements as
   questions — the exact opposite of the subtractive pass, which *cut* them. Asking is what discovery
   does, so this is where the affordance is cheapest to save. Had pilot #6's Guide grounded the waitlist
   this way, "see / leave the queue" would have been a stated requirement and never droppable.
2. **It works for mutations — the case the counterweight could not.** The discovery arms surfaced
   *leave*, *cancel*, *decline* (all mutations) as naturally as the reads, because **asking** "can the
   user also cancel?" carries none of the anti-speculation reflex that made *inferring* it at review
   fail. This is the whole point: prevent the omission, don't reconstruct it later.
3. **The rule removes the residual variance.** OLD is good but inconsistent — it missed "see your
   position" in one waitlist run and rarely stated "view cart" outright. NEW made every complement
   explicit **2/2**, and the agents cited the rule as the driver. Same variance-removal value as the
   counterweight, now at the right layer and by asking rather than guessing.

## Honest limit

The rule leans on the Guide actually running discovery (a Guide who declares an affordance a non-goal
without asking still loses it — closer to pilot #6's real failure than the subtractive pass ever was).
It sharpens and makes reliable a tendency discovery already had; it is not a guarantee. n = 2 per arm,
two domains — directional-plus.
