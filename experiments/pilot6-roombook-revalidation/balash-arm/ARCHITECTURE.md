# RoomBook — Architecture (Stage 4: room capacity and the person-overlap rule)

Buildable design for the booking core. Behavior contract and substrate are fixed by GOALS.md and
BASE-DEPENDENCIES.md; this document records the structure, the seam, each rule's single owner,
and the rationale for each structural choice, including rejected alternatives. Stage-4 revisions
are folded in place — every statement below describes the stage-4 design, not a diff against
stage 3. **Round status:** this stage's deliverable is the design; roombook.js currently carries
the live stage-3 behavior plus the stage-4 contracts and stubs, with every pending delta marked
`[STAGE-4 WIRING]`. The stage-3 test suite (T1–T43) runs green against it, byte-unmodified —
with one recorded collision that the implementation round must resolve by Guide decision (§7,
"the T43 surface pin").

Stage 4 introduces the product's first **cross-room rule** (person-overlap) and its first
**non-cancel enabling event** (a capacity raise). Both of the stage-3 judgments whose recorded
revisit conditions covered exactly this have fired — promotion's per-room isolation, and the
cancel-only promotion trigger — and are re-judged from scratch below (§3.7, §3.10, §6), their
old text replaced, not patched.

## 1. Module map

```
roombook.js        the entire booking core (single module)
  export createRoomBook()      factory -> { book, bookRecurring, schedule, cancel,
                                            joinWaitlist, setCapacity }
  export BookingConflictError  thrown by book()/bookRecurring() on same-room interval
                               overlap (for a series: ANY occurrence, incl. vs. a sibling
                               occurrence of the same series)
  export CapacityExceededError thrown by book()/bookRecurring() when the attendee count
                               exceeds the room's declared capacity
  export PersonConflictError   thrown by book()/bookRecurring() when an attendee already
                               has an overlapping live booking in ANOTHER room (a same-room
                               person overlap is always also a room overlap and reports as
                               BookingConflictError — §3.6)
  export InvalidIntervalError  thrown by book()/bookRecurring()/joinWaitlist() on a
                               malformed interval (one rule, one gate for all three)
  export InvalidRecurrenceError thrown by bookRecurring() on malformed {everyMinutes, count}
  export InvalidAttendeesError thrown by book()/bookRecurring()/joinWaitlist() on a
                               malformed attendee list (non-array, or duplicate ids)
  export InvalidCapacityError  thrown by setCapacity() on a malformed capacity value
  export UnknownBookingError   thrown by cancel() on an id with no live booking
  export NoConflictError       thrown by joinWaitlist() when the interval does not
                               currently conflict (the correct act is book(), not join)
package.json       {"type":"module"} + `node --test` script; no dependencies
```

Still one module, re-judged under the stage-4 forces: capacity and person-overlap are not new
concepts beside the booking store — they are two more *creation rules over the same store*,
enforced by the same commit authority every existing rule lives in (§3). A `capacity.js` or
`people.js` split would sever a rule from the one function that must enforce it, and the first
cross-room rule makes the strongest case yet for one module: the person-overlap scan needs the
*whole* store in view, which only the authority's closure has. Every candidate extraction still
has exactly one consumer. Revisit when a second consumer of any internal part exists.

## 2. The public seam

`createRoomBook()` returns a frozen object with exactly six functions:

- `book(room, start, end, organizer, attendees = []) -> string` (booking id) — signature grown
- `bookRecurring(room, start, end, organizer, {everyMinutes, count}, attendees = []) ->
  string[]` (one id per occurrence, in occurrence order) — signature grown
- `schedule(room) -> Booking[]` (ordered by start; `[]` for unknown/empty room) — unchanged
- `cancel(bookingId) -> undefined` — contract grown: promotion after removal is now GLOBAL
  (§3.7)
- `joinWaitlist(room, start, end, requester, attendees = []) -> undefined` — signature grown
- `setCapacity(room, capacity) -> undefined` — new (§3.9)

**Where the `attendees` parameter sits — forced, and recorded as such.** T1–T43 pass
byte-unmodified only if every existing positional argument keeps its position, so the attendee
list can only be an appended, optional, trailing parameter, defaulting to empty on all three
interval-taking operations. This is not a free choice being rationalized: backward compatibility
pins it, and it happens to also be the honest shape (the common case — no attendees — writes
nothing).

**Vocabulary crossing the seam (§7 of design-principles):** JavaScript built-ins only — strings,
integer numbers, arrays, one plain options object — plus one domain record shape defined by this
module, **still unchanged from stage 1**:

```
Booking { id: string, room: string, start: number, end: number, organizer: string }
```

**The Booking record does NOT grow an `attendees` field — a deliberate seam decision, not a
side effect.** Argued three ways: (1) *no consumer act exists* — no GOALS scenario reads an
attendee list back out; `schedule()`'s stated purpose is the room's timeline, and every
attendee-driven behavior (capacity and person rejections, promotion) is observable through the
operations themselves; (2) the record shape has been contract since stage 1, asserted at the
seam by the shipped suite (T38/T41 check `Object.keys` is exactly the five fields) — growing it
is a one-way door with nobody waiting on the other side; (3) attendee lists are the closest
thing this product has to personal data, and a seam should not start exporting it for free.
Consequence for internals: the store's records carry the list privately and `schedule()` mints
the public five-field record (§5). Rejected alternatives: a visible `attendees` field (no
consumer act); a *non-enumerable* `attendees` property (passes the `Object.keys` tests while
still leaking the list through direct property access — a seam leak wearing a test-passing
costume); a numeric `attendeeCount` field (re-invents the separate-headcount concept GOALS
explicitly merged away).

**Attendee lists are copied at the seam.** The caller keeps ownership of the array it passed;
mutating it after the call changes nothing inside (the validated copy is the truth — for a
booking it becomes the internal record's frozen list, for a waitlist entry it is what promotion
later hands the authority). This is the inbound sibling of the outbound fresh-array/frozen-record
defenses, and it becomes load-bearing exactly at stage 4 because for the first time a mutable
caller structure crosses *into* the store.

**Attendee ids are opaque** — like `room`, `organizer`, and `requester`: stored verbatim, never
interpreted, no person registry (GOALS non-goal). The list's *shape* is validated (array, no
duplicates — §3.1); its *elements* are not type-checked, for the same reason `organizer` is not:
validating stringness would be the first brick of a person registry the product refuses.
Duplicate detection uses SameValueZero (`Set` semantics). The organizer label is NOT implicitly
an attendee (GOALS-recorded): only listed ids are checked, even when the organizer label equals
some busy person id.

**`setCapacity` returns `undefined`** — the `cancel` precedent: success needs no payload.
Rejected: returning the previous capacity (a read operation in disguise; no consumer act reads
capacity — GOALS's observability for capacity is rejection behavior, exactly as the waitlist's
is promotion behavior); returning a "changed" boolean (duplicates the error channel). There is
deliberately **no capacity read operation**: undeclared rooms are contractually indistinguishable
from unlimited ones except through creation rejections, and the seam keeps it that way.

Nothing about the internal stores (the three Maps/arrays, their keys) is reachable or inferable
from the seam. `schedule()` still returns a fresh array per call of frozen five-field records;
ids are opaque, instance-unique, never reused; waitlist entries and capacities never appear in
any read operation.

**`joinWaitlist` returns `undefined`; `cancel` returns `undefined`** — both stage-3 decisions
stand unchanged, with their recorded rationale (no entry handle: no operation consumes one; no
promoted-ids return: `schedule()` is the observation channel). Stage 4 adds no force against
either.

