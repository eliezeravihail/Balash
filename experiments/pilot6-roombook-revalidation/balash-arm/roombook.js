/**
 * RoomBook — meeting-room booking core (stage 4: room capacity and the
 * person-overlap rule).
 *
 * Stage 4 adds the product's first CROSS-ROOM rule (person-overlap) and its
 * first non-cancel enabling event (a capacity raise). See ARCHITECTURE.md
 * (stage 4) for the full design and rationale.
 *
 * Single module owning the whole booking concept. Stage 4 has FOUR creation
 * rules plus two batch/queue invariants, each with exactly one owner
 * (ARCHITECTURE.md §3):
 *
 * - Input validity (interval, recurrence, attendees, capacity value): shared
 *   gates, one encoding per input kind, contractually ordered before the
 *   commit authority (§3.1). State-independent — a verdict never goes stale.
 * - Room no-overlap, capacity, person no-overlap: owned by the internal
 *   `commitBookings` — the only code path that creates bookings or writes to
 *   the store. All THREE creating paths route through it: `book`,
 *   `bookRecurring`, and waitlist promotion (a promotion is a real booking,
 *   offered to the same authority). Person no-overlap is the product's first
 *   CROSS-ROOM rule: the authority's conflict domain grows to the whole
 *   store, which its closure already holds — no second writer, no second
 *   encoding, no rule checked outside the authority (§3.4).
 * - All-or-nothing series creation: owned by the same `commitBookings`, by
 *   construction — the whole batch is proven bookable under ALL rules before
 *   anything is written; a rejected series leaves no observable trace.
 * - Quiescence (generalized): between public operations, no queued entry
 *   passes every creation rule. Owned by the internal `promoteWaitlist` —
 *   global at stage 4 — called from exactly one site per enabling event:
 *   `cancel` (frees a room interval AND every listed attendee's time, in any
 *   room) and `setCapacity` on a strict raise (§3.10).
 *
 * Time is integer minutes; intervals are half-open [start, end):
 * [10,20) and [20,30) do NOT conflict; identical intervals do. A person may
 * leave one meeting at minute 30 and start another at minute 30 (half-open
 * semantics apply to the person rule verbatim).
 *
 * Zero dependencies; in-memory state only; ES module.
 */

/**
 * A booking record as seen through the public seam.
 *
 * Records handed out by `schedule()` are frozen: they cannot be mutated, and
 * mutating the containing array does not affect the store.
 *
 * @typedef {Object} Booking
 * @property {string} id        Opaque id, unique across all rooms of one RoomBook
 *                              instance. Callers must not parse it or assume ordering.
 * @property {string} room      The room name as passed to `book()`.
 * @property {number} start     Inclusive start, integer minutes.
 * @property {number} end       Exclusive end, integer minutes; always > start.
 * @property {string} organizer Opaque label, stored and returned verbatim.
 */

/**
 * Thrown by `book()` and `bookRecurring()` when the requested interval is
 * malformed: `end <= start`, or either bound is not an integer (floats, NaN,
 * Infinity, and non-numbers all count as non-integers). It is one rule with
 * one gate: `bookRecurring` validates its base interval by exactly the same
 * predicate as `book` (ARCHITECTURE.md §3.3).
 *
 * Distinguish from a conflict via `instanceof` (or `err.name`).
 */
export class InvalidIntervalError extends Error {
  /** @param {string} message Human-readable reason in booking terms. */
  constructor(message) {
    super(message);
    this.name = 'InvalidIntervalError';
  }
}

/**
 * Thrown by `book()` and `bookRecurring()` when a requested interval —
 * already validated as well-formed — overlaps an existing booking in the same
 * room. For a series this means ANY occurrence conflicting, including with a
 * sibling occurrence of the same series (one conflict rule, one error type —
 * ARCHITECTURE.md §1, §4). Bookings in other rooms never cause this.
 *
 * Distinguish from invalid input via `instanceof` (or `err.name`).
 */
export class BookingConflictError extends Error {
  /** @param {string} message Human-readable reason in booking terms. */
  constructor(message) {
    super(message);
    this.name = 'BookingConflictError';
  }
}

/**
 * Thrown by `bookRecurring()` when the recurrence options are malformed:
 * `everyMinutes` or `count` missing, not an integer, or < 1 — including a
 * missing or non-object options argument. Distinct from `InvalidIntervalError`
 * (the times may be perfectly valid) and from `BookingConflictError` (no
 * conflict check has run yet — see the contractual check order in
 * ARCHITECTURE.md §3.3).
 *
 * Distinguish via `instanceof` (or `err.name`).
 */
export class InvalidRecurrenceError extends Error {
  /** @param {string} message Human-readable reason in booking terms. */
  constructor(message) {
    super(message);
    this.name = 'InvalidRecurrenceError';
  }
}

/**
 * Thrown by `cancel()` when the given id has no live booking in this
 * instance: the id was never issued, or its booking was already canceled
 * (ids are never reused, so a dead id stays dead forever). The two causes
 * are deliberately not distinguished (ARCHITECTURE.md §3.4).
 *
 * Distinguish via `instanceof` (or `err.name`).
 */
export class UnknownBookingError extends Error {
  /** @param {string} message Human-readable reason in booking terms. */
  constructor(message) {
    super(message);
    this.name = 'UnknownBookingError';
  }
}

