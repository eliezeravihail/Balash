# A/B — the subtractive-pass **counterweight** (fixes pilot #6's recurring A2 miss)

**What prompted it.** Across pilots #4 and #6 the method reliably closed product *bugs* but repeatedly
**cut a real affordance** — "a user cannot see who is queued" (`waitlistFor`). A wrong output has a
failing test to catch it; a missing affordance has none, so the **subtractive pass** — which deletes
any element no *invariant* forces — waved it out as ceremony. The fix (this change): give the pass a
**counterweight** — *a force is not only a rule.* A capability the concrete usage scenario **implies a
user needs** (a read/inspect/feedback affordance) is itself a present force, even though it owns no
invariant, and must not be cut for tidiness. The pass now runs **both ways** against one yardstick, the
usage scenario.

## Method

Same returned design handed to blind agents running **only the subtractive pass**
([`design-brief-*.md`](design-brief-test-need-unstated.md)). It lists 8 elements — 5 genuine
rule-owners, one **read affordance** `waitlistFor` (the discriminator), and 2 real ceremony items (a
`Symbol`-guarded field-bag class; a no-op `normalizeRequester`) as controls that a working pass must
still cut. The only variable is the method text:

- **OLD** — the subtractive pass without the counterweight ([`subtractive-old.md`](subtractive-old.md)).
- **NEW** — with the counterweight ([`subtractive-new.md`](subtractive-new.md)).

Two briefs: a **control** where the scenario *states* the view-the-queue need, and the **real test**
where — like pilot #4/#6's actual spec — the need is **unstated** and must be *inferred* from "the
product queues people." n = 2 per arm on the test (per the ≥2 replication convention).

## Result — clean separation on the real test

| brief | arm | `waitlistFor` (#6) | ceremony (#7, #8) |
|---|---|---|---|
| **Test** (need *unstated*) | OLD | ❌ **CUT, 2/2** — "the scenario requires joining and auto-promotion, never viewing the queue… rent paid to nobody" | CUT ✓ |
| **Test** (need *unstated*) | NEW | ✅ **KEPT, 2/2** — "the product queues people, so someone must see who is queued… kept by the counterweight, not tidiness" | CUT ✓ |
| **Control** (need *stated*) | OLD & NEW | KEPT, 4/4 | CUT ✓ |

**The counterweight causes the fix, and only where it should.** With the need unstated, OLD reproduces
the exact A2 miss (cuts the affordance 2/2); NEW keeps it 2/2 — while **both** arms still cut the two
genuine ceremony items, so the counterweight discriminates rather than turning the pass into
"keep everything." The control (need stated) is a NULL — both arms keep it — confirming the change acts
specifically on the **inference** step, the one that failed in the pilots.

## Honest limit

The affordance in this first brief is deliberately clear-cut (a queue people wait in). The counterweight
asks a judgment question ("what does the scenario imply?"), and a borderline affordance could still be
argued either way — this closes the blatant miss, not every possible one. n = 2 per arm; directional-plus,
not a large sample.

**Corroborated on two further domains** ([`corroboration/`](corroboration)): inventory-reservation and
support-tickets, same blind protocol, need unstated. Headline — across all three domains NEW keeps the
affordance **6/6** and never over-keeps (it still cuts the ceremony and the speculative element every
time); OLD cuts it where the affordance is easy to miss (waitlist, reservation-expiry) and keeps it only
where it is salient enough to read as a "boundary" already (tickets — a NULL). The counterweight's value
is **variance removal**: it makes a needed affordance *reliably* survive instead of depending on whether
the reviewer happens to rationalize a boundary. Remaining limit: all three are read/inspect affordances
(the class the counterweight names), so this generalizes across domains, not across every kind of
affordance.

## Files
- [`subtractive-old.md`](subtractive-old.md) / [`subtractive-new.md`](subtractive-new.md) — the two method-text variants (the `review.md` subtractive-pass section).
- [`design-brief-test-need-unstated.md`](design-brief-test-need-unstated.md) — the real test (need inferred).
- [`design-brief-control-need-stated.md`](design-brief-control-need-stated.md) — the control (need stated → NULL).