**Why a factory returning closures, not a class** — unchanged from stages 1–3; stage 4 adds a
third per-instance store (capacities) and the closure confines it identically. Instance
isolation now also covers capacities: a `setCapacity` in one instance constrains nothing in
another (T-plan: instance-isolation cases).

## 3. The rules and their single owners (§9)

Stage 4 has **four creation rules** — input validity, room no-overlap, capacity, person
no-overlap — plus the all-or-nothing batch guarantee and the quiescence invariant. Each has
exactly one owner:

| Rule / invariant | Owner (the one place it is encoded and enforced) |
|---|---|
| Input validity: interval | `assertValidInterval` — shared gate, three public callers (§3.1) |
| Input validity: recurrence | `bookRecurring`'s recurrence gate (§3.1) |
| Input validity: attendees | `assertValidAttendees` — shared gate, three public callers (§3.1) |
| Input validity: capacity value | `setCapacity`'s gate (§3.1, §3.9) |
| Room no-overlap | `commitBookings` (§3.2) |
| Capacity | `commitBookings` (§3.3) |
| Person no-overlap | `commitBookings` (§3.4) |
| All-or-nothing batches | `commitBookings`, by construction (§3.5) |
| Quiescence | `promoteWaitlist` (§3.10) |

**How this satisfies "all four rules at the single commit authority."** The three
*state-dependent* rules — room no-overlap, capacity, person no-overlap — are enforced inside
`commitBookings`, the only writer, so every creating path (book, every series occurrence,
promotion) meets them by construction: to create is to ask the authority. Input validity is
*state-independent* and is enforced by shared gates that run, contractually, before the
authority is reachable — one encoding per input kind, every creating path provably behind it:
`book`/`bookRecurring` gate their own arguments; promotion's entries were gated **at join by the
same shared functions**, and state-independence means that verdict cannot go stale between join
and promotion. Validity cannot move *inside* the authority without breaking two recorded
contracts: the interval gate must run before series expansion (interval-before-recurrence order,
pinned by T28), and the same gates serve `joinWaitlist`, a non-creating path the authority never
sees. The enforcement point per rule is singular either way — which is what §9 actually demands.

### 3.1 Input validity — the shared gates

Four input kinds, four gates, one encoding each:

- **Interval** — `assertValidInterval`: integers with `start < end`, else
  `InvalidIntervalError`. Three public callers (`book`, `bookRecurring`, `joinWaitlist`).
  Unchanged from stage 3.
- **Recurrence** — `bookRecurring` only: object with integer `everyMinutes >= 1` and integer
  `count >= 1`, else `InvalidRecurrenceError`. Unchanged.
- **Attendees** — `assertValidAttendees`, new, shared by the same three operations the interval
  gate serves: omitted (`undefined`) means the empty list; otherwise the value must be an array
  containing no duplicate elements (SameValueZero), else `InvalidAttendeesError`. Elements are
  opaque and not type-checked (§2). The gate returns the validated **copy** (frozen) that the
  caller hands onward — validation and the seam-copy defense are one act, so an unvalidated or
  caller-aliased list cannot exist inside.
- **Capacity value** — `setCapacity` only: an integer `>= 0`, else `InvalidCapacityError`
  (§3.9). Inline in its one caller — a shared gate needs a second caller, and none exists.

### 3.2 Room no-overlap

**Invariant:** within one room, no two live bookings overlap; intervals are half-open integer
`[start, end)`; `a` and `b` overlap iff `a.start < b.end && b.start < a.end`.

**Owner: `commitBookings(room, occurrences, organizer, attendees)`** — still the *only* code
path that mints ids, creates records, or writes to the booking store, and stage 4 does not add a
creating path: the same three (book: batch of one; bookRecurring: the expanded batch; promotion:
a batch of one per queued entry) all route through it. The read-only query `roomHasConflict`
remains the rule's one encoding for its two askers (`commitBookings`' batch-vs-store leg and
`joinWaitlist`'s gate), under the stage-3 line that still governs:

> **Non-creating paths may ask a query; every creating path must ask the authority — by asking
> it to commit.** Queries never write and never throw; only `commitBookings` turns "no" into an
> error, and only `commitBookings` writes.

The removing path still cannot violate this invariant (a subset of a pairwise-non-overlapping
set is pairwise non-overlapping), and `cancel`'s subsequent promotions go through the authority
like every other creation.

### 3.3 Capacity

**Invariant:** every live booking's attendee count was `<=` its room's **effective capacity at
its creation time**. Deliberately *not* "no booking exceeds the current capacity": capacity is a
creation-time gate only (GOALS-recorded) — lowering a capacity evicts nothing and leaves
standing bookings above the new value standing, so the invariant is about admission, not about
the present store.

**Owner: `commitBookings`.** Effective capacity is the declared value, or unlimited for an
undeclared room; the one encoding of "undeclared = unlimited" is the internal query
`effectiveCapacity(room)` (§5), which has exactly two askers — this check, and `setCapacity`'s
raise detection (§3.9). The check is **batch-level, not per-occurrence**: a batch has one room
and one attendee list, so `attendees.length > effectiveCapacity(room)` is a single question per
commit, asked once before any interval scanning (order argued in §3.6). Rejection is
`CapacityExceededError`; `count === capacity` passes; the empty list passes every capacity
including 0.

### 3.4 Person no-overlap — the first cross-room rule

**Invariant:** no person id appears in the attendee lists of two overlapping live bookings,
**across all rooms** of the instance.

**Owner: `commitBookings` — the conflict domain grows; the authority does not.** The rule's
domain is no longer "this room's array" but the whole store — and the authority already *holds*
the whole store (it lives in the factory closure beside `bookingsByRoom`). Absorbing the rule is
therefore a new read-only leg inside the same function — the internal scan
`personConflictsAnywhere(attendees, start, end)` (§5), asked only by the authority — not a
second writer, not a second encoding, and not a check outside the authority. Nothing about the
single-writer discipline changes: cross-room *reading* was always available to the one function
that owns creation; stage 4 is the first rule to need it.

**The batch-vs-batch person check is deleted as provably redundant** — recorded so the deletion
is a lemma, not an oversight: every batch has one room and one attendee list, so two occurrences
of a batch sharing an attendee (they all do, or none do) person-overlap iff their intervals
overlap — and overlapping intervals in one room already fail the room batch-vs-batch leg first.
Touching occurrences sharing attendees are legal by the same half-open predicate everywhere.
*Validity condition of the lemma:* it holds only while batches are single-room, single-list; if
a future operation ever batches across rooms or varies attendees per occurrence, the person
batch leg must be re-derived — recorded as the revisit condition.

**Half-open semantics apply verbatim:** a person may leave one meeting at minute 30 and start
another at minute 30, in any rooms.

**A same-room person overlap never reports as one.** In one room, overlapping intervals are
already a room conflict, and the room leg runs first (§3.6) — so `PersonConflictError` is, in
practice, always a *cross-room* answer. This is a derived consequence, pinned by test (T51), not
a rule of its own.

### 3.5 All-or-nothing batches

**Invariant and owner unchanged:** `commitBookings` is check-everything-then-commit; a rejected
batch leaves no observable trace, by construction, with no rollback path in existence. Stage 4
widens what "check everything" means — capacity and person legs join the two room legs — and the
guarantee composes for free: one occurrence failing ANY of the three state rules rejects the
whole series with nothing written, no ids minted, no room key created (T52). Promotion still
reuses this machinery with batches of one, which is precisely what keeps every rule at one
writer.

### 3.6 Contractual check order (creating paths)

