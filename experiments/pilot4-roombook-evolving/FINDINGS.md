# Pilot #4 — RoomBook: an evolving product, isolated operators, separate verdicts

This is the experiment the earlier pilots pointed to. It is the first pilot where the two arms
**split**: design-first won the design and lost the product. That split is the result.

## What makes this pilot different (it fixes the three biggest holes)

- **Isolated operators.** The two arms were built by two *separate agent contexts* that never saw
  each other's code or reasoning. The same operator did not run both arms — the main confound of
  pilots #1–#3.
- **An evolving product.** RoomBook was built over **four hidden stages**, each revealed only after
  the previous shipped, so neither arm could design for the future. This tests Balash's real claim —
  quality *under evolution* — not just initial design. (Only pilot #1 did this before.)
- **Three separate verdicts.** Design, product-quality, and edge-over-engineering were judged
  independently and never merged into one score.

Both arms ran on the **same strong model** (no weak-executor handicap this time). The Direct arm got a
competent-senior-engineer framing; the Balash arm additionally ran under the `balash-guide` skill.
Both finished all four stages green: **40/40 tests each** (Direct `909fd23`, Balash `8868a72`).

## The product

"RoomBook", an in-memory meeting-room booking core (pure Node, `node --test`), chosen because its hard
invariant *evolves*:

1. book + reject same-room overlaps.
2. all-or-nothing recurring series + cancel.
3. waitlist with auto-promotion on cancel.
4. room capacity **and a new cross-room invariant**: a person can't be in two overlapping meetings in
   *any* room.

Stage 4b was the designed stress: the same "overlap" truth applied to a *new entity* (a person), to
see whether each arm's design generalized it or bolted it on.

## Verdict 1 — DESIGN: Balash wins, clear, and robustly

Two blind judges with **opposite dispositions** (one minimalist/anti-abstraction, one
invariant-ownership/rigor), with **labels and order crossed** so neither position nor letter mapped to
a method, **both chose the Balash arm, "clear" margin.**

Why: at Stage 4 the Balash arm recognized the person-rule *falsifies* the "rooms are independent"
assumption every earlier stage was built on. It fused same-room and per-person conflict into **one
pairwise rule** — `Booking.conflictsWith`: *overlap AND (same room OR shared attendee)* — and **retired
the now-false per-room partition** (flattened its `_byRoom` map to a single list), keeping capacity (the
one genuinely per-room fact) separate. Every creation path funnels through one `_admit` gate; bookings
are frozen so admitted state can't be mutated out from under the rule. The Direct arm kept its per-room
`Map` and added person-conflict as a *separate* all-rooms scan (`_personConflict`) alongside the
room-time scan (`_conflicts`) — two co-owned notions of "conflict," plus an id→room index to compensate
for a partition the final rule outgrew.

This is the clearest instance yet of the effect under test: design-as-goal spent cognition on *"where
should this truth now live?"* — to the point of **deleting a structural assumption** — where the feature
framing bolted the new rule onto the old shape. Both opposite-disposition judges *also* independently
found the promotion gap below and credited Direct for it, so the design verdict is not a taste artifact.

## Verdict 2 — PRODUCT: Direct wins, clear (not overwhelming)

The **same minimalist discipline that won the design cost the Balash arm real product behavior.** A
blind product assessor, given the full spec and free to probe, chose the Direct arm. Verified defects in
the Balash arm (each reproduced by probe, not taken on the judge's word):

- **A1 — cross-room promotion is broken (real liveness defect).** `cancel` re-sweeps only the cancelled
  booking's *own room's* waitlist, but a cancel can free a *person*, which should promote a waitlist
  entry in *another* room. Reproduced: Alice booked in room A; Bob waitlisted in room B, blocked only by
  Alice; cancel the room-A booking → **Direct promotes Bob; Balash leaves room B empty forever.** The
  Balash arm *wrote the exact insight* ("conflict is no longer a room-local question") yet failed to
  propagate it to the promotion trigger — a design-completeness slip by a strong model.
- **A2 — no way to inspect the waitlist.** The subtractive pass explicitly cut a waitlist read surface
  ("no present force asks for it"). A real user cannot see who is queued. Direct ships `waitlistFor`.
- **A3 — recurring series accepts a negative stride and books backwards in time.** Reproduced:
  `bookSeries(room, org, 100, 160, -100, 3)` created bookings at `[100,160) [0,60) [-100,-40)`. Direct
  rejects a non-positive stride with a `RangeError`.

The Direct arm's product gaps were milder: `cancel` returns a bare boolean (no promotion feedback, where
Balash returns `{removed, promoted}`); `setCapacity(0)` is over-strictly rejected (Balash accepts a
valid zero-capacity room); cross-room promotion uses room-map order rather than strict global FIFO.

Net: on serving the user *correctly and completely*, Direct led. **A2 is the sharpest lesson** — the
subtractive discipline that produced the winning design is the *same* act that removed a real product
affordance. That is why design-quality and product-quality must be scored separately.

## Verdict 3 — EDGE OVER-ENGINEERING: Balash leaner this time (a reversal)

In pilots #1–#3 the recurring secondary finding was that *Balash* over-built at the seams. Here the
blind edge auditor found the **opposite**: the Balash arm was leaner-per-need, and the *Direct* arm
carried the ceremony —

- a `_normalizeAttendees` that **normalizes nothing** (validates and returns the input unchanged);
- a numeric-id + `_index` + `_nextId` layer made unnecessary by object identity;
- a `while` fixpoint loop around promotion whose justifying comment is **provably false** (a single
  sweep always suffices, since a promotion only ever adds bookings).

The Balash arm declined ids, indexes, a `Series`/`WaitlistEntry`/`Room` type, and a per-person index —
every construct pinned to a present rule. **This is the first pilot after adding the mandatory
subtractive pass to the skill, and the 3/3 edge-ceremony pattern did not recur.** One data point —
suggestive, not proven — but it points the right way.

## What this pilot establishes — and does not

**Establishes (more strongly than before):**
- Under operator isolation and product evolution, design-as-goal still produces the *deeper* design —
  here, re-homing an invariant and deleting a falsified structural assumption.
- **Winning design and losing product is real, and it happened.** The minimalist discipline that won
  design cut an affordance (A2) and shipped two real bugs (A1, A3). The verdicts must stay separate.
- The new subtractive pass plausibly addressed the edge over-engineering (n=1).

**Does NOT establish:**
- One orchestrator still authored both arms' stage prompts (from identical spec text; only the Balash
  arm additionally got the skill). Genuine independent human operators remain a stronger control.
- **Fidelity deviation:** within the Balash arm, one agent played *both* Guide and Worker; it did not
  delegate to a separate Worker sub-agent as pilots #1–#3 did. The design-first cognition was present,
  but the role-separation was not enacted.
- Evolving-product pilots are now two (this + #1); still small N.
- Neither arm is strictly better: the design arm is not the safer arm here — it shipped A1 and A3.

## Provenance
- Direct arm final commit `909fd23`; Balash arm final commit `8868a72`. Both 40/40 tests.
- `STAGES.md` — the staged spec (orchestrator copy). `balash-arm/HANDOFF.md` — the Guide's written
  objectives per stage.
- Anonymized snapshots given to the judges had method-giveaway files (HANDOFF, `.balash/`) stripped.
- `probe-direct.js`, `probe-balash.js`, `probe-a3.js` — reproduce A1, A3, capacity, and person-overlap.
