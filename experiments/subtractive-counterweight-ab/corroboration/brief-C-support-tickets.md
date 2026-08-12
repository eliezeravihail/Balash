# The design a Worker returned (run the subtractive pass on it)

## Concrete usage scenario (the product — this is the whole spec you were given)

A customer opens a support ticket describing a problem. Staff pick up open tickets and reply; a ticket
moves through **open → in-progress → resolved** as staff work it. A customer may have several tickets
open at once, and staff may add more than one reply to a ticket before it is resolved.

## The elements the Worker introduced (decide KEEP or CUT for each)

1. `openTicket(customer, text)` — create a new ticket in the `open` state.
2. `respond(ticketId, staff, text)` — a staff reply; moves an `open` ticket to `in-progress`.
3. `resolve(ticketId)` — mark a ticket `resolved`.
4. internal `ticketsById` + a state machine enforcing the open→in-progress→resolved transitions.
5. internal `assignNext(staff)` — hand the staff member the oldest unresolved ticket.
6. `ticketsFor(customer)` — returns the customer's tickets, each with its current state and the replies
   staff have added so far.
7. `class TicketId` — a class wrapping the ticket's string id, constructed only through a `Symbol`-guarded
   factory so callers can't build one directly; no methods beyond returning the string.
8. `normalizeText(text)` — validates that `text` is a non-empty string and returns it unchanged.

## Your task

Run the **subtractive pass** exactly as the method file you were given defines it. For **each** of the 8
elements, decide **KEEP** or **CUT**, and give the one-line reason your pass produces (the present force
that requires it, or why its removal costs nothing real). Output only a table:

| # | element | KEEP / CUT | the force (or why it's ceremony) |

Then one final line: `CUT LIST: <comma-separated element numbers you would remove>`.

Judge strictly by the method file's subtractive-pass definition — not by your own taste. The scenario
above is the entire product specification you were given; there is no additional requirements document.
