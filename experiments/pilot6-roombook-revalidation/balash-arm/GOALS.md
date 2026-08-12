# Goals

## Primary goal

RoomBook is a meeting-room booking core: it accepts bookings for named rooms, rejects any booking
that would overlap an existing booking in the same room, and reports each room's schedule. It is a
library core (in-process API), not a service or UI.

## Use scenarios

- An organizer books room "A" for [60, 120) and receives a booking id. A second organizer tries
  room "A" for [90, 150) and is rejected (overlap). A third books room "A" for [120, 180) and
  succeeds — intervals are half-open, so [60,120) and [120,180) do not conflict. `schedule("A")`
  returns both surviving bookings ordered by start.
- Bookings in different rooms never conflict with each other, regardless of times.

- A team books a recurring slot: room "A", [60, 120), weekly stand-in as
  `{everyMinutes: 1440, count: 3}` → occurrences [60,120), [1500,1560), [2940,3000), all booked,
  each visible in `schedule("A")` as an ordinary booking with its own id. If ANY occurrence would
  conflict, nothing at all is booked (all-or-nothing) and the rejection says so.
- An organizer cancels a booking by id; the slot is immediately free and a new booking over the
  same interval succeeds.
- A requester whose booking request for room "A" [0,30) conflicts joins the waitlist for that
  room+interval instead. When the blocking booking is canceled, the entry is automatically
  promoted: a real booking for [0,30) with that requester appears in `schedule("A")`, and the
  entry leaves the queue. If the waitlist also held a later, non-overlapping entry [30,60) that
  now fits, it is promoted too (see Decisions).

- A team declares room "A" holds 4 people. A booking of "A" with 5 attendee ids is rejected
  (capacity). Person "p1" attends a booking in room "A" [10,20); a booking in room "B" [15,25)
  listing "p1" is rejected — a person cannot be in two overlapping meetings, regardless of room.
  Canceling p1's booking in "A" frees p1, and a queued entry in "B" whose only obstacle was p1's
  conflict is automatically promoted.

## Non-goals

Deliberately excluded as of stage 4: persistence (state is in-memory only), modification of
existing bookings, series-level operations (occurrences are ordinary independent bookings), a
room registry as a booking gate (rooms still need no prior creation to book or join; declaring a
capacity is an optional per-room attribute, narrowed from the earlier blanket non-goal by the
stage-4 capacity requirement), a person registry (person ids are opaque labels; no person needs
prior creation), retroactive rule enforcement (all rules are creation gates: lowering a capacity
or booking a person never evicts or invalidates existing bookings), concurrency control,
calendar/date semantics beyond integer minutes, users/authentication (organizer and requester
are opaque labels), leaving or inspecting the waitlist, waitlist priority over direct booking,
and any notification mechanism (promotion is observed via `schedule()`).

## Decisions & insights

- **Time is integer minutes; intervals are half-open [start, end).** [10,20) and [20,30) do NOT
  conflict. Set by the user in the product request.
- **Conflict rule: a booking is rejected iff it overlaps an existing booking in the SAME room.**
  Rooms are fully independent. Set by the user.
- **`schedule(room)` returns that room's bookings ordered by start.** Within one room this ordering
  is total: two bookings in the same room can never share a start (equal starts with positive
  length always overlap, so the second would have been rejected).
- **An interval must satisfy `start < end`, both integers; anything else is rejected as invalid
  input.** Not user-stated, but a zero-length or inverted booking has no meaning in a booking core;
  rejection is the only reasonable behavior. Recorded here so it is a deliberate rule, not an
  accident of implementation.
- **Recurring series (stage 2): `bookRecurring(room, start, end, organizer, {everyMinutes, count})`
  creates `count` occurrences, occurrence i at [start + i·everyMinutes, end + i·everyMinutes), and
  is ALL-OR-NOTHING: if ANY occurrence conflicts, the whole series is rejected and nothing is
  booked.** Set by the user. "Any occurrence conflicts" includes occurrences of the series
  conflicting with *each other* (e.g. a stride shorter than the duration): such a series is
  unbookable — this follows from composing the stated rule, not a new rule.
- **Malformed recurrence parameters are invalid input:** `everyMinutes` and `count` must be
  integers with `everyMinutes >= 1` and `count >= 1`. Same principle as the interval rule:
  meaningless input (an empty series, a zero or backward stride) has only one reasonable
  treatment. A `count` of 1 is a valid degenerate series equivalent to a single `book`.
- **Cancellation (stage 2) is at booking granularity: `cancel(bookingId)` removes exactly that
  booking; the freed slot is immediately rebookable.** Set by the user. A recurring occurrence is
  canceled individually like any other booking — no series identity survives creation (the spec
  defines no series operations; see Non-goals).
- **`cancel` of an id with no live booking (never issued, or already canceled) is a distinguishable
  error, not a silent no-op.** The user delegated this choice ("choose as the engineer, record it").
  Reason: ids originate only from this in-process instance, so a dead id means a caller bug or a
  double-cancel; silence would hide both. Also consistent with the seam's rejection philosophy
  (ARCHITECTURE.md §4: the throw channel is the one callers cannot silently ignore).
