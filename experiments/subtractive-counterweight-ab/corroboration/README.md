# Corroboration — does the counterweight generalize past the one waitlist case?

The original A/B validated the counterweight on a single domain (a room-booking **waitlist**), and its
honest limit was: *the affordance was deliberately clear-cut.* This run repeats the same blind protocol
on **two new domains** with different affordance types, need **unstated** (the real test condition),
n = 2 per arm.

- **Case B — inventory reservation** ([`brief-B-inventory-reservation.md`](brief-B-inventory-reservation.md)):
  a cart reserves stock that expires in 15 min. Discriminating element `#6 reservationsFor(shopper)` —
  a shopper needs to see what they hold and *when it lapses*.
- **Case C — support tickets** ([`brief-C-support-tickets.md`](brief-C-support-tickets.md)): a customer
  opens tickets that move open→in-progress→resolved. Discriminating element `#6 ticketsFor(customer)` —
  a customer needs to see each ticket's status and the replies.

Both briefs also carry the same two **ceremony controls** (a `Symbol`-guarded field-bag class; a no-op
`normalize*`) and one **speculative** element (an unrequested auto-assignment/waitlist handoff) that a
working pass must still cut.

## Result across all three domains (discriminating element `#6`, need unstated)

| domain | affordance `#6` | OLD | NEW | ceremony #7/#8 | speculative #5 |
|---|---|---|---|---|---|
| waitlist (original) | see the queue | **CUT 2/2** | KEEP 2/2 | CUT both arms | — |
| **B — inventory** | see reservation + expiry | **CUT 2/2** | KEEP 2/2 | CUT both arms | CUT both arms |
| **C — support tickets** | see ticket status + replies | KEEP 2/2 | KEEP 2/2 | CUT both arms | CUT both arms |

## Reading — a stronger, more honest result than "it flips every case"

1. **NEW never cut a needed affordance: 6/6 KEEP across all three domains** — and never degraded into
   "keep everything," cutting the two ceremony items and the speculative handoff every single time. The
   counterweight is **safe and discriminating**, not a blanket "retain."
2. **The counterweight bites where the miss actually happens.** Where the affordance is easy to overlook
   (a queue you wait in; a reservation quietly counting down), OLD cut it **2/2** and NEW rescued it. It
   is the exact recurring A2 failure, reproduced in a second domain.
3. **Case C is a NULL, and that is the honest boundary.** When the affordance is salient enough that even
   the invariant-only pass rationalizes it as a "read boundary" ("without a read path the tracked state
   is unobservable"), OLD already keeps it — so the counterweight is **redundant but harmless** there.

**The value is variance removal.** Without the counterweight, whether a needed affordance survives
depends on whether the reviewer happens to talk itself into calling it a "boundary" — it did for tickets,
it did **not** for the waitlist or the reservation. The counterweight makes the KEEP **reliable** instead
of luck-of-the-framing, at zero cost to the pass's ability to cut real ceremony.

## Limit that remains

All three affordances are **read/inspect** capabilities (the failure class the counterweight names).
This corroborates generalization *across domains*, not across every *kind* of affordance (e.g. an
undo/cancel or a notification). And it closes the blatant miss, not every borderline judgment call —
the counterweight still asks a question ("what does the scenario imply?") whose answer a reviewer can
get wrong at the margin.

## Method-run provenance

Method text pinned at commit `731ea42` (the counterweight as shipped). One agent in the first launch was
handed a mistyped method path (`subtractive-*.md` instead of `review-*.md`); **every** such agent
**refused to proceed and reported the missing file rather than substitute its own judgment** — an
incidental confirmation that the arms were genuinely blind to anything but the method file handed them.
The run was relaunched with the correct path; the results above are that clean run.