/**
 * Thrown by `joinWaitlist()` when the requested interval does NOT currently
 * conflict with any booking in that room: joining is defined only as the
 * alternative to a conflicting booking request (GOALS.md recorded decision),
 * so for a free interval the correct act is `book()`, not joining — and this
 * error's caller act is exactly that. Nothing is queued.
 *
 * Deliberately NOT `BookingConflictError` — that type names the opposite
 * condition (a conflict exists); reusing it would invert its meaning at the
 * seam (ARCHITECTURE.md §4).
 *
 * Distinguish via `instanceof` (or `err.name`).
 */
export class NoConflictError extends Error {
  /** @param {string} message Human-readable reason in booking terms. */
  constructor(message) {
    super(message);
    this.name = 'NoConflictError';
  }
}

// ---- stage-4 error vocabulary ----------------------------------------------
//
// The four classes below are stage-4 seam vocabulary (ARCHITECTURE.md §4),
// exported alongside the five existing types (nine total, no shared base
// class). The grown surface is pinned exactly once, by T60 (the stage-3 T43
// surface pin is superseded — ARCHITECTURE.md §7).

/**
 * Thrown by `setCapacity()` when the capacity value is malformed: not an
 * integer, or negative (floats, NaN, Infinity, non-numbers, and missing
 * values all count as malformed). A failed declaration changes nothing —
 * the room's previous capacity state (declared value, or undeclared =
 * unlimited) stands.
 *
 * One name per malformed input kind, as everywhere in this taxonomy
 * (ARCHITECTURE.md §4): no interval is in sight (`InvalidIntervalError`
 * would lie) and nothing recurs (`InvalidRecurrenceError` would too).
 *
 * Distinguish via `instanceof` (or `err.name`).
 */
export class InvalidCapacityError extends Error {
  /** @param {string} message Human-readable reason in booking terms. */
  constructor(message) {
    super(message);
    this.name = 'InvalidCapacityError';
  }
}

/**
 * Thrown by `book()`, `bookRecurring()`, and `joinWaitlist()` when the
 * attendees argument is malformed: present but not an array, or an array
 * containing duplicate ids (SameValueZero — a person cannot attend twice; a
 * duplicate is a caller bug, and this seam signals caller bugs). One rule,
 * one gate (`assertValidAttendees`) for all three operations, exactly like
 * the interval gate (ARCHITECTURE.md §3.1).
 *
 * The elements themselves are NOT type-checked: person ids are opaque labels
 * like organizer/requester — validating them would be the first brick of the
 * person registry GOALS excludes.
 *
 * Distinguish via `instanceof` (or `err.name`).
 */
export class InvalidAttendeesError extends Error {
  /** @param {string} message Human-readable reason in booking terms. */
  constructor(message) {
    super(message);
    this.name = 'InvalidAttendeesError';
  }
}

/**
 * Thrown by `book()` and `bookRecurring()` when the attendee count exceeds
 * the room's declared capacity (`count > capacity`; `count === capacity` is
 * allowed; an undeclared room is unlimited and never throws this). For a
 * series the check is batch-level — one room, one list — so the whole series
 * stands or falls together (all-or-nothing, ARCHITECTURE.md §3.3, §3.5).
 *
 * Deliberately NOT `BookingConflictError`: that type's caller act — wait it
 * out or join the waitlist — is wrong here (joining needs a room conflict,
 * and waiting cures nothing but a capacity raise). The caller act for THIS
 * type is: bring fewer people, or choose another room. The message carries
 * the declared capacity and the offending count (there is no capacity read
 * operation; rejection messages are where a human learns the number).
 *
 * Distinguish via `instanceof` (or `err.name`).
 */
export class CapacityExceededError extends Error {
  /** @param {string} message Human-readable reason in booking terms. */
  constructor(message) {
    super(message);
    this.name = 'CapacityExceededError';
  }
}

/**
 * Thrown by `book()` and `bookRecurring()` when any listed attendee already
 * has an overlapping live booking in ANY room — the product's first
 * cross-room rule (half-open semantics: touching meetings may share an
 * attendee). In the SAME room an overlapping interval is already a room
 * conflict and reports as `BookingConflictError` first (contractual check
 * order, ARCHITECTURE.md §3.6), so this type is in practice the cross-room
 * answer.
 *
 * Deliberately NOT `BookingConflictError`: changing rooms always cures a
 * room conflict and never cures this one; a caller's uniform room-conflict
 * handler would misroute it twice over (the room may even be free, so
 * `joinWaitlist` may not be available). The caller act here is: drop the
 * busy attendee, or move the time.
 *
 * Distinguish via `instanceof` (or `err.name`).
 */
export class PersonConflictError extends Error {
  /** @param {string} message Human-readable reason in booking terms. */
  constructor(message) {
    super(message);
    this.name = 'PersonConflictError';
  }
}

// ---- confined internals shared by every instance (stateless) ---------------

/**
 * THE half-open overlap predicate: [aStart, aEnd) and [bStart, bEnd) overlap
 * iff `aStart < bEnd && bStart < aEnd`. The conflict rule's single encoding
 * (ARCHITECTURE.md §5): every overlap question goes through this one function
 * — `commitBookings`' batch-vs-batch leg directly, and the store-conflict
 * query `roomHasConflict` (which serves `commitBookings`' batch-vs-store leg
 * and `joinWaitlist`'s gate) — so the rule cannot drift.
 * Internal only; not exported.
 */
function overlaps(aStart, aEnd, bStart, bEnd) {
  return aStart < bEnd && bStart < aEnd;
}

/**
 * The interval-validity gate, shared by all three interval-taking operations
 * — `book`, `bookRecurring`, and `joinWaitlist` (two creating paths and one
 * non-creating one) — so the rule has one encoding (ARCHITECTURE.md §3.3
 * step 1, §3.5 step 1): `start` and `end` must be integers with
 * `start < end`; otherwise `InvalidIntervalError`. Negative integers are
 * valid times. Internal only; not exported.
 *
 * @throws {InvalidIntervalError}
 */
