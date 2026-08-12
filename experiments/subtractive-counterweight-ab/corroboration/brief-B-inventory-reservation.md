# The design a Worker returned (run the subtractive pass on it)

## Concrete usage scenario (the product — this is the whole spec you were given)

A shopper adds an item to their cart, which **reserves one unit of stock** for them. If they do not
check out within 15 minutes, the reservation **expires** and the unit is released back to available
stock. Several shoppers may compete for the last unit of a popular item.

## The elements the Worker introduced (decide KEEP or CUT for each)

1. `reserve(sku, shopper)` — reserve one unit if one is available; the core add-to-cart action.
2. `checkout(cart)` — convert the shopper's reservations into a completed sale.
3. internal `reservationsBySku: Map<sku, {shopper, expiresAt}[]>` — the reservation store.
4. internal `sweepExpired(now)` — release reservations whose `expiresAt` has passed, back to stock.
5. `reserveNextIfWaiting(sku)` — when a unit frees, give it to the earliest shopper still trying.
6. `reservationsFor(shopper)` — returns the shopper's currently-held reservations, each with the sku and
   the time it will expire.
7. `class ReservationToken` — a class wrapping `{sku, shopper, expiresAt}`, constructed only through a
   `Symbol`-guarded factory so callers can't build one directly; no methods beyond field access.
8. `normalizeSku(sku)` — validates that `sku` is a non-empty string and returns it unchanged.

## Your task

Run the **subtractive pass** exactly as the method file you were given defines it. For **each** of the 8
elements, decide **KEEP** or **CUT**, and give the one-line reason your pass produces (the present force
that requires it, or why its removal costs nothing real). Output only a table:

| # | element | KEEP / CUT | the force (or why it's ceremony) |

Then one final line: `CUT LIST: <comma-separated element numbers you would remove>`.

Judge strictly by the method file's subtractive-pass definition — not by your own taste. The scenario
above is the entire product specification you were given; there is no additional requirements document.
