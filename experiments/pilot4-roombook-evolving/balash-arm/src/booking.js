'use strict';

// A Booking is one reserved half-open interval [start, end) on a room, by an organizer, attended by
// a set of person ids. It owns the definition of when two bookings clash: they must not overlap in
// time while sharing a resource — the same room, or a person. That single pairwise rule is both the
// same-room no-double-book rule and the per-person no-overlap rule; a caller asks "do these clash?"
// rather than reaching into rooms and attendee lists to decide for itself. It also owns the rule
// that an interval must be non-empty: end must be strictly after start.
class Booking {
  constructor(room, organizer, start, end, attendees = []) {
    if (!Number.isInteger(start) || !Number.isInteger(end)) {
      throw new TypeError('start and end must be integer minutes');
    }
    if (end <= start) {
      throw new RangeError(`empty interval [${start}, ${end}): end must be after start`);
    }
    if (!Array.isArray(attendees)) {
      throw new TypeError('attendees must be an array of person ids');
    }
    this.room = room;
    this.organizer = organizer;
    this.start = start;
    this.end = end;
    // A booking's attendees are fixed once it exists: copy and freeze so a caller holding the
    // original array cannot mutate it out from under the per-person rule after admission.
    this.attendees = Object.freeze([...attendees]);
    Object.freeze(this);
  }

  // Half-open overlap: [a.start, a.end) and [b.start, b.end) share a point iff each starts
  // before the other ends. Touching endpoints ([10,20) & [20,30)) therefore do not overlap.
  overlaps(other) {
    return this.start < other.end && other.start < this.end;
  }

  // Two bookings clash iff they overlap in time AND compete for a shared resource: the same room
  // (two meetings can't hold one room at once) or a shared attendee (one person can't be in two
  // meetings at once, in any rooms). This is the whole conflict definition, in one place.
  conflictsWith(other) {
    if (!this.overlaps(other)) return false;
    if (this.room === other.room) return true;
    return this.attendees.some((p) => other.attendees.includes(p));
  }
}

module.exports = { Booking };