- **Waitlist (stage 3): a requester whose booking request conflicts may instead join a waitlist
  for that exact room+interval.** Set by the user. Joining is the requester's explicit choice;
  an entry records room, interval, and requester (opaque label, like organizer).
- **Joining the waitlist for an interval that does NOT currently conflict is rejected as an
  error.** Derived from the spec's own conditional ("IF a booking request conflicts, the requester
  MAY INSTEAD join"): joining is defined only as the alternative to a conflicting request — for a
  free interval the correct action is booking it. This also makes every entry born incompatible,
  which grounds the promotion invariant below. Interval validity rules apply to joins exactly as
  to bookings.
- **Promotion (stage 3): when a cancellation frees space, queued entries are examined in join
  order and EVERY entry that now fits is promoted — each promotion is a real, ordinary booking
  (visible in `schedule()`, cancelable), and the promoted entry leaves the queue.** The user
  delegated the several-entries-fit case ("read the spec's sentence as written; where it leaves
  room, choose and record"). Reason for promote-all-that-fit: each single promotion is exactly the
  spec's sentence — "the earliest-queued compatible entry is promoted" — applied again; stopping
  after one would leave a free slot beside a compatible waiting entry, which a direct `book` could
  then take ahead of the queue (an anomaly the spec nowhere asks for). The resulting product
  invariant: **between operations, no queued entry could ever be successfully booked** — entries
  are born incompatible (join requires conflict), only cancellation can make one compatible, and
  cancellation immediately promotes everything compatible. Promotion order is join order, so of
  two overlapping compatible entries the earlier-queued one wins and the later stays queued
  (promotion only adds bookings, so it can never make another entry newly compatible).
  *(Stage-4 generalization below: "fits" now means "passes every creation rule", the enabling
  events grow beyond cancellation, and join order is global.)*
- **Capacity (stage 4): a room's capacity is established by a declaration operation; a room with
  no declared capacity is unlimited.** The user delegated the mechanism ("yours to decide, record
  it"). Reasons: capacity is a property of a room, so it is declared per room; undeclared =
  unlimited is the only reading that keeps every recorded stage-1–3 behavior true (the shipped
  contract books rooms that were never declared); the no-registry non-goal is narrowed, not
  reversed — declaring is optional and only constrains. Supporting decisions (same delegation):
  capacity is an integer >= 0, else invalid input; re-declaring overwrites; capacity is a
  **creation-time gate only** — lowering it never evicts existing bookings (every rule in this
  product is a creation gate; eviction would need policy the spec does not define). A booking is
  rejected iff its attendee count exceeds the room's capacity at creation time; count == capacity
  is allowed.
- **Attendees (stage 4): the count and the list are ONE concept.** A booking carries a list of
  person ids; its attendee count IS the list's length — capacity checks the length, the overlap
  rule checks the ids. The user delegated this ("yours to decide, record it"). Reasons: the
  spec's two sentences describe one datum from two sides; a separate unnamed-headcount field
  would invent a guests concept no scenario asks for, and two fields create count-vs-list
  disagreement states needing rules the spec never defines. Supporting decisions: person ids are
  opaque strings (like room/organizer/requester; no person registry); the list is **optional at
  creation, defaulting to empty** (an empty list is valid — this keeps every existing recorded
  call correct); a list containing duplicate ids is invalid input (a person cannot attend twice;
  a duplicate is a caller bug, and this seam signals caller bugs); the organizer is NOT
  implicitly an attendee (the spec defines no relation between the opaque organizer label and
  person ids — only listed ids are checked).
- **Person-overlap rule (stage 4): a booking is rejected if ANY of its attendees already has an
  overlapping live booking in ANY room.** Set by the user — the product's first cross-room rule.
  Half-open interval semantics apply as everywhere (touching meetings share an attendee legally).
  It is a creation gate on every creating path: `book`, every occurrence of a series (the series'
  all-or-nothing covers it — one attendee-conflicted occurrence rejects the whole series), and
  promotion.
- **Quiescence generalized (stage 4): "fits" means passes EVERY creation rule** (interval free in
  the room, capacity, person-overlap). Consequences, all following from keeping the stage-3
  invariant true rather than silently weakening it: an entry stays queued if promotion is
  rejected for ANY reason; the **enabling events** — operations after which a queued entry may
  have become bookable — are now (1) any cancellation, which can free an interval in its own room
  AND free a person for entries in ANY room, and (2) a capacity increase for a room. Each
  enabling event immediately triggers promotion of everything that now fits. **Join order is
  global** (one instance-wide join sequence, not per-room): promotion can now span rooms, and
  "the earliest-queued compatible entry" needs one answer when entries in different rooms compete
  for the same person's time. Waitlist entries therefore carry their attendee list (promotion
  mints real bookings, which need it); the join gate itself is unchanged — a join still requires
  a present interval conflict, and capacity/person-overlap are NOT join gates, because both can
  change before promotion (capacity can be raised; the blocking person's meeting can be
  canceled) — rejecting eagerly would refuse entries that may legitimately promote later.
