# The design a Worker returned (run the subtractive pass on it)

## Concrete usage scenario (the product — this is the whole spec you were given)

A shopper **adds items to a cart** while browsing, building the cart up over a session, and then
**checks out** to buy everything in it. Prices are summed at checkout. A shopper may put several
different items in the cart before checking out.

## The elements the Worker introduced (decide KEEP or CUT for each)

1. `addItem(cart, sku, qty)` — put an item (or more of it) into the cart.
2. `checkout(cart)` — sum the line prices and complete the purchase of everything in the cart.
3. internal `linesByCart: Map<cart, Line[]>` — the cart's line-item store.
4. `total(cart)` — compute the current sum of the cart's line prices.
5. `removeItem(cart, sku)` — take an item back out of the cart.
6. `suggestRelated(cart)` — internal helper that computes "customers also bought" suggestions for the cart.
7. `class CartLine` — a class wrapping `{sku, qty, unitPrice}`, constructed only through a `Symbol`-guarded
   factory so callers can't build one directly; no methods beyond field access.
8. `normalizeSku(sku)` — validates that `sku` is a non-empty string and returns it unchanged.

## Your task

Run the **subtractive pass** exactly as the method file you were given defines it. For **each** of the 8
elements, decide **KEEP** or **CUT**, and give the one-line reason your pass produces (the present force
that requires it, or why its removal costs nothing real). Output only a table:

| # | element | KEEP / CUT | the force (or why it's ceremony) |

Then one final line: `CUT LIST: <comma-separated element numbers you would remove>`.

Judge strictly by the method file's subtractive-pass definition — not by your own taste. The scenario
above is the entire product specification you were given; there is no additional requirements document.
