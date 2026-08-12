# The design a Worker returned (run the subtractive pass on it)

## Concrete usage scenario (the product)

People book meeting rooms for time slots. When the room a person wants is already taken for that slot,
the person **joins a waitlist** for that room+slot. When a booking is cancelled and frees the slot, the
earliest-queued compatible person is **automatically promoted** into a real booking. Several people can
be queued for the same room, and a person who has joined a waitlist checks back later to find out
whether they got in or are still waiting.

## The elements the Worker introduced (decide KEEP or CUT for each)

1. `book(room, start, end, who)` — create a booking; rejects a same-room overlap.
2. `cancel(bookingId)` — remove a booking; triggers waitlist promotion.
3. `joinWaitlist(room, start, end, who)` — enqueue a waitlist entry when the slot currently conflicts.
4. internal `waitlistByRoom: Map<room, Entry[]>` — the queue store, in join order.
5. internal `promoteWaitlist(room)` — on cancel, promote the earliest compatible queued entry.
6. `waitlistFor(room)` — returns the list of entries currently queued for that room (who is waiting, and
   for which slot), in queue order.
7. `class WaitlistEntry` — a class wrapping `{room, start, end, who}`, constructed only through a
   `Symbol`-guarded factory so callers can't build one directly; it has no methods beyond field access.
8. `normalizeRequester(who)` — validates that `who` is a non-empty string and returns it unchanged.

## Your task

Run the **subtractive pass** exactly as the method file you were given defines it. For **each** of the 8
elements, decide **KEEP** or **CUT**, and give the one-line reason your pass produces (the present force
that requires it, or why its removal costs nothing real). Output only a table:

| # | element | KEEP / CUT | the force (or why it's ceremony) |

Then one final line: `CUT LIST: <comma-separated element numbers you would remove>`.

Judge strictly by the method file's subtractive-pass definition — not by your own taste.
