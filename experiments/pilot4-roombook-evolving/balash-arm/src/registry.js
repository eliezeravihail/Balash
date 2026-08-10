'use strict';

const { Booking } = require('./booking');

// The one owner of "what bookings exist" and "what is waiting for each room", and so the one place
// every admission rule is enforced. Every booking that comes to exist — a direct booking, a series
// occurrence, or a waitlist promotion — passes through _admit, and _admit is the only writer, so
// auditing any admission rule (overlap, per-person, capacity) means reading exactly one method.
//
// Bookings are held in a single flat list, not partitioned by room: since a person may not be in two
// overlapping meetings in ANY room, conflict is no longer a room-local question, so the conflict scan
// spans all bookings. Room capacity is the one genuinely per-room fact, held on its own.
class BookingRegistry {
  constructor() {
    this._bookings = [];
    this._capacity = new Map();
    this._waitlist = new Map();
  }

  // Declare a room's capacity (max attendees per booking). An undeclared room is unlimited.
  setCapacity(room, capacity) {
    if (!Number.isInteger(capacity) || capacity < 0) {
      throw new RangeError(`capacity must be a non-negative integer, got ${capacity}`);
    }
    this._capacity.set(room, capacity);
  }

  // Attempt to book [start, end) on room for organizer with the given attendees.
  // Returns the created Booking, or null if it is rejected. A single booking is the one-element case
  // of a series, so it shares the same atomic gate.
  book(room, organizer, start, end, attendees = []) {
    const admitted = this._admit([new Booking(room, organizer, start, end, attendees)]);
    return admitted === null ? null : admitted[0];
  }

  // Attempt to book a recurring series: occurrence i is
  // [start + i*everyMinutes, end + i*everyMinutes), for i in 0..count-1, all with the same attendees.
  // All-or-nothing: if any occurrence is rejected (overlap, per-person, or capacity), the whole
  // series is rejected and nothing is created. count must be a positive integer.
  bookSeries(room, organizer, start, end, everyMinutes, count, attendees = []) {
    if (!Number.isInteger(count) || count < 1) {
      throw new RangeError(`count must be a positive integer, got ${count}`);
    }
    const occurrences = [];
    for (let i = 0; i < count; i++) {
      const shift = i * everyMinutes;
      occurrences.push(new Booking(room, organizer, start + shift, end + shift, attendees));
    }
    return this._admit(occurrences);
  }

  // Join the waitlist for [start, end) on room. A waiting request is just a booking that has not been
  // admitted yet — the same object is admitted verbatim if it is later promoted, so the handle
  // returned here is the very Booking that will appear in the schedule on promotion.
  waitlist(room, organizer, start, end, attendees = []) {
    const entry = new Booking(room, organizer, start, end, attendees);
    const queue = this._waitlist.get(room);
    if (queue === undefined) this._waitlist.set(room, [entry]);
    else queue.push(entry);
    return entry;
  }

  // Free a booking's interval again by removing that exact booking, then run the waitlist promotion
  // cascade for that room. Returns { removed, promoted }: whether the target was present, and the
  // bookings promoted off the waitlist as a result, in the order they were promoted.
  cancel(booking) {
    const i = this._bookings.indexOf(booking);
    if (i === -1) return { removed: false, promoted: [] };
    this._bookings.splice(i, 1);
    return { removed: true, promoted: this._promote(booking.room) };
  }

  // A room's bookings ordered by start time. Returns a fresh array so callers cannot mutate stored
  // state; an unbooked room reads as empty.
  scheduleFor(room) {
    return this._bookings
      .filter((b) => b.room === room)
      .sort((a, b) => a.start - b.start);
  }

  // The atomic admission gate. For each candidate, enforce every admission rule against what is
  // already stored and against the earlier candidates in the same set; then commit all of them or
  // none. Because every check happens before any write, a rejected set leaves storage untouched — no
  // rollback needed. This is the single place all three admission paths funnel through, so every rule
  // enforced here holds for direct bookings, series, and promotions alike.
  _admit(candidates) {
    for (let i = 0; i < candidates.length; i++) {
      const candidate = candidates[i];
      const capacity = this._capacity.get(candidate.room);
      if (capacity !== undefined && candidate.attendees.length > capacity) return null;
      if (this._bookings.some((b) => b.conflictsWith(candidate))) return null;
      if (candidates.slice(0, i).some((b) => b.conflictsWith(candidate))) return null;
    }
    for (const candidate of candidates) this._bookings.push(candidate);
    return candidates;
  }

  // Walk the room's waitlist in arrival order and admit each entry that now fits, through the same
  // gate that guards every booking — so a promotion likewise obeys capacity and the per-person rule.
  // A promotion only ever adds a booking, so it can only add conflicts, never remove them: a single
  // forward pass suffices, and an entry skipped as still-blocked stays blocked. Because _admit checks
  // against live stored bookings, each promotion is seen by the entries still behind it in the queue.
  _promote(room) {
    const queue = this._waitlist.get(room);
    if (queue === undefined) return [];
    const remaining = [];
    const promoted = [];
    for (const entry of queue) {
      if (this._admit([entry]) !== null) promoted.push(entry);
      else remaining.push(entry);
    }
    this._waitlist.set(room, remaining);
    return promoted;
  }
}

module.exports = { BookingRegistry };
