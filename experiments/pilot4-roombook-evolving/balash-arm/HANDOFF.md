# Worker Handoff — Stage 1: room booking with conflict rejection

## ROLE
You are the implementation Worker — a senior engineer as capable as the Guide. The **design is the
deliverable**, not just passing tests. Do not redefine scope. If evidence invalidates the objective,
report it instead of expanding.

## DESIGN GOAL (a quality outcome, not a feature)
Give the "no two bookings for the same room may overlap" invariant **one owner and one gate**. There
must be a single place every booking attempt passes through, such that a reader auditing "can this
invariant ever be violated?" has exactly one method to read — no path can add a booking to a room
without the overlap check having decided. And the definition of *conflict itself* (half-open
interval overlap, and the fact that different rooms never conflict) must live in one home, not be
re-derived by each caller that pokes at raw start/end fields.

How you shape that — what types exist, whether interval math is a method on the booking or a free
predicate, how a room's bookings are stored — is yours to decide.

## BEHAVIOR IT MUST SATISFY (constraints on the design, not the thing to optimize)
- Book a room for a half-open interval [start, end) with an organizer.
- A booking is **rejected and nothing is created** if it overlaps an existing booking for the **same**
  room. The caller can observe that the attempt was rejected.
- Different rooms never conflict: identical intervals in different rooms both succeed.
- Half-open semantics: [10,20) and [20,30) do NOT conflict; [10,20) and [15,25) do.
- Read a room's schedule ordered by start time.
- Times are integers (minutes).

## WHY NOW
First capability of a new product. The overlap invariant is the whole point of the product; if its
enforcement is scattered or bypassable now, every later stage (cancellation, availability search,
recurring bookings) inherits an unsafe core. Establish the owner before anything is layered on it.

## WHAT "GOOD" AIMS AT
`skills/balash-guide/references/design-principles.md` — the target, not a checklist. Most relevant
here: #9 (one enforced place for the rule), #1/#5 (the conflict definition is behavior that lives on
the concept, not asked-for data a service decides externally), #10/#12 (do not add a type or module
that owns no current rule). Where a principle doesn't apply at this scale, don't force it.

## RELEVANT CONTEXT / PRESERVE / NON-GOALS
- Pure Node.js, in-memory, ZERO dependencies. Tests run with `node --test` and must pass.
- Reject on conflict must mean *nothing created* — an observable rejection, not a partial write.
- NON-GOALS (do not build for these; design for the truth in front of you now): cancellation,
  updates, persistence, availability/free-slot search, recurring bookings, multi-tenant identity,
  authorization. No speculative abstraction for imagined future stages.
- Degenerate/malformed intervals (end <= start) are a caller precondition violation, distinct from a
  legitimate-but-conflicting booking; treat the two differently so a rejected booking and a bug are
  not confused. (Chosen invariant — noted, not from the user.)
- The modules, classes, and interfaces are YOURS. Design for what's here.

## RETURN TO GUIDE
- Working code + `node --test` passing.
- Key design decisions: where the invariant is enforced (the one gate), where the conflict definition
  lives, and any type you introduced with the present force that requires it.
- Run the **subtractive pass** on your own design before returning: for every type/guard/wrapper,
  name the current rule/invariant/boundary whose ownership breaks if you delete it; collapse the rest.
- Result: met | partially_met | invalidated | blocked, against the design goal.

---

# Worker Handoff — Stage 2: recurring series + cancel

## DESIGN GOAL (a quality outcome, not a feature)
Keep the same-room no-overlap invariant a **single owned truth** as admission grows from one booking
to an atomic *set*, and give cancellation an owner that is the inverse of admission — without
inventing entities the product does not have.

- **One atomic gate.** A recurring series is admitted all-or-nothing: if any occurrence would break
  the room invariant (against an existing booking OR against another occurrence of the same series),
  nothing is created. A single booking should not need its own separate enforcement path — a single
  booking is the degenerate case of a set. There must remain exactly one place a reader checks to
  answer "can the room invariant ever be violated?" and that place must guarantee no partial write.
  In-memory and synchronous: validate-then-commit needs no transaction/rollback machinery — design
  it so none is required.