1. **Interval validity** — `InvalidIntervalError` (gate: §3.1). First on every path, unchanged.
2. **Recurrence validity** (`bookRecurring` only) — `InvalidRecurrenceError`. Unchanged
   position (interval-before-recurrence is pinned by T28).
3. **Attendees validity** — `InvalidAttendeesError`. The new gate appends after the existing
   ones — existing gates keep their pinned relative order; "the attendees gate is the last
   validity gate on every path" is the one new ordering rule.
4. **Capacity** — inside `commitBookings`, batch-level, before any interval scanning;
   `CapacityExceededError`.
5. **Per occurrence, in occurrence order** — room-vs-store conflict, then room-vs-batch
   conflict (`BookingConflictError`), then person-vs-store overlap (`PersonConflictError`). The
   first failing check of the first failing occurrence reports.
6. **Commit** — mint ids, freeze records, append. Nothing written before this step.

**Why capacity before the interval legs:** a capacity failure is *time-independent* — this
request can never succeed in this room with this list at any time, and no enabling event short
of a capacity raise changes that; reporting it ahead of any timing accident tells the caller the
strongest true thing. (It also keeps every attendee-less path's behavior byte-identical to
stage 3, since the empty list passes every capacity.)

**Why room before person within an occurrence:** the room answer licenses the caller's next act
— `joinWaitlist` is available exactly when a room conflict exists — so when both hold, the room
answer routes the caller to the product's designed recourse. (The person conflict, if it
persists, is promotion's problem later, which is exactly what the waitlist is for.) It also
yields the same-room subsumption consequence of §3.4.

An invalid input never reaches the authority, on any path.

### 3.7 Cancellation

`cancel(bookingId)` is the seam's only removing operation, three contractual steps:

1. **Locate** — find the live booking with `id === bookingId`; otherwise `UnknownBookingError`.
   On this failure NOTHING happens: no removal, no promotion pass, no store touched.
2. **Remove** — splice exactly that booking from its room's array; siblings of a former series
   and all other rooms/bookings untouched, as always.
3. **Restore quiescence** — call `promoteWaitlist()` — the GLOBAL pass, unscoped (§3.10).

**The stage-3 per-room scoping is invalidated and removed — its recorded revisit condition
fired.** Stage 3 passed `promoteWaitlist(room)` "for the removed booking's room only (freed
space exists nowhere else — per-room isolation is structural, not filtered)." That sentence's
premise is now false by product rule: a cancel frees the room-interval *and every listed
attendee's time*, and a freed person can be the only obstacle of a queued entry in ANY room
(GOALS's own scenario: cancel in A promotes in B). The enabling reach of a cancel is
instance-wide, so the restoration step is instance-wide. Scoping the pass to "affected" rooms
would require computing, outside the authority, which entries a given cancel could enable — a
second encoding of the rules, rejected in §3.10.

**Is cancel still one responsibility?** Re-judged, and the stage-3 framing ("the pass is the
completion of removal") is retired rather than stretched: with two enabling events the honest
statement is the general one — **every operation that weakens a creation constraint ends by
restoring quiescence** (§3.10). Cancel weakens two constraints (room occupancy, person
occupancy) and so ends with the restoration call; `setCapacity` on a raise weakens one and ends
the same way. Cancel's body remains three named steps; the third is one call to the one function
that owns the invariant.

"Never issued" vs "already canceled" remain deliberately undistinguished (stage-2 argument).

### 3.8 The join gate

`joinWaitlist(room, start, end, requester, attendees = [])` is the seam's only enqueuing
operation:

1. **Interval validity** — same gate as bookings (`InvalidIntervalError`), first, unchanged.
2. **Attendees validity** — same shared gate as bookings (`InvalidAttendeesError`); the entry's
   list is validated **and copied** here, at join. This is the right and only place: validity is
   state-independent (a list valid at join is valid at promotion), and promotion must never be
   the first to discover a malformed list — the authority's promotion-time answers must be
   exactly the three state-rule rejections (§3.10).
3. **Conflict REQUIRED** — if `roomHasConflict(room, start, end)` is false, throw
   `NoConflictError`. Unchanged rule, unchanged encoding, unchanged reason (joining is defined
   only as the alternative to a conflicting request).
4. **Enqueue** — append `{room, start, end, requester, attendees}` to the instance's ONE global
   queue (§3.10, §5). Append order IS global join order.

**Capacity and person-overlap are deliberately NOT join gates** (GOALS-recorded, with its
reason): both can change between join and promotion — capacity can be raised, the blocking
person's meeting can be canceled — so eager rejection would refuse entries that may legitimately
promote later. The join gate checks exactly what is state-independent (validity) plus the one
thing that *defines* joining (a present room conflict). Consequence: an entry may join while
over-capacity or while its attendee is busy (T54); it simply waits.

**Born incompatible, still:** step 3 guarantees every entry fails at least the room rule at the
moment it enters the queue — the first leg of quiescence, unchanged.

A rejected join (any of the three errors) leaves no trace. Duplicates are permitted, unchanged.

### 3.9 setCapacity — the declaration operation

`setCapacity(room, capacity)`:

1. **Capacity validity** — integer `>= 0`, else `InvalidCapacityError`; nothing changes on
   rejection. `room` is opaque as everywhere; no registry, no existence check (declaring is what
   makes the room *declared*).
2. **Write** — record the value for the room (overwrite on re-declare; lazy key). This is the
   capacity store's only writer. Lowering (or re-declaring equal) does nothing further: **no
   eviction** (capacity is a creation-time gate, §3.3) and **no promotion** (below).
3. **If the effective capacity strictly increased** — restore quiescence: call
   `promoteWaitlist()`, the same global pass cancel calls (§3.10).

**The raise test is the enabling-event definition, not entry eligibility.** Deciding *which
entries* now fit belongs to the authority alone; deciding *whether anything could possibly have
been enabled* is the event's own definition: a lower or equal declaration only tightens or
preserves constraints, and quiescence held before the call, so a pass would be dead code
asserting a false possibility — the same argument that keeps the pass out of `book()`. Note the
asymmetry it implies, recorded: **declaring a capacity on an undeclared room is never a raise**
(the old effective capacity was unlimited), so a first declaration never triggers promotion —
it can only constrain.

### 3.10 Quiescence, generalized — the invariant, its owner, and the trigger structure re-judged

**Invariant (GOALS-recorded, stage-4 form):** between public operations, no queued entry could
be successfully booked — where "booked" means passing **all four creation rules** with the
entry's own room, interval, and attendees.

**Owner: the internal function `promoteWaitlist()`** — global, unparameterized — still the only
code that removes entries from the queue and the only code that turns entries into bookings.
The stage-3 per-room signature and its single call site are replaced wholesale (both recorded
revisit conditions fired; this is the re-judgment, not a patch):

**The enabling events, enumerated with a completeness argument.** An operation can make a queued
entry newly bookable only by *weakening* something the authority checks. The authority checks:
room-interval occupancy (weakened only by removing a booking → `cancel`), person occupancy
(weakened only by removing a booking → `cancel`), capacity (weakened only by a strict raise →
`setCapacity`), and validity (state-independent — nothing weakens it). `book`, `bookRecurring`,
`joinWaitlist`, and promotion itself only *add* bookings or entries; `schedule` reads; a
lower/equal `setCapacity` only tightens. So the complete enabling-event set is: **any cancel;
any strict capacity raise.** The trigger structure realizes exactly this: `promoteWaitlist()` has
exactly **two call sites** — `cancel` step 3 and `setCapacity` step 3 — one per enabling event.
The audit is a grep: call sites of the owner match the enumerated event list, one to one.
Rejected trigger structures: a wrapper/decorator over mutating operations detecting "enabling
changes" (machinery re-encoding the event list it exists to enforce, with no third event in
sight); an observer/event bus (the same, heavier).

**What the pass does:** walk the ONE global queue **in join order**; for each entry, offer it to
the commit authority — `commitBookings(entry.room, [entry's interval], entry.requester,
entry.attendees)` in a try/catch — and on acceptance remove the entry (its booking now exists,
ordinary in every respect); on any of the authority's three state-rule answers —
`BookingConflictError`, `CapacityExceededError`, `PersonConflictError` — leave the entry queued
and continue. NOTHING else is caught: any other error propagates, and none exists by
construction (validity was settled at join, §3.8). The catch *enumerates* the three types
deliberately: the list is the audit of what promotion may swallow, and a future fourth rule must
show up here consciously (§4 records why there is no shared base type to hide behind).

**Why the pass offers EVERY entry, not an "affected" subset.** Computing which entries a given
event could have enabled — by freed room, freed attendees, raised-capacity room — is a second
encoding of the four rules living outside the authority, and drift between it and the
authority's own answers becomes an expressible bug (an entry the filter wrongly skips stays
wrongly queued: a quiescence violation). Under offer-everything, eligibility is decided in
exactly one place — the authority — and a wrong answer is structurally inexpressible. This is
the same argument that rejected pre-check-then-commit at stage 3, one level up. Cost: one
authority offer per queued entry per enabling event, all linear scans; GOALS scenarios remain
small integers, and no measured force exists (§5, §6 — the index row).