function assertValidInterval(room, start, end) {
  if (!Number.isInteger(start) || !Number.isInteger(end) || !(start < end)) {
    throw new InvalidIntervalError(
      `Invalid interval for room ${String(room)}: an interval must run over ` +
      `whole minutes with its start before its end, but ` +
      `[${String(start)}, ${String(end)}) does not.`
    );
  }
}

/**
 * The attendees gate (stage 4), shared by the same three operations the
 * interval gate serves — `book`, `bookRecurring`, `joinWaitlist` — so the
 * rule has one encoding (ARCHITECTURE.md §3.1): omitted (`undefined`) means
 * the empty list; otherwise the value must be an array with no duplicate
 * elements (SameValueZero), else `InvalidAttendeesError`. Elements are
 * opaque and not type-checked (§2 — no person registry).
 *
 * Returns the validated FROZEN COPY the caller hands onward: validation and
 * the copy-at-the-seam defense are one act, so an unvalidated or
 * caller-aliased list cannot exist inside (the caller keeps ownership of the
 * array it passed; mutating it later changes nothing here).
 *
 * Contractual position: the LAST validity gate on every path — after the
 * interval gate, and after the recurrence gate on `bookRecurring` (§3.6).
 * Wired into all three interval-taking operations. Internal only; never
 * exported.
 *
 * @param {string} room For the error message only.
 * @param {readonly string[] | undefined} attendees As passed at the seam.
 * @returns {readonly string[]} Frozen validated copy (fresh; empty if omitted).
 * @throws {InvalidAttendeesError}
 */
function assertValidAttendees(room, attendees) {
  if (attendees === undefined) return Object.freeze([]);
  if (!Array.isArray(attendees) || new Set(attendees).size !== attendees.length) {
    throw new InvalidAttendeesError(
      `Invalid attendees for room ${String(room)}: attendees must be a list ` +
      `of person ids with no id listed twice.`
    );
  }
  return Object.freeze(attendees.slice());
}

/**
 * Create an independent, empty RoomBook.
 *
 * All state lives in this closure — the booking store, the per-room declared
 * capacities, AND the ONE global waitlist queue; each call returns a fully
 * isolated instance (bookings, capacities, and waitlist entries in one are
 * invisible to another). The returned object is frozen and exposes exactly
 * `book`, `bookRecurring`, `schedule`, `cancel`, `joinWaitlist`, and
 * `setCapacity`; all are freely detachable (no `this` dependence).
 *
 * @returns {{
 *   book: (room: string, start: number, end: number, organizer: string,
 *          attendees?: readonly string[]) => string,
 *   bookRecurring: (room: string, start: number, end: number, organizer: string,
 *                   recurrence: { everyMinutes: number, count: number },
 *                   attendees?: readonly string[]) => string[],
 *   schedule: (room: string) => Booking[],
 *   cancel: (bookingId: string) => undefined,
 *   joinWaitlist: (room: string, start: number, end: number, requester: string,
 *                  attendees?: readonly string[]) => undefined,
 *   setCapacity: (room: string, capacity: number) => undefined,
 * }}
 */