- **Cancel as the inverse of admission.** Making an interval free again is removing exactly one
  booking from the same owner that admits them. Decide what *names* a booking for removal; introduce
  a booking id only if a present force requires one.

How you shape this — one gate or two, how a series is expressed, what cancel takes — is yours.

## BEHAVIOR IT MUST SATISFY
- Book a series: first interval [start,end), stride `everyMinutes`, `count` occurrences; occurrence i
  is [start+i*everyMinutes, end+i*everyMinutes). ALL-OR-NOTHING vs existing bookings in that room.
  On success the caller learns the created bookings.
- Cancel a booking so its interval becomes free again (a later booking there then succeeds).
- Everything from Stage 1 still holds (half-open, integer minutes, per-room, ordered schedule).

## WHY NOW
Second capability. Series is the first time admission is a *batch*, which is exactly where a partial
write or a second enforcement path would silently corrupt the invariant the whole product rests on.
Cancel is the first *removal*; if it doesn't route through the same owner, "what exists in a room"
stops having one home.

## WHAT "GOOD" AIMS AT
`skills/balash-guide/references/design-principles.md`. Most load-bearing here: #9 (one enforced
place, now for a batch), #10/#12 (no `Series`/transaction/id type that owns no current rule), #1
(reuse the conflict definition already on `Booking`, don't re-derive it).

## PRESERVE / NON-GOALS
- Preserve Stage 1 behavior and its malformed-interval-throws-vs-conflict-returns-null distinction.
- NON-GOALS: editing/moving a booking, cancelling a whole series as a unit, series identity/linkage,
  persistence, availability search, auth. Design for the truth in front of you now.

## RETURN TO GUIDE
- Working code + `node --test` passing; key design decisions; result met|partially_met|invalidated|blocked.
- Run the subtractive pass before returning: name the present force behind every new type/guard/path;
  collapse the rest (especially any second enforcement path, rollback machinery, or booking id).

---

# Worker Handoff — Stage 3: waitlist with auto-promotion

## DESIGN GOAL (a quality outcome, not a feature)
Introduce a per-room waitlist as new state, and make **promotion an act of admission** so the
same-room no-overlap invariant keeps its single owner. The registry already owns "what is booked in
a room" through one atomic gate; the waitlist ("what is waiting for a room") must live with that same
owner, and a waitlisted request that gets promoted must become a real booking *through the existing
admission gate* — never by a separate write or a second conflict check. A reader auditing "can a
promotion ever create an overlap?" must land on the same one place that already guards booking.

How you represent a waiting request, where the queue lives, and how the caller learns of promotions
are yours to decide.

## BEHAVIOR IT MUST SATISFY
- A requester whose booking would be rejected (conflict) may instead join the waitlist for that
  room + interval. (Booking's own contract from Stages 1-2 is unchanged; joining is the requester's
  explicit choice.)
- On cancel, if the freed interval makes a waitlisted request no longer conflict with anything in
  that room, the earliest-queued compatible entry is promoted into a real booking and leaves the
  waitlist. The caller learns which entries were promoted.
- Cascade: if several become bookable at once, promote in queue (arrival) order, skipping any that
  still conflict — INCLUDING against entries just promoted in this same cancel.
- Everything from Stages 1-2 still holds.

## WHY NOW
Third capability. Promotion is the first path that creates a booking *without a direct caller* — it
is exactly where a second, unguarded write would silently break the invariant the product rests on.
The queue's arrival-order + skip-still-conflicting rule is a grounded product fact, not a freedom.

## WHAT "GOOD" AIMS AT
`skills/balash-guide/references/design-principles.md`. Most load-bearing: #9 (promotion routes
through the one enforced place), #2/#5/#10 (do NOT add a waiting-request type that only re-wraps a
booking's fields + overlap — that owns no rule the existing concept doesn't), #1 (reuse the conflict
definition, don't re-derive it for promotion).