**Why one pass in GLOBAL join order is still the fixpoint** — the stage-3 lemma, re-proved for
the enlarged rule set (monotonicity): during a pass, the store only grows and capacities do not
change; every state rule is monotone in the store (adding a booking can only add room conflicts
and person conflicts, never remove them; capacity is constant within the pass). So an entry
rejected at its turn was rejected against a store at least as small as the final one — still
rejected. No repeat scan, no worklist. Cross-room competition resolves for free and in the right
order: of two entries in different rooms wanting the same person's time, the earlier GLOBAL join
is offered first and promotes; the later then person-conflicts with the just-minted booking and
stays queued (T57) — "the earliest-queued compatible entry" has one instance-wide answer, which
is why GOALS pins join order as global and why the order lives in one instance-wide structure
(§5).

**Recursion is impossible, still:** `promoteWaitlist` calls only `commitBookings`, which never
cancels, never touches the queue, and never touches capacities; the two callers of
`promoteWaitlist` are public operations not reachable from inside the pass.

**The three greppable facts, stage-4 form:**

1. **Entries are born incompatible** — `joinWaitlist` step 3, the only enqueuing code.
2. **Only an enabling event can make an entry compatible** — bookings are removed in exactly
   one place (`cancel` step 2) and capacity is raised in exactly one place (`setCapacity`
   step 2); every other mutation only adds bookings or entries, and the rules are monotone.
3. **Every enabling event immediately restores quiescence** — both events' operations end with
   the call to `promoteWaitlist()`, which leaves no compatible entry queued (the fixpoint
   lemma).

## 4. Rejection representation: thrown typed errors

All six operations **throw** on rejection; success returns the bare value. The stage-1 rationale
is unchanged. **The error vocabulary grows by four types (five → nine), each argued under the
grow-vs-reuse philosophy** (grow where a genuinely new rule with its own caller act exists;
reuse where the rule is the same):

- `InvalidCapacityError` — **new**, thrown only by `setCapacity`. A genuinely new input rule
  (integer `>= 0`) with its own caller act: fix the capacity value. Reuse candidates rejected:
  `InvalidIntervalError` (no interval is in sight) and `InvalidRecurrenceError` (nothing
  recurs) each name a different malformed input; the taxonomy's shape since stage 1 is one name
  per input kind, which is what keeps §11 honest at the seam.
- `InvalidAttendeesError` — **new**, thrown by all three interval-taking operations through the
  one shared gate. New input rule (an array, no duplicate ids); caller act: fix the list. A
  merged generic `InvalidInputError` was rejected for the same reason it has been rejected since
  stage 1: the name must say what is wrong from the caller's seat.
- `CapacityExceededError` — **new**, thrown by `book`/`bookRecurring` (and spoken internally by
  the authority to promotion, never escaping `cancel`/`setCapacity`). A genuinely new rule with
  a caller act all its own: bring fewer people, or choose another room. Reusing
  `BookingConflictError` was rejected because that type's established caller act — wait it out
  or `joinWaitlist` — is precisely wrong here: joining is unavailable (no room conflict need
  exist) and waiting cures nothing but a capacity raise. The message carries the declared
  capacity and the offending count in text (there is no capacity read operation — §2 — so the
  message is where a human learns the number); no structured payload until a programmatic
  consumer act exists (recorded revisit condition).
- `PersonConflictError` — **new**, same-shaped argument from the other side: the caller act is
  drop the busy attendee or move the time — and, decisively, **changing rooms does not help**,
  whereas it always cures a `BookingConflictError`; a caller's uniform room-conflict handler
  ("try another room" / "join this room's waitlist") would misroute person conflicts twice over
  (join may not even be available — the room can be free). Two different recoveries, two types.
- `InvalidIntervalError`, `InvalidRecurrenceError`, `UnknownBookingError`, `NoConflictError`,
  `BookingConflictError` — unchanged meanings, unchanged owners. `BookingConflictError` remains
  the room-interval answer only — it never reports capacity or person trouble.

**Still no common base class — re-judged at nine types.** The new near-force: promotion's catch
now wants "any authority rejection," which a `CreationRejectedError` base would name. Rejected:
that consumer is internal and deliberately *enumerating* (the catch list is the audit of what
promotion may swallow — a base class would let a future rule slip in silently); at the seam, no
caller act handles "any rejection" uniformly — every type above has a *different* recovery,
which is the whole argument for their existence. Revisit iff a seam consumer with a genuine
uniform act appears.

Error payloads remain messages only, in booking terms, distinguished by `instanceof` (and
`name`).

## 5. Confined internals (implementation guidance, not contract)

Free to change without touching the seam:

- **Booking store: `Map<string, InternalBooking[]>` (`bookingsByRoom`)** — unchanged shape, but
  the stored record grows a private field: `InternalBooking = frozen {id, room, start, end,
  organizer, attendees: frozen string[]}`. The internal record is the ONE home of a booking's
  attendee list — a parallel `Map<id, attendees>` was rejected as a second structure asserting
  facts about the same booking (drift on cancel, the standing anti-index argument). Records stay
  frozen at commit: they no longer cross the seam themselves, but immutability keeps in-place
  edits — the one mutation the single-writer audit cannot see — inexpressible.
- **`schedule()` mints the public record**: a fresh frozen five-field `Booking` per internal
  record per call (the record shape is contract; the attendee list never leaves — §2). No test
  or contract promises reference identity of records across calls; freshness per call was
  already the contract for the *array*.
- **Capacity store: `Map<string, number>` (`capacityByRoom`)** — third sibling map, keyed
  lazily, only by `setCapacity` (its only writer). Values are the declared finite integers
  `>= 0` only; **unlimited is represented by key absence alone** — `Infinity` is never stored,
  so "unlimited" has one representation, not two.
- **`effectiveCapacity(room) -> number`** — returns the declared value or `Infinity`; the one
  encoding of "undeclared = unlimited," with exactly two askers: the authority's capacity leg
  (§3.3) and `setCapacity`'s raise detection (§3.9). Read-only, never throws.