export function createRoomBook() {
  // ---- confined internals (ARCHITECTURE.md §5) -----------------------------
  const bookingsByRoom = new Map(); // Map<string, InternalBooking[]>, append order.
                                    // InternalBooking = frozen {id, room, start,
                                    // end, organizer, attendees: frozen string[]};
                                    // the attendee list's ONE home. schedule()
                                    // mints the public five-field record (§5).
  const capacityByRoom = new Map(); // Map<string, number>, declared finite ints
                                    // only; keyed lazily, ONLY by setCapacity.
                                    // "unlimited" is KEY ABSENCE — never Infinity.
  const waitlist = [];              // ONE global queue in join order; entries are
                                    // {room, start, end, requester, attendees}.
                                    // Append = join; walk = join order (§5).
                                    // Plain unfrozen objects (they never cross the
                                    // seam), but `attendees` is the gate's frozen
                                    // seam-copy, so post-join mutation cannot reach
                                    // it. Each entry carries its room (no map key).
  let nextIdNumber = 1;             // instance-wide counter -> "bk-<n>", never reused

  /**
   * The store-conflict query (ARCHITECTURE.md §5): does [start, end) overlap
   * any live booking in `room` right now? The ONE encoding of that question,
   * built on the one `overlaps()` predicate. Read-only: never writes, never
   * throws. Exactly two askers — `commitBookings`' batch-vs-store leg and
   * `joinWaitlist`'s conflict-required gate (§3.5 step 2). Promotion does NOT
   * ask it: creating paths ask the authority by asking it to commit (§3.1,
   * §3.6). Internal only; not exported.
   *
   * @param {string} room
   * @param {number} start
   * @param {number} end
   * @returns {boolean}
   */
  function roomHasConflict(room, start, end) {
    const existing = bookingsByRoom.get(room);
    if (existing === undefined) return false;
    return existing.some((b) => overlaps(start, end, b.start, b.end));
  }

  /**
   * The ONE encoding of "undeclared = unlimited" (ARCHITECTURE.md §3.3, §5):
   * a room's effective capacity is its declared value, or `Infinity` when no
   * capacity was ever declared (key absence). Read-only, never throws. Exactly
   * two askers — the authority's capacity leg (`commitBookings`) and
   * `setCapacity`'s raise detection. Internal only; not exported.
   *
   * @param {string} room
   * @returns {number} The declared finite integer, or `Infinity`.
   */
  function effectiveCapacity(room) {
    const declared = capacityByRoom.get(room);
    return declared === undefined ? Infinity : declared;
  }

  /**
   * The person-overlap query (ARCHITECTURE.md §3.4, §5): does any id in
   * `attendees` appear on a live booking that overlaps [start, end) in ANY
   * room? The product's first cross-room read — built on the one `overlaps()`
   * predicate, walking the whole store the authority's closure holds. Its SOLE
   * asker is the authority's person leg; it is deliberately unavailable to the
   * non-creating join path (person-overlap is not a join gate, §3.8).
   * Read-only: never writes, never throws. Internal only; not exported.
   *
   * @param {readonly string[]} attendees The batch's attendee ids (frozen copy).
   * @param {number} start
   * @param {number} end
   * @returns {boolean}
   */
  function personConflictsAnywhere(attendees, start, end) {
    if (attendees.length === 0) return false; // no ids to clash — common case
    const ids = new Set(attendees);
    for (const roomBookings of bookingsByRoom.values()) {
      for (const b of roomBookings) {
        if (!overlaps(start, end, b.start, b.end)) continue;
        for (const a of b.attendees) {
          if (ids.has(a)) return true;
        }
      }
    }
    return false;
  }

  /**
   * The single writer (ARCHITECTURE.md §3): the ONLY code path that mints
   * ids, creates records, or writes to the store — and the sole enforcer of
   * the THREE state rules (room no-overlap, capacity, person no-overlap). All
   * THREE creating paths route through it: `book` (batch of one),
   * `bookRecurring` (the expanded batch), and waitlist promotion (a batch of
   * one per queued entry). Every creation therefore meets every state rule by
   * construction — to create is to ask the authority (§3).
   *
   * Check-everything-then-commit, so all-or-nothing holds by construction and
   * no rollback path exists (§3.5). Check order (§3.6):
   *   4. Capacity — batch-level (one room, one list), before any interval
   *      scanning: `attendees.length > effectiveCapacity(room)` →
   *      `CapacityExceededError` (a time-independent verdict, reported ahead of
   *      any timing accident).
   *   5. Per occurrence, in order: room-vs-store, then room-vs-batch (both
   *      `BookingConflictError`), THEN person-vs-store (`PersonConflictError`).
   *      Room reports before person, so a same-room person clash always
   *      surfaces as a room conflict (§3.4 subsumption). No person batch-vs-
   *      batch leg — provably redundant while batches are single-room/single-
   *      list (§3.4 lemma): personConflictsAnywhere scans only the committed
   *      store, never this uncommitted batch.
   * Any hit throws before ANY write (no id minted, no record created, no room
   * key created). The commit loop that follows cannot fail.
   *
   * Callers gate their own inputs first (§3.1): every occurrence handed in is
   * already a valid integer interval, and `attendees` is the shared gate's
   * validated frozen copy.
   *
   * @param {string} room
   * @param {Array<{start: number, end: number}>} occurrences In occurrence order.
   * @param {string} organizer
   * @param {readonly string[]} attendees Validated frozen list (empty allowed).
   * @returns {string[]} Fresh array of new ids, `ids[i]` for `occurrences[i]`.
   * @throws {CapacityExceededError} iff the attendee count exceeds the room's
   *                    declared capacity; the store is untouched.
   * @throws {BookingConflictError} iff any occurrence overlaps an existing
   *                    booking in `room` or an earlier occurrence of the
   *                    batch; the store is untouched.
   * @throws {PersonConflictError} iff any occurrence's attendees overlap a
   *                    live booking of the same person in ANY room; untouched.
   */
  function commitBookings(room, occurrences, organizer, attendees) {
    // Capacity — batch-level, before any interval scanning (§3.3, §3.6 step 4).
    // An undeclared room is unlimited, so the empty list passes every capacity.
    const capacity = effectiveCapacity(room);
    if (attendees.length > capacity) {
      throw new CapacityExceededError(
        `Cannot book room ${String(room)}: it holds ${capacity}, but the ` +
        `booking lists ${attendees.length} attendees.`
      );
    }

    // Check the ENTIRE batch before the first write (§3.5, §3.6 step 5). The
    // batch-vs-store leg delegates to the one store-conflict query; the
    // batch-vs-batch leg checks earlier occurrences of this same batch; the
    // person leg scans the whole store through the one person query.
    for (let i = 0; i < occurrences.length; i += 1) {
      const occ = occurrences[i];
      if (roomHasConflict(room, occ.start, occ.end)) {
        // The message names the colliding occurrence for humans (§4); for a
        // batch of one it is byte-identical to the stage-1 book() message.
        const target = occurrences.length === 1
          ? `for [${occ.start}, ${occ.end})`
          : `for occurrence ${i} of the series, [${occ.start}, ${occ.end})`;
        throw new BookingConflictError(
          `Cannot book room ${String(room)} ${target}: ` +
          `it overlaps an existing booking in that room.`
        );
      }
      for (let j = 0; j < i; j += 1) {
        const earlier = occurrences[j];
        if (overlaps(occ.start, occ.end, earlier.start, earlier.end)) {
          throw new BookingConflictError(
            `Cannot book room ${String(room)}: occurrence ${i} of the series, ` +
            `[${occ.start}, ${occ.end}), overlaps occurrence ${j}, ` +
            `[${earlier.start}, ${earlier.end}), of the same series.`
          );
        }
      }
      // Person-vs-store overlap — AFTER the room legs (§3.6), so a same-room
      // person clash reports as a room conflict first (§3.4 subsumption).
      if (personConflictsAnywhere(attendees, occ.start, occ.end)) {
        const target = occurrences.length === 1
          ? `[${occ.start}, ${occ.end})`
          : `occurrence ${i} of the series, [${occ.start}, ${occ.end}),`;
        throw new PersonConflictError(
          `Cannot book room ${String(room)} for ${target}: a listed attendee ` +
          `already has an overlapping booking in another room.`
        );
      }
    }

    // Commit — the whole batch is proven bookable; nothing can fail below.
    let roomBookings = bookingsByRoom.get(room);
    if (roomBookings === undefined) {
      roomBookings = [];
      bookingsByRoom.set(room, roomBookings); // lazy key creation, on commit only
    }
    const ids = [];
    for (const occ of occurrences) {
      const id = `bk-${nextIdNumber}`;
      nextIdNumber += 1;
      roomBookings.push(
        // The frozen attendee list is stamped on the internal record — its one
        // home (§5); it never leaves via schedule().
        Object.freeze({ id, room, start: occ.start, end: occ.end, organizer, attendees })
      );
      ids.push(id);
    }
    return ids;
  }

  /**
   * Book `room` for the half-open interval [start, end).
   *
   * Rooms need no prior creation — any room name is a room. `room` and
   * `organizer` are opaque: not validated, not interpreted; `room` is used
   * only as an identity key (string equality).
   *
   * Check order is contractual: validity first, then conflict, then commit —
   * an invalid interval is reported as invalid even if it would also conflict,
   * and a rejected call writes nothing (no observable trace: a later
   * non-overlapping `book` succeeds and `schedule` is unchanged).
   *
   * @param {string} room      Room name (identity key; any string).
   * @param {number} start     Inclusive start, integer minutes (any integer,
   *                           negatives allowed).
   * @param {number} end       Exclusive end, integer minutes; must be > start.
   * @param {string} organizer Opaque label, stored verbatim.
   * @returns {string} The new booking's opaque id, unique across all rooms of
   *                   this instance.
   * @throws {InvalidIntervalError} iff `end <= start`, or `start` or `end` is
   *                   not an integer (`Number.isInteger` is the gate).
   * @throws {BookingConflictError} iff the interval is well-formed and overlaps
   *                   an existing booking in the SAME room, where [a,b) and
   *                   [c,d) overlap iff `a < d && c < b`.
   */
  function book(room, start, end, organizer, attendees = []) {
    // 1. Interval validity (before the authority — contractual order, §3.6).
    assertValidInterval(room, start, end);
    // 2. Attendees validity — the shared gate validates AND copies at the seam,
    // returning the frozen list the authority stamps on the record (§3.1).
    const validated = assertValidAttendees(room, attendees);
    // 3. Capacity + conflicts + commit: the single writer, batch of one (§3.6).
    return commitBookings(room, [{ start, end }], organizer, validated)[0];
  }

  /**
   * Book a recurring series in `room`: `count` occurrences, occurrence i at
   * [start + i*everyMinutes, end + i*everyMinutes) for i in 0..count-1.
   *
   * ALL-OR-NOTHING: if ANY occurrence conflicts — with an existing booking in
   * `room`, or with another occurrence of this same series (e.g. a stride
   * shorter than the duration) — the whole series is rejected and NOTHING is
   * booked: `schedule(room)` is identical to before the call, no id is
   * minted, and every slot any occurrence would have taken is still bookable.
   * (Owned by the internal commit path by construction: the full batch is
   * checked before anything is written — ARCHITECTURE.md §3.2.)
   *
   * On success every occurrence is an ORDINARY booking: it appears in
   * `schedule(room)` as its own frozen Booking record with its own id and is
   * individually cancelable. No series identity survives this call — nothing
   * links the occurrences afterward.
   *
   * Check order is contractual (ARCHITECTURE.md §3.3): interval validity
   * first, then recurrence validity, then conflicts, then commit. An input
   * that is invalid in more than one way reports the earliest gate's error.
   *
   * A `count` of 1 is a valid degenerate series equivalent to a single
   * `book()` (one booking, an id array of length 1). `everyMinutes` equal to
   * the duration (`end - start`) yields touching, non-conflicting occurrences
   * (half-open intervals).
   *
   * @param {string} room       Room name (identity key; any string). The whole
   *                            series lives in this one room; other rooms are
   *                            never consulted or affected.
   * @param {number} start      Inclusive start of occurrence 0, integer
   *                            minutes (any integer, negatives allowed).
   * @param {number} end        Exclusive end of occurrence 0, integer minutes;
   *                            must be > start.
   * @param {string} organizer  Opaque label, stored verbatim on every
   *                            occurrence.
   * @param {{ everyMinutes: number, count: number }} recurrence
   *                            Stride and occurrence count. Both must be
   *                            integers >= 1. Only these two properties are
   *                            read; extras are ignored.
   * @returns {string[]} A fresh, caller-owned array of the new bookings' ids
   *                     in occurrence order (`ids[i]` is occurrence i's id);
   *                     length === `count`. Ids are opaque, unique across all
   *                     rooms of this instance, never reused.
   * @throws {InvalidIntervalError}   iff `end <= start`, or `start` or `end`
   *                     is not an integer (`Number.isInteger` is the gate).
   *                     Checked FIRST — reported even if the recurrence is
   *                     also malformed or the series would also conflict.
   * @throws {InvalidRecurrenceError} iff the interval is well-formed and
   *                     `recurrence` is not an object with integer
   *                     `everyMinutes >= 1` and integer `count >= 1`.
   *                     Checked before any conflict detection.
   * @throws {BookingConflictError}   iff inputs are valid and any occurrence
   *                     overlaps an existing booking in `room` or an earlier
   *                     occurrence of this series ([a,b) and [c,d) overlap
   *                     iff `a < d && c < b`). Nothing is booked.
   */
  function bookRecurring(room, start, end, organizer, recurrence, attendees = []) {
    // 1. Interval validity — contractual FIRST gate, same rule and same gate
    // as book() (ARCHITECTURE.md §3.6 step 1).
    assertValidInterval(room, start, end);

    // 2. Recurrence validity — integers, both >= 1; a missing or non-object
    // options argument fails the same gate (§3.6 step 2).
    if (recurrence === null || typeof recurrence !== 'object' ||
        !Number.isInteger(recurrence.everyMinutes) || recurrence.everyMinutes < 1 ||
        !Number.isInteger(recurrence.count) || recurrence.count < 1) {
      throw new InvalidRecurrenceError(
        `Cannot book a recurring series in room ${String(room)}: the recurrence ` +
        `options must be an object with integer everyMinutes >= 1 and integer ` +
        `count >= 1.`
      );
    }
    const { everyMinutes, count } = recurrence;

    // 3. Attendees validity — the LAST validity gate, after interval and
    // recurrence (§3.6 step 3); validates AND copies at the seam.
    const validated = assertValidAttendees(room, attendees);

    // 4. Expand the series; capacity, conflicts, and commit happen in the
    // single writer (§3.5, §3.6).
    const occurrences = [];
    for (let i = 0; i < count; i += 1) {
      occurrences.push({
        start: start + i * everyMinutes,
        end: end + i * everyMinutes,
      });
    }
    return commitBookings(room, occurrences, organizer, validated);
  }

  /**
   * The quiescence owner (ARCHITECTURE.md §3.10): global and unparameterized —
   * the ONLY code that removes entries from the queue and the ONLY code that
   * turns entries into bookings. Called from exactly TWO sites, one per
   * enabling event — `cancel` step 3 (a cancel frees a room interval AND every
   * listed attendee, in any room) and `setCapacity` step 3 (on a strict
   * raise). No other caller (the audit is a grep of these two).
   *
   * Walks the ONE global queue in JOIN ORDER and OFFERS every entry to the
   * commit authority — `commitBookings` with a batch of one — inside a
   * try/catch: on acceptance the entry is spliced out (its booking now exists,
   * ordinary in every respect); on any of the authority's three state-rule
   * answers — `BookingConflictError`, `CapacityExceededError`,
   * `PersonConflictError` — the entry stays queued and the walk continues.
   * NOTHING else is caught: the three types are ENUMERATED (no base type), so
   * a future fourth rule must appear here consciously (§4); any other error
   * propagates (none exists by construction — validity was settled at join).
   *
   * OFFER EVERY entry, never an "affected" subset (§3.10): eligibility is
   * decided in exactly one place — the authority — so a filter/authority drift
   * bug is structurally inexpressible.
   *
   * ONE pass in global join order is the fixpoint (§3.10, monotonicity): within
   * a pass the store only grows and capacities do not change, and every state
   * rule is monotone in the store, so an entry rejected at its turn stays
   * rejected. No repeat scan, no worklist. Cross-room competition for one
   * person resolves for free: the earlier GLOBAL join is offered first and
   * promotes; the later then person-conflicts with the just-minted booking.
   *
   * @returns {undefined}
   */
  function promoteWaitlist() {
    let i = 0;
    while (i < waitlist.length) {
      const entry = waitlist[i];
      try {
        // Offer to the authority — exactly as book() would (§3.1): no
        // promotion-specific check, no promotion-specific write. The id is
        // minted inside commitBookings, at promotion time, in promotion order,
        // by the same instance-wide counter. The entry's frozen attendees list
        // is what the authority stamps on the new record.
        commitBookings(
          entry.room, [{ start: entry.start, end: entry.end }],
          entry.requester, entry.attendees
        );
      } catch (err) {
        if (err instanceof BookingConflictError ||
            err instanceof CapacityExceededError ||
            err instanceof PersonConflictError) {
          i += 1; // the authority said no: the entry stays queued
          continue;
        }
        throw err; // catch NOTHING else (enumerated, no base type — §4)
      }
      waitlist.splice(i, 1); // promoted: the entry leaves the queue permanently
    }
    return undefined;
  }

  /**
   * Cancel the live booking with id `bookingId`, removing exactly that
   * booking from its room's schedule — and then restore quiescence GLOBALLY
   * (ARCHITECTURE.md §3.7).
   *
   * Contractual order (ARCHITECTURE.md §3.7): locate, remove, promote.
   *
   * PROMOTION (stage 4, GLOBAL): a cancel frees the room interval AND every
   * listed attendee's time, and a freed person can be the only obstacle of a
   * queued entry in ANY room — so after removal the ONE global waitlist is
   * examined in JOIN ORDER, and EVERY entry that now passes all four creation
   * rules (interval free in its room, capacity, person-overlap) is promoted:
   * it becomes a real, ordinary booking — created through the same commit
   * authority as `book()`, with a fresh never-reused id, a frozen
   * stage-1-shape record, and `organizer` set to the entry's requester label —
   * and the entry leaves the queue permanently. Entries that still fail any
   * rule — including against bookings created by EARLIER promotions of this
   * same cancel — stay queued unchanged (of two competing compatible entries,
   * the earlier GLOBAL join wins). One pass in join order is exhaustive under
   * the monotonicity lemma (§3.10). Promotions are observed via `schedule()`;
   * there is no notification and the promoted ids are not returned (GOALS.md
   * non-goal).
   *
   * With an empty or all-incompatible waitlist, cancel behaves exactly as
   * stage 2: the freed slot simply stays free and immediately rebookable,
   * including by the IDENTICAL interval. All other bookings — other rooms,
   * other bookings in the same room, and sibling occurrences of a former
   * recurring series — are untouched. A promoted booking is cancelable like
   * any other, and canceling IT re-triggers promotion the same way.
   *
   * An id with no live booking is a distinguishable error, never a silent
   * no-op (GOALS.md recorded decision): ids originate only from this
   * instance, so a dead id means a caller bug or a double-cancel. Ids are
   * never reused, so an already-canceled id stays dead forever. On this
   * error nothing at all happens: no removal and NO promotion pass —
   * waitlists are untouched.
   *
   * @param {string} bookingId An id previously returned by `book()` or
   *                    `bookRecurring()` of THIS instance (including ids of
   *                    promoted bookings). Not shape-validated: any value
   *                    that is not a live booking's id — wrong type included
   *                    — is uniformly unknown.
   * @returns {undefined} Nothing on success (the caller already holds the id;
   *                    promotions are observed via `schedule()` — returning
   *                    promoted ids was rejected, ARCHITECTURE.md §2).
   * @throws {UnknownBookingError} iff no live booking has this id: never
   *                    issued by this instance, or already canceled. The two
   *                    causes are deliberately not distinguished
   *                    (ARCHITECTURE.md §3.4). Store and waitlists unchanged.
   */
  function cancel(bookingId) {
    // 1. Locate — linear scan of the store; no id index (ARCHITECTURE.md §5).
    for (const [room, roomBookings] of bookingsByRoom.entries()) {
      for (let i = 0; i < roomBookings.length; i += 1) {
        if (roomBookings[i].id === bookingId) {
          // 2. Remove — splice exactly this one record (§3.4). The only code
          // that deletes; removal only shrinks the set, so it cannot
          // introduce an overlap (§3.1).
          roomBookings.splice(i, 1);
          // 3. Restore quiescence — the GLOBAL pass (§3.7 step 3, §3.10). A
          // cancel frees the room interval AND every listed attendee, and a
          // freed person can enable a queued entry in ANY room, so the
          // restoration is instance-wide, not scoped to `room`.
          promoteWaitlist();
          return undefined;
        }
      }
    }
    // No live booking has this id: never issued, or already canceled (ids are
    // never reused). Deliberately not distinguished (§3.4); store unchanged.
    throw new UnknownBookingError(
      `Cannot cancel booking ${String(bookingId)}: no booking with this id is ` +
      `live in this room-book (it was never issued, or was already canceled).`
    );
  }

  /**
   * Report `room`'s bookings ordered by ascending `start`.
   *
   * The ordering is total within a room: two same-room bookings can never
   * share a start (equal starts always overlap, so the second was rejected).
   *
   * @param {string} room Room name (identity key; any string).
   * @returns {Booking[]} A NEW array per call of frozen Booking records,
   *                   sorted by `start`. A room with no bookings — including a
   *                   name never seen before — yields `[]`, never an error.
   *                   Mutating the array does not affect the store; the
   *                   records themselves are immutable.
   */
  function schedule(room) {
    // Fresh array per call. schedule() MINTS the public five-field record from
    // each internal record (§2, §5): the internal record carries a private
    // `attendees` list, which never leaves via the seam — so the public record
    // is a fresh frozen {id, room, start, end, organizer}, exactly the stage-1
    // shape. Absent key and empty array both yield [].
    const existing = bookingsByRoom.get(room);
    if (existing === undefined) return [];
    return existing
      .slice()
      .sort((a, b) => a.start - b.start)
      .map((b) => Object.freeze({
        id: b.id, room: b.room, start: b.start, end: b.end, organizer: b.organizer,
      }));
  }

  /**
   * Join the waitlist for `room` over the half-open interval [start, end) —
   * the explicit alternative to a booking request that conflicts RIGHT NOW
   * (ARCHITECTURE.md §3.5).
   *
   * The entry records the room, the interval, `requester` (an opaque label,
   * exactly like `organizer` — stored verbatim, never validated), and the
   * frozen seam-copy of its attendee list (promotion mints a real booking,
   * which needs it). The ONE global queue is invisible: it cannot be inspected
   * or left (GOALS.md non-goals), and entries never appear in `schedule()`. An
   * entry becomes observable only by PROMOTION: when an enabling event (any
   * cancel, in any room, or a strict capacity raise) leaves it passing all
   * four creation rules, it becomes a real, ordinary booking with `organizer`
   * = `requester` (see `cancel()`), and leaves the queue permanently.
   *
   * Contractual order (ARCHITECTURE.md §3.5) mirrors the booking paths:
   *
   * 1. Interval validity — the SAME rule through the SAME gate as `book()`:
   *    integers with `start < end`, else `InvalidIntervalError`. An interval
   *    that is malformed AND would not conflict reports the validity error
   *    (validity first, as on every path).
   * 2. Conflict REQUIRED — if [start, end) does not overlap any live booking
   *    in `room`, throw `NoConflictError`: joining is defined only as the
   *    alternative to a conflicting request (GOALS.md decision); a free
   *    interval should simply be booked. The test is the same single
   *    encoding of the conflict question the commit authority uses.
   * 3. Enqueue — append the entry at the queue's tail. Join order is
   *    contractual: promotion examines entries in join order.
   *
   * A rejected join (either error) leaves NO trace: nothing queued, nothing
   * booked, `schedule()` unchanged. Duplicate entries are permitted (no
   * stated rule): each successful join queues independently; after one of
   * two identical entries promotes, the other conflicts with the new booking
   * and stays queued.
   *
   * Between public operations, no queued entry could be successfully booked
   * (the quiescence invariant, GOALS.md): entries are born incompatible
   * (step 2), and cancellation immediately promotes everything compatible.
   *
   * @param {string} room      Room name (identity key; any string). Rooms
   *                    need no prior creation; waitlists are per-room and
   *                    fully independent, like bookings.
   * @param {number} start     Inclusive start, integer minutes (any integer,
   *                    negatives allowed).
   * @param {number} end       Exclusive end, integer minutes; must be > start.
   * @param {string} requester Opaque label, stored verbatim; becomes the
   *                    promoted booking's `organizer`.
   * @returns {undefined} Nothing on success. No entry handle/ticket is
   *                    returned: no operation consumes one (no leave, no
   *                    inspect — GOALS.md non-goals), and the eventual
   *                    booking's id cannot exist before it is committed
   *                    (ARCHITECTURE.md §2, the seam-trap decision).
   * @throws {InvalidIntervalError} iff `end <= start`, or `start` or `end` is
   *                    not an integer (`Number.isInteger` is the gate) —
   *                    checked FIRST, reported even if the interval would
   *                    also fail the conflict-required gate.
   * @throws {NoConflictError} iff the interval is well-formed and does NOT
   *                    overlap any live booking in `room` ([a,b) and [c,d)
   *                    overlap iff `a < d && c < b`): the interval is
   *                    bookable, so book it instead. Nothing is queued.
   */
  function joinWaitlist(room, start, end, requester, attendees = []) {
    // 1. Interval validity — the SAME gate as the booking paths, checked
    // FIRST (contractual order, §3.8 step 1).
    assertValidInterval(room, start, end);
    // 2. Attendees validity — the SAME shared gate as the booking paths; the
    // entry's list is validated AND copied here, at join (§3.8 step 2). This
    // is the only place: validity is state-independent, and promotion must
    // never be the first to discover a malformed list.
    const validated = assertValidAttendees(room, attendees);
    // 3. Conflict REQUIRED — the same single encoding of the store-conflict
    // question the commit authority's store leg uses (§3.8 step 3); a
    // non-creating path may ask the query (§3.1). Capacity and person-overlap
    // are deliberately NOT join gates — both can change before promotion.
    if (!roomHasConflict(room, start, end)) {
      throw new NoConflictError(
        `Cannot join the waitlist for room ${String(room)} over ` +
        `[${String(start)}, ${String(end)}): no current booking conflicts ` +
        `with that interval — book it directly instead.`
      );
    }
    // 4. Enqueue — append to the ONE global queue (append = global join order,
    // which promotion walks). The entry carries its room (no map key) and the
    // frozen seam-copy of its attendees. A rejected join above leaves no trace.
    waitlist.push({ room, start, end, requester, attendees: validated });
    return undefined;
  }

  /**
   * Declare `room`'s capacity — the maximum attendee count a booking of that
   * room may carry at creation time (ARCHITECTURE.md §3.9). `room` is opaque
   * as everywhere; no registry, no existence check — declaring is what makes a
   * room *declared*. An undeclared room is unlimited.
   *
   * Three contractual steps:
   *
   * 1. Capacity validity — an integer `>= 0`, else `InvalidCapacityError`;
   *    nothing changes on rejection.
   * 2. Write — record the value (overwrite on re-declare; lazy key). Lowering
   *    or re-declaring equal does nothing further: capacity is a creation-time
   *    gate, so NO eviction of standing bookings.
   * 3. If the effective capacity STRICTLY increased — restore quiescence via
   *    the global `promoteWaitlist()` (the same pass `cancel` calls). A raise
   *    is an enabling event; a lower/equal only tightens, and quiescence held
   *    before the call, so a pass would be dead code. Declaring a capacity on
   *    an undeclared room is never a raise (old effective was `Infinity`), so a
   *    first declaration never promotes.
   *
   * @param {string} room     Room name (identity key; any string).
   * @param {number} capacity Integer `>= 0`.
   * @returns {undefined} Nothing on success (the cancel precedent: success
   *                    needs no payload; there is no capacity read operation).
   * @throws {InvalidCapacityError} iff `capacity` is not an integer `>= 0`
   *                    (floats, NaN, Infinity, non-numbers, negatives). The
   *                    room's previous capacity state stands unchanged.
   */
  function setCapacity(room, capacity) {
    // 1. Capacity validity — inline gate, one caller (§3.1, §3.9 step 1).
    if (!Number.isInteger(capacity) || capacity < 0) {
      throw new InvalidCapacityError(
        `Cannot set capacity for room ${String(room)}: a capacity must be a ` +
        `whole number of people that is zero or more, but ` +
        `${String(capacity)} is not.`
      );
    }
    // 2. Write — overwrite on re-declare. `effectiveCapacity` read BEFORE the
    // write gives the old effective value for raise detection (§3.9 step 2).
    const previous = effectiveCapacity(room);
    capacityByRoom.set(room, capacity); // the capacity store's only writer
    // 3. Restore quiescence iff the effective capacity STRICTLY increased
    // (§3.9 step 3). A first declaration (previous === Infinity) is never a
    // raise; a lower/equal re-declaration enables nothing.
    if (capacity > previous) {
      promoteWaitlist();
    }
    return undefined;
  }

  return Object.freeze({
    book, bookRecurring, schedule, cancel, joinWaitlist, setCapacity,
  });
}
