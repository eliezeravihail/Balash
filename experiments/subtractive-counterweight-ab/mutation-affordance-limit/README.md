# The limit that retired the counterweight — it does not fire for mutation affordances

The counterweight was validated for **read** affordances (see the queue, see your reservation, see
ticket status). This run tested **non-read (mutation) affordances** — actions the scenario implies a
user must be able to *do*, not just *see*: `removeItem` from a cart, `cancel` an appointment. Same blind
protocol, need unstated, n = 2 per arm.

## Result — NEW cuts the mutation affordance, exactly like OLD

| case | mutation affordance | OLD | NEW (with counterweight) |
|---|---|---|---|
| D — shopping cart | `removeItem` | CUT 2/2 | **CUT 2/2** |
| E — clinic booking | `cancel` | CUT 2/2 | **CUT 2/2** |

The counterweight did **not** rescue either. The smoking gun is in the NEW appointment runs: the same
agent **applied** the counterweight to a read affordance (`openSlots` — "someone must see which slots are
open") while **rejecting** the mutation (`cancel`) as *"'scarce slots might want release' is future-force
reasoning the pass rejects."*

## Why — and why it retired the whole approach

For a **read**, "the scenario shows state, so someone must see it" almost never collides with anything —
there is no "speculative getter" failure mode competing. For a **mutation**, the very same inference
("the scenario implies you'd want to undo") is *indistinguishable* from the "a future change might want
it" reasoning the subtractive pass exists to reject. So a review-time counterweight can only safely catch
reads; extending it to mutations would require it to override the pass's core anti-speculation job — the
opposite failure.

That is the signal that the counterweight was the wrong mechanism at the wrong layer: patching a missing
requirement *after* the design is built, by inference, instead of making it an explicit requirement
*before*. The fix moved upstream to discovery, where **asking** "can the user also cancel/remove?" is
natural and carries none of this collision — and there it works for mutations too
([`../../discovery-completeness-ab`](../../discovery-completeness-ab)). The counterweight was removed from
the skill; this folder is the evidence for why.