- **Waitlist store: ONE global array (`waitlist: Array<{room, start, end, requester,
  attendees}>`)** — replaces stage 3's `waitlistByRoom` map. The per-room map was the data shape
  of "promotion is per-room," a judgment stage 4 invalidates; with GLOBAL join order pinned by
  GOALS, the ordering must be instance-wide, and the honest structure makes the order *be* the
  structure: append = join, walk = join order. Rejected: per-room queues plus global sequence
  numbers merged at promotion time — two structures encoding one ordering, reconciled at every
  pass (drift), serving a per-room grouping that no longer has a consumer. Consequence: the
  entry now **carries its `room`** — stage 3's "no room field, the map key already says it"
  inverts because the map key is gone; there is still exactly one copy of the fact. Entries stay
  plain and unfrozen (they never cross the seam), but their `attendees` array is the gate's
  frozen seam-copy (§3.1), so post-join caller mutation cannot reach it.
- `overlaps(aStart, aEnd, bStart, bEnd)` — THE half-open predicate, unchanged, still the one
  encoding of overlap for room and person legs alike.
- `roomHasConflict(room, start, end) -> boolean` — unchanged: the room-conflict question's one
  encoding; two askers (authority's batch-vs-store leg, join gate).
- **`personConflictsAnywhere(attendees, start, end) -> boolean`** — new read-only query: does
  any of these ids appear on a live booking overlapping `[start, end)` in ANY room? Built on the
  one `overlaps()` predicate; implementation: a `Set` of the batch's ids, then walk every room's
  array, interval test first, id-intersection second. Its **sole asker is the authority's person
  leg** — it is named for the legibility of a function that now enforces three state rules
  (§12's one-sentence test), not for sharing; it stays internal beside `roomHasConflict`, and
  the non-creating world has no business asking it (person-overlap is not a join gate).
- `commitBookings(room, occurrences, organizer, attendees) -> string[]` — the single writer;
  signature grows the validated attendee list (already gated and copied by the caller's shared
  gates, §3.1). Check order per §3.6; commit loop additionally stamps the frozen `attendees`
  list on each record. Sole-writer role is the contractual part.
- `promoteWaitlist() -> undefined` — the quiescence owner (§3.10): global, unparameterized;
  walks the one queue in join order; try-commits each entry via the authority; catches exactly
  the three state-rule errors; splices promoted entries out. Called from exactly two sites
  (`cancel`, `setCapacity`-on-raise). Internal only; not exported.
- `assertValidInterval(room, start, end)` — unchanged, three callers.
- `assertValidAttendees(room, attendees) -> frozen string[]` — the attendees gate (§3.1), three
  callers; returns the validated frozen copy.
- **Linear scans everywhere, re-judged under the stage-4 load** — the person leg is
  O(total live bookings) per occurrence, and every enabling event now offers the whole queue to
  the authority. Still: GOALS scenarios are small integers, the only present workload is the
  falsifier suite, and a person→bookings (or interval) index is a second structure asserting
  the same facts with an invariant-maintenance cost on every commit and cancel. **No index
  without a measured force** — the trigger remains a measured hot path from a real consumer,
  which does not exist. Same verdict for the id→booking index (cancel's locate) and any
  queue-by-room index for promotion.
- Id minting: per-instance counter, never reused — unchanged; promoted bookings mint at
  promotion time, in promotion order, through the same counter inside `commitBookings`.

## 6. Subtractive pass — re-run on stage-4 evidence

**Fired stage-3 revisits, re-judged from scratch (old text replaced in §3):**

| Stage-3 judgment (its recorded revisit condition) | Stage-4 re-judgment |
|---|---|
| Promotion scoped per room — `promoteWaitlist(room)`, "per-room isolation is structural, not filtered" (revisit: an operation that frees space beyond one room) | **Invalidated by the product**: a cancel frees people, and a freed person can enable an entry in any room. The pass is now global and unscoped (§3.7, §3.10); scoping would re-encode the rules outside the authority. |
| Promotion triggered ONLY by cancellation (revisit: a second space-freeing operation) | **Invalidated**: a capacity raise is an enabling event that is not a cancel. Re-judged structure: the owner stays ONE function; call sites grow to exactly two, matching the enumerated enabling-event set one-to-one — the trigger responsibility reads as "every constraint-weakening operation ends by restoring quiescence" (§3.10). |
| "The pass is the completion of removal" framing of cancel's single responsibility | **Retired, not stretched**: with two enabling events the honest general statement replaces the cancel-specific one (§3.7). |
| `waitlistByRoom` map; entry carries no `room` field | **Superseded**: one global queue (global join order is the structure); the entry carries its room — still exactly one copy of the fact (§5). |

**Candidates introduced or deleted on stage-4 evidence** (prior tables' verdicts stand where no
new force touches them):

| Candidate | Prior verdict | Stage-4 verdict | Why (on the new evidence) |
|---|---|---|---|
| `setCapacity` public operation | n/a | **introduced** | GOALS pins a declaration operation; capacity is a per-room attribute with its own writer (§3.9). |
| `capacityByRoom` third sibling map | n/a | **introduced** | Capacity has its own lifecycle (survives an empty schedule, one writer, overwrite semantics); a number per room, keyed lazily by its only writer (§5). |
| `effectiveCapacity` query | n/a | **introduced** | Two askers (authority's capacity leg; raise detection) of one question — "undeclared = unlimited" gets one encoding (§3.3, §3.9). |
| Storing `Infinity` for undeclared rooms | n/a | **deleted** | Two representations of "unlimited" (absent key AND a stored value) is a drift state; absence alone carries the fact (§5). |
| One global waitlist array (replacing the per-room map) | per-room map (stage 3) | **introduced** | GOALS pins global join order; the per-room grouping's only consumer (per-room promotion) is invalidated; the order should BE the structure, not data reconciled across structures (§5). |
| Per-room queues + global sequence numbers | n/a | **deleted** | Two structures encoding one ordering, merged on every pass — drift risk bought for a grouping nothing consumes (§5). |
| `room` field on the waitlist entry | deleted (stage 3) | **introduced — prior deletion inverted** | The map key that carried the fact is gone; the global array's entries must say their room; still exactly one copy (§5). |
| `personConflictsAnywhere` query | n/a | **introduced** | The person rule's one encoding, named for the authority's legibility now that it enforces three state rules; sole asker is the authority — deliberately unavailable to non-creating paths (§3.4, §5). |
| Person batch-vs-batch leg in the authority | n/a | **deleted (lemma)** | Provably unreachable while batches are single-room/single-list: a person overlap within a batch is always a room overlap first (§3.4; revisit if batching ever spans rooms). |
| Person/interval index (person → bookings) | n/a | **deleted — the trap this stage invites** | No measured force: workloads are the falsifier suite; an index is a second structure asserting the same facts, with maintenance cost on every commit and cancel; the trigger (a measured hot path from a real consumer) does not exist (§5). |
| Affected-set filtering in the promotion pass (offer only plausibly-enabled entries) | n/a | **deleted** | A second encoding of the four rules outside the authority; filter/authority drift becomes an expressible quiescence bug. Offer-everything keeps eligibility decided in exactly one place — the stage-3 pre-check rejection, one level up (§3.10). |
| Unconditional promotion pass in `setCapacity` (incl. lower/equal) | n/a | **deleted** | A non-raise only tightens constraints and quiescence held before the call — the pass would be dead code asserting a false possibility; the same argument that keeps the pass out of `book()` (§3.9). |
| Trigger wrapper / event bus for enabling events | n/a | **deleted** | Two enumerable call sites realize the complete event set; machinery would re-encode the very list it exists to enforce, for a third event that does not exist (§3.10). |
| `attendees` field on the public Booking record | n/a | **deleted — the seam decision argued, not defaulted** | No consumer act reads it; the five-field shape is shipped contract (asserted by T38/T41); attendee data should not leak for free. Non-enumerable variant also rejected (leaks via property access while dodging the tests) (§2). |
| `attendees` on the internal record + `schedule()` minting public records | n/a | **introduced** | The list must live somewhere the authority's person leg can see; the internal record is its one home; a parallel `Map<id, attendees>` is a second structure asserting the same facts (drift on cancel) (§5). |
| `attendeeCount` numeric field / separate headcount | n/a | **deleted** | GOALS merged count and list into one concept; a second field re-creates the disagreement states the merge killed (§2). |
| Capacity / person-overlap as join gates | n/a | **deleted** | GOALS-recorded reason: both can change before promotion; eager rejection refuses legitimately promotable entries (§3.8). |
| Validating attendee ids as strings / person registry | n/a | **deleted** | Ids are opaque labels like organizer/requester; type-validation is the first brick of the registry GOALS excludes (§2). |
| `InvalidCapacityError`, `InvalidAttendeesError`, `CapacityExceededError`, `PersonConflictError` | n/a | **introduced (four)** | Each a genuinely new rule with its own caller act; reuse candidates each name a different condition or recovery — full per-type argument in §4. |
| `CreationRejectedError` base class for the authority's answers | no base class (5 types) | **deleted again — re-judged at 9 types with a near-force** | Promotion's catch is the one candidate consumer, and it deliberately enumerates (the list is the audit); no seam act handles "any rejection" uniformly (§4). |
| Structured payload fields on `CapacityExceededError` | n/a | **deleted** | No programmatic consumer act; the human-readable message carries the numbers; revisit when a consumer act appears (§4). |
| Eviction / re-check on capacity lowering | n/a | **deleted** | GOALS: all rules are creation gates; retroactive enforcement is a non-goal (§3.3). |
| Capacity read operation (`getCapacity`) | n/a | **deleted** | No consumer act; capacity is observable through rejections exactly as the waitlist is through promotions (§2). |
| Per-room owner object (`{bookings, waitlist, capacity}`) | deleted three times | **deleted a fourth time — the force got weaker** | The three stores no longer even share a shape: bookings are per-room, capacity is per-room, but the queue is now GLOBAL — a Room object could hold only two of the three, and the operation that touches all stores (promotion) is instance-scoped, not room-scoped (§3.10, §5). |
| Freezing internal booking records | kept (stage 1–3, seam defense) | **kept — force restated** | They no longer cross the seam (schedule mints), but immutability keeps in-place edits — mutation invisible to the single-writer audit — inexpressible (§5). |

## 7. Falsifier test plan

Each case names the design element it verifies. All run against a fresh `createRoomBook()`
unless stated. **T1–T43 are the stage-1/2/3 suites, implemented and green — the stage-4
regression gate: all must pass with roombook.test.js byte-unmodified.**

**The T43 surface pin — a recorded collision requiring a Guide decision.** T43's final
assertions pin the module's exports and the instance's keys *exactly* to the stage-3 surface
(`Object.keys` equality against the five-error export list and the five-function instance). Any
stage-4 seam growth — the `setCapacity` key, the four new error exports — falsifies those two
assertions even though every stage-1–3 *behavior* is unchanged. The byte-unmodified constraint
and the GOALS-mandated seam growth are therefore in direct conflict **at implementation time**
(the design round sidesteps it by deferring seam wiring — the skeleton defines the new
vocabulary without exporting it). Resolution options, for the Guide: (a) amend T43's two
surface assertions in the implementation round (a sanctioned, minimal edit to the hashed file);
or (b) supersede the surface pin in the stage-4 file (T60 below re-pins the grown surface) and
exempt T43's last two asserts. Gaming the test — non-enumerable seam members so `Object.keys`
misses them — is rejected in §2. All behavioral tests T1–T42 and T43's byte-identity are
unaffected and remain hard gates.

### Stage-1 table (implemented; regression gate)

| # | Case | Verifies |
|---|---|---|
| T1 | book A [10,20), then A [20,30) → both succeed; schedule has 2 entries | half-open boundary: touching intervals do not conflict (§3 predicate) |
| T2 | book A [10,20) twice → second throws `BookingConflictError` | identical interval rejected |
| T3a | A [10,40) exists; book A [20,30) → conflict | containment rejected (new inside existing) |
| T3b | A [20,30) exists; book A [10,40) → conflict | containment rejected (new surrounds existing) |
| T4a | A [10,30) exists; book A [20,40) → conflict | partial overlap, new starts inside existing |
| T4b | A [20,40) exists; book A [10,30) → conflict | partial overlap, new ends inside existing |
| T5 | A [10,20) exists; book B [10,20) → succeeds | rooms fully independent |
| T6 | `schedule("never-used")` → `[]` (and is an array, not an error) | unknown/empty room yields empty result |
| T7 | book A [50,60), A [10,20), A [30,40) in that order → schedule starts = [10, 30, 50] | schedule ordered by start regardless of insertion order |
| T8 | book A [20,20) and A [30,20) → `InvalidIntervalError` both times | end <= start rejected, incl. zero length |
| T9 | book A [10.5, 20), A [10, NaN), A ["10", 20) → `InvalidIntervalError` | non-integer times rejected (`Number.isInteger` gate) |
| T10 | after a T4-style rejection: book A [100,110) → succeeds; schedule identical to pre-rejection plus the new booking | rejected call leaves no trace (§3 commit-last ordering) |
| T11 | T8/T9 errors are `instanceof InvalidIntervalError` and NOT `BookingConflictError`; T2 error the reverse | rejection kinds distinguishable at the seam (§4) |
| T12 | book A [10,20), B [10,20), C [5,15) → three ids, all distinct | id uniqueness across rooms (instance-wide counter) |
| T13 | mutate the array returned by `schedule(A)` (push/splice) and attempt to mutate a returned record → next `schedule(A)` unchanged; record mutation throws in strict mode / no-ops | seam cannot corrupt the store (fresh array, frozen records) |
| T14 | two `createRoomBook()` instances: booking in one is invisible to the other | factory confines state per instance; no module-level state |
| T15 | id returned by `book` appears as `id` of exactly one record in `schedule(room)`, with matching room/start/end/organizer | book/schedule agree on the Booking record contents |

### Stage-2 table (implemented; regression gate)

| # | Case | Verifies |
|---|---|---|
| T16 | bookRecurring A [60,120) {everyMinutes:1440, count:3} → returns 3 distinct string ids; `schedule(A)` shows exactly [60,120), [1500,1560), [2940,3000), each a frozen ordinary Booking record | GOALS recurring scenario end-to-end; occurrences are ordinary bookings (§2) |
| T17 | ids[i] from T16 names the record whose interval is occurrence i's ([60,120) ↔ ids[0], etc.); the returned array is fresh (mutating it, then `schedule(A)`, shows no effect) | return-shape decision: occurrence-order id array, caller-owned (§2) |
| T18 | book A [2940,3000) first; then bookRecurring A [60,120) {1440, 3} → `BookingConflictError` (k-th occurrence conflicts); `schedule(A)` byte-identical to before the call; then book A [60,120) — the slot occurrence 0 would have taken — **succeeds** | all-or-nothing by construction: nothing written until whole series proven bookable, no ids minted, no partial trace (§3.5) |
| T19 | bookRecurring A [0,60) {everyMinutes:30, count:2} → `BookingConflictError`; `schedule(A)` = [] | intra-series self-overlap (stride < duration) rejected whole, via the same predicate — batch-vs-batch check (§3.2) |
| T20 | bookRecurring A [0,60) {everyMinutes:60, count:3} → succeeds; schedule = [0,60),[60,120),[120,180) | touching stride (everyMinutes == duration) succeeds: half-open predicate in the batch check (§3.2) |
| T21 | bookRecurring A [10,20) {everyMinutes:5, count:1} → returns array of length 1; schedule shows one booking [10,20); its id cancelable like any `book` id | count == 1 degenerate series behaves like book() (§3.2: batch of one) |
| T22 | bookRecurring with {everyMinutes:0}, {everyMinutes:-10}, {count:0}, {count:-1}, {count:1.5}, {everyMinutes:"60"}, and missing/non-object options → `InvalidRecurrenceError` each time; NOT `BookingConflictError`, NOT `InvalidIntervalError`; nothing booked | malformed recurrence is invalid input, distinguishable by type (§3.6 step 2, §4) |
| T23 | book B [60,120); bookRecurring A [60,120) {1440, 3} → succeeds despite B's booking; a failing series in A (T18 setup) leaves `schedule(B)` untouched | series ROOM conflicts scoped to the series' room (§3.2) |
| T24 | book A [10,20); cancel(id); book A [10,20) → succeeds with a NEW id; `schedule(A)` shows only the new booking | cancel frees the slot for the IDENTICAL interval; removal is real (§3.7) |
| T25 | bookRecurring A ×3 (T16 shape); cancel(ids[1]) → `schedule(A)` has occurrences 0 and 2 intact under their original ids; the freed middle slot is rebookable | occurrence canceled individually; siblings unlinked and untouched — no series residue (§2, §3.7) |
| T26 | cancel(id) twice → second throws `UnknownBookingError`; cancel("bk-999") and cancel("nonsense") on a fresh instance → `UnknownBookingError`; each is NOT any of the other error types (instanceof + name) | dead id (double-cancel or never issued) is the distinguishable error (§3.7, §4) |
| T27 | book A [10,20), A [30,40), B [10,20); cancel the A [10,20) id → `schedule(A)` = [30,40) only, `schedule(B)` unchanged | cancel removes exactly one booking; other bookings and rooms untouched (§3.7) |
| T28 | A [10,30) exists; book A (20.5, 25) — non-integer AND inside the existing booking → `InvalidIntervalError`, not conflict; same via bookRecurring; and bookRecurring A (20, 10) {everyMinutes:0, count:0} → `InvalidIntervalError` (interval gate before recurrence gate) | contractual check order: validity before conflict, interval before recurrence (§3.6) |
| T29 | after T18's rejected series and T26's failed cancels: `schedule` across A and B matches exactly the successful operations performed | rejected/failed operations of ALL kinds leave no observable trace (§3.5, §3.7) |

### Stage-3 table (implemented; regression gate)

| # | Case | Verifies |
|---|---|---|
| T30 | book A [10,20); joinWaitlist A [30,40) — currently bookable → `NoConflictError` (NOT `BookingConflictError`, NOT `InvalidIntervalError`); then cancel the [10,20) booking → `schedule(A)` = [] | join-only-on-conflict gate; distinguishable rejection; rejected join leaves no trace (§3.8, §4) |
| T31 | joinWaitlist A [20,20), [30,20), [10.5,20), [10,NaN) → `InvalidIntervalError` each time; joinWaitlist A [20,10) on an EMPTY room → `InvalidIntervalError`, not `NoConflictError` | same interval rule through the same gate as bookings; validity before the conflict-required gate (§3.8) |
| T32 | GOALS scenario end-to-end: book A [0,30) olga → id; joinWaitlist A [0,30) pete → `undefined`; cancel(id) → `schedule(A)` = one frozen Booking [0,30) organizer "pete", fresh id; cancel(pete's id) → `schedule(A)` = [] and stays [] | promotion is a real ordinary booking via the one authority; entry leaves queue (§2, §3.10) |
| T33 | book A [0,60) big; joinWaitlist A [0,30) w1, then A [30,60) w2; cancel(big) → BOTH promoted in one cancel; canceling each promoted booking then empties A permanently | multi-fit cascade: promote-ALL-that-fit in join order; one pass drains every compatible entry (§3.10) |
| T34 | book A [0,30) b1, A [30,60) b2; joinWaitlist A [20,40) w1, then A [0,20) w2; cancel(b1) → w1 NOT promoted, w2 promoted; then cancel(b2) → w1 promotes | queue-order skip: earliest incompatible entry stays queued; skipped entry promotes on a later enabling event (§3.10) |
| T35 | book A [0,30) blocker; joinWaitlist A [0,30) w1, then A [10,40) w2; cancel(blocker) → w1 promoted, w2 stays queued; direct book A [10,40) → `BookingConflictError`; cancel(w1's booking) → w2 promotes | overlapping compatible entries: join order wins; later entry provably unbookable between operations (§3.10) |
| T36 | book A [0,30) b1, A [30,60) b2; joinWaitlist A [25,45) w; cancel(b1) → w NOT promoted; book A [0,25) → succeeds | promotion respects no-overlap against REMAINING bookings; unpromotable freed slot stays free (§3.2, §3.10) |
| T37 | (a) cancel with waitlist EMPTY behaves as stage 2 (T24 shape); (b) all-incompatible waitlist: cancel promotes nothing, freed slot rebookable identically | cancel with empty/all-incompatible waitlist is exactly stage-2 cancel (§3.7) |
| T38 | duplicate-interval entries; cancel → w1's booking frozen, opaque id, organizer = requester, exactly five fields; canceling IT promotes w2; then A empty permanently | promoted bookings ordinary (frozen, stage-1 shape, cancelable); re-triggered cascade; duplicates coherent (§2, §3.10) |
| T39 | book A [0,30), book B [0,30); joinWaitlist B [0,30) wb; cancel(A's id) → wb NOT promoted (its room conflict in B stands); cancel(B's id) → wb promotes | a cancel elsewhere leaves a still-room-blocked entry queued — under the stage-4 GLOBAL pass this holds because the authority still says no, not because B's queue went unexamined (§3.7, §3.10) |
| T40 | two instances: cancel in #2 never promotes #1's entry; #1's own cancel does | instance isolation extends to waitlists (§2) |
| T41 | join returns `undefined`; no queue residue in `schedule`; `Object.keys` of a Booking = exactly the five stage-1 fields | seam leaks nothing; record shape is contract (§2) |
| T42 | quiescence sweep: at every between-operations point of T33–T39, a direct `book()` of each still-queued entry's exact room+interval → `BookingConflictError` | quiescence probed at the seam, behaviorally (§3.10) |
| T43 | T1–T29 byte-for-byte unmodified pass; module exports and instance keys pinned to the stage-3 surface | regression gate — **the surface-pin half collides with stage-4 seam growth; see "The T43 surface pin" above** |

### Stage-4 table (to be written in the implementation round)

Attendee-carrying state is asserted through behavior only, as always: capacity through
acceptance/rejection, person-overlap through rejection and promotion, queue state through the
book-probe. "ids ×N" below means a list of N distinct opaque strings.

| # | Case | Verifies |
|---|---|---|
| T44 | setCapacity(A, v) for v in −1, 1.5, "4", NaN, Infinity, null, undefined (missing) → `InvalidCapacityError` each time (instanceof + name; NOT InvalidInterval/InvalidRecurrence/InvalidAttendees); afterward book A [0,30) with ids ×5 → **succeeds** (room still undeclared/unlimited — rejection left no trace) | capacity-value gate and its distinguishable error; failed declaration writes nothing (§3.1, §3.9 step 1, §4) |
| T45 | setCapacity(A, 4) → `undefined`; book A [0,30) ids ×5 → `CapacityExceededError` (instanceof + name, NOT BookingConflictError); schedule(A) unchanged, the slot still bookable; book A [0,30) ids ×4 → succeeds (count == capacity) | the capacity gate at the authority: > rejected, == accepted; rejection no-trace; setCapacity returns undefined (§3.3, §2) |
| T46 | setCapacity(A, 0); book A [0,30) (attendees omitted) → succeeds; book A [40,50) with [] → succeeds; book A [60,70) with ids ×1 → `CapacityExceededError` | capacity 0 semantics; omitted ≡ empty list; empty passes every capacity (§3.1, §3.3) |
| T47 | fresh instance: book A [0,30) org, ids ×50 → succeeds (stage-1-shape call plus a big list) | undeclared room is unlimited — absence-of-key encoding (§3.3, §5) |
| T48 | setCapacity(A, 2); book A [0,30) ids ×2 (ok); setCapacity(A, 1) → existing booking intact (schedule unchanged — nothing evicted); book A [40,50) ids ×2 → `CapacityExceededError`; ids ×1 → ok; with a queued over-capacity entry present, the lowering triggers no promotion (probe per T58) | re-declare overwrites, future creations only; lowering evicts nothing and enables nothing (§3.3, §3.9) |
| T49 | duplicates ["p1","p1"] → `InvalidAttendeesError` on book, bookRecurring, AND joinWaitlist (nothing created/queued — no-trace probes); non-array attendees ("p1", 7, {}) → `InvalidAttendeesError`; weird opaque ids ("", "🦆", "p 1") accepted; order pins: invalid interval + duplicates → `InvalidIntervalError`; bad recurrence + duplicates → `InvalidRecurrenceError`; valid inputs + duplicates + would-conflict → `InvalidAttendeesError` (validity before authority) | the one attendees gate on all three ops; element opacity; the contractual gate order incl. "attendees gate last of the validity gates" (§3.1, §3.6, §4) |
| T50 | book A [0,30) organizer "x" attendees ["p1"]; book B [10,20) organizer "p1" (no attendees) → **succeeds**; book B [10,20) organizer "y" attendees ["p1"] → `PersonConflictError` | organizer is NOT implicitly an attendee — only listed ids are checked (§2) |
| T51 | cross-room: A [0,30) ["p1"] then B [15,25) ["p1"] → `PersonConflictError` (GOALS scenario); B [30,60) ["p1"] → succeeds (touching, half-open); B [15,25) ["p2"] → succeeds (no shared id); same-room: A [10,40) ["p1"] → `BookingConflictError`, NOT PersonConflictError (room leg first — the §3.4 subsumption consequence) | person rule domain = all rooms; half-open semantics; check order inside the authority (§3.4, §3.6) |
| T52 | (a) setCapacity(A, 2); bookRecurring A [60,120) {1440,3} ids ×3 → `CapacityExceededError`, schedule(A) = [], occurrence-0 slot bookable; (b) book B [2940,3000) ["p1"]; bookRecurring A [60,120) {1440,3} ["p1"] → `PersonConflictError` (occurrence 2's time is p1-busy in B), schedule(A) = [], schedule(B) untouched, no ids minted | all-or-nothing composes over the NEW rules: one occurrence failing capacity or person rejects the whole series with no trace (§3.5) |
| T53 | bookRecurring A [0,60) {everyMinutes:60, count:3} ["p1","p2"] → succeeds (own touching occurrences share attendees legally); with p1 busy in B only at [200,300) (overlapping no occurrence) → still succeeds | no false intra-series person conflict — the deleted batch-leg lemma, probed (§3.4) |
| T54 | book A [0,30) b (no attendees); setCapacity(A, 1); joinWaitlist A [0,30) w ["p","q"] → **accepted** (over capacity is not a join gate); separately: p1 busy in C [0,30); joinWaitlist A [0,30) w2 ["p1"] (A room-conflicted) → **accepted** (person-busy is not a join gate) | join gate unchanged: validity + conflict-required only; capacity/person deliberately not join gates (§3.8) |
| T55 | continue T54(first): cancel(b) → w NOT promoted (capacity 1 < 2); probe book A [0,30) org ["p","q"] → `CapacityExceededError`; setCapacity(A, 2) → w promotes (schedule(A) = [0,30) organizer w); probe: queue empty | an interval-fitting entry blocked by capacity stays queued; a capacity RAISE is an enabling event reaching the same owner (§3.9, §3.10) |
| T56 | book A [0,30) ["p1"] = idA; book B [0,30) (none) = idB; joinWaitlist B [0,30) w ["p1"] (valid: room conflict with idB); cancel(idB) → w NOT promoted (p1 busy in A); probe book B [0,30) org ["p1"] → `PersonConflictError`; **cancel(idA) — a cancel in ANOTHER room — → w promotes into B** | the cross-room enabling falsifier: promotion's reach is global; person-freeing cancels promote elsewhere (§3.7, §3.10) |
| T57 | book C [0,30) ["p1"] = idC; book A [0,30) = bA; book B [0,30) = bB; joinWaitlist A [0,30) w1 ["p1"]; joinWaitlist B [0,30) w2 ["p1"]; cancel(bA), cancel(bB) → both stay queued (person-blocked; probes); cancel(idC) — ONE event enables both → **w1 (earlier GLOBAL join) promotes into A; w2 stays queued** (probe: book B [0,30) org ["p1"] → `PersonConflictError`); cancel(w1's booking) → w2 promotes into B | global join order: cross-room competition for one person resolves by the one instance-wide order; the fixpoint under the monotonicity lemma; the person frees again → later entry promotes (§3.10, §5) |
| T58 | quiescence sweep extended: replay T54–T57's scenarios; after EVERY public call — **including every setCapacity, raising or lowering** — probe each still-queued entry via `book(entry.room, start, end, fresh-organizer, entry.attendees)` → throws one of `BookingConflictError` / `CapacityExceededError` / `PersonConflictError` (each probe is a rejected call, so it leaves no trace) | the generalized invariant itself, probed at the seam over the enlarged enabling-event set: between operations no queued entry passes all four rules (§3.10) |
| T59 | arr = ["p1"]; book A [0,30) org arr; arr.push("p2") → book B [0,30) ["p2"] **succeeds** (p2 never became busy) and book B [0,30) ["p1"] → `PersonConflictError` (original list is the truth); same probe for a waitlist entry mutated after join and before promotion; schedule(A) records: frozen, exactly the five stage-1 keys even for attendee-carrying bookings | attendee lists copied at the seam (in-bound defense); Booking record shape unchanged — the seam decision, probed (§2, §5) |
| T60 | stage-4 surface pin: module exports = createRoomBook + the nine error types; instance = frozen six-function object; two instances: setCapacity in one never constrains the other, and a cancel in one never promotes the other's entries | the grown seam pinned exactly once (supersedes T43's stage-3 surface pin — see the collision note); instance isolation extends to capacities (§1, §2) |

T44–T48 pin the capacity rule end to end (gate, error, 0, unlimited, overwrite/lower);
T49–T51 pin the attendees vocabulary and the person rule's domain, order, and semantics;
T52–T53 pin all-or-nothing over the new rules and the batch-leg lemma; T54–T57 pin the
generalized quiescence machinery — join gate unchanged, both enabling events, cross-room reach,
global join order; T58 is the invariant's behavioral audit over the enlarged event set; T59 pins
the two stage-4 seam defenses; T60 re-pins the grown surface. T1–T43 remain the regression gate,
with the T43 surface-pin collision recorded above for Guide resolution.
