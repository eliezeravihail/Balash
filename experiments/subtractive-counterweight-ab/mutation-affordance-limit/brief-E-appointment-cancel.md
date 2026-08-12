# The design a Worker returned (run the subtractive pass on it)

## Concrete usage scenario (the product — this is the whole spec you were given)

A clinic offers appointment slots. A patient **books** an open slot; once booked, that slot is no longer
open to anyone else. Slots are scarce, so a slot that is taken cannot be double-booked. A patient may
hold several appointments across different days.

## The elements the Worker introduced (decide KEEP or CUT for each)

1. `book(slot, patient)` — book an open slot for a patient; refuses if the slot is already taken.
2. internal `slotsById` / `bookingsBySlot` — the store of which slot is held by whom.
3. `openSlots(day)` — list the slots still open on a given day.
4. `cancel(slot, patient)` — the patient gives up an appointment they hold, so the slot is open again.
5. `rebalanceLoad()` — internal helper that spreads a day's bookings evenly across the clinic's rooms.
6. `class SlotToken` — a class wrapping `{slotId, patient}`, constructed only through a `Symbol`-guarded
   factory so callers can't build one directly; no methods beyond field access.
7. `normalizePatientId(id)` — validates that `id` is a non-empty string and returns it unchanged.
8. internal `assertNoOverlap(slot)` — checks, on booking, that the slot is not already taken.

## Your task

Run the **subtractive pass** exactly as the method file you were given defines it. For **each** of the 8
elements, decide **KEEP** or **CUT**, and give the one-line reason your pass produces (the present force
that requires it, or why its removal costs nothing real). Output only a table:

| # | element | KEEP / CUT | the force (or why it's ceremony) |

Then one final line: `CUT LIST: <comma-separated element numbers you would remove>`.

Judge strictly by the method file's subtractive-pass definition — not by your own taste. The scenario
above is the entire product specification you were given; there is no additional requirements document.