## PRESERVE / NON-GOALS
- Preserve all Stage 1-2 behavior and the malformed-input-throws vs conflict-returns-null distinction.
- NON-GOALS: leaving/cancelling a waitlist entry, reading/listing the waitlist, priorities beyond
  arrival order, notifying the promoted requester out-of-band, promotion triggered by anything other
  than a cancel. Design for the truth in front of you now.

## RETURN TO GUIDE
- Working code + `node --test` passing; key design decisions; result met|partially_met|invalidated|blocked.
- Run the subtractive pass before returning: name the present force behind every new type/queue/return
  shape; collapse any waiting-request type that re-wraps Booking, and any promotion conflict check
  that duplicates the admission gate.

---

# Worker Handoff — Stage 4: capacity + per-person no-overlap

## DESIGN GOAL (a quality outcome, not a feature)
Enforce two new admission rules — room capacity and a per-person no-overlap rule — such that they hold
on EVERY path a booking comes into existence (single, all-or-nothing series, waitlist promotion) by
living at the ONE gate all those paths already funnel through, not re-checked per path. Adding these
rules should touch that single place, not three. Two truths to home:

- **Capacity** is a per-room fact (declared; undeclared = unlimited). Decide where a room's declared
  capacity lives and where "attendees must not exceed it" is enforced.
- **Per-person no-overlap is cross-room.** This breaks the standing assumption that the per-room
  grouping embodies — "different rooms never conflict" is no longer true (same person + overlapping
  time in two rooms is a conflict). The conflict definition can no longer be scoped by room; find it
  the right home so a single pairwise "do these two bookings clash?" answers both the same-room rule
  and the per-person rule, and the gate asks that question without re-deriving room/attendee logic
  itself.

How you represent attendees, where capacity is stored, and whether the conflict predicate moves onto
the booking are yours to decide.

## BEHAVIOR IT MUST SATISFY
- A way to declare a room's capacity; an undeclared room is unlimited.
- A booking specifies attendees as a list of person ids. Rejected if #attendees > room capacity.
- Rejected if any attendee already attends another booking whose interval overlaps this one, in ANY
  room (not only the same room). Half-open overlap as before (touching is fine).
- Both rules hold for a single booking, an all-or-nothing series (any occurrence violating => whole
  series rejected, nothing created), and an automatic waitlist promotion (a promotion that would
  violate either rule is skipped, not admitted).
- Everything from Stages 1-3 still holds. A booking with no attendees is valid (holds the room only).

## WHY NOW
Final capability. It is the direct test of whether the single-gate design pays off: two cross-cutting
rules should land in one place. The per-person rule also invalidates the per-room "no cross-room
conflict" assumption, so the conflict definition's home must be reconsidered — exactly the kind of
structural truth this method exists to keep honest.

## WHAT "GOOD" AIMS AT
`skills/balash-guide/references/design-principles.md`. Most load-bearing: #9 (both rules enforced at
the one place every path passes), #6 (a cross-cutting rule change should not be shotgun surgery
across paths), #1/#5 (the pairwise conflict decision belongs on the domain object, not asked-for data
the gate recombines), #4 (attendees/capacity get real representation, not re-validated ad hoc).

## PRESERVE / NON-GOALS / BOUNDARY
- Preserve all Stage 1-3 behavior and the precondition-throws vs conflict-returns-null distinction.
- BOUNDARY (non-speculative reading): promotion's TRIGGER stays as Stage 3 defined it — a cancel in
  room R scans room R's waitlist — but each promotion must now satisfy capacity + per-person too. Do
  NOT build a new cross-room promotion trigger (a cancel in room A hunting room B's waitlist because
  it freed a person); that is beyond the stated truth. Enforce the rules on promotion; don't widen
  the trigger.
- NON-GOALS: per-person capacity/quotas, attendee roles, editing attendees of an existing booking,
  reading the waitlist, persistence, auth.

## RETURN TO GUIDE
- Working code + `node --test` passing; key design decisions; result met|partially_met|invalidated|blocked.
- Run the subtractive pass: name the present force behind every new type/index/guard; collapse any
  per-path duplication of the new rules, and any index/type that owns no rule a scan/existing type
  doesn't already own.
