'use strict';

// In-memory meeting-room booking.
// Intervals are half-open [start, end): [10,20) and [20,30) do NOT conflict.
// Times are integers (minutes).

function overlaps(aStart, aEnd, bStart, bEnd) {
  // Half-open overlap: true when the intervals share any point.
  return aStart < bEnd && bStart < aEnd;
}

class BookingSystem {
  constructor() {
    // room -> array of bookings, kept sorted by start.
    this._rooms = new Map();
    // room -> array of waitlist entries, in queue (arrival) order.
    this._waitlists = new Map();
    // room -> declared capacity (max attendees). Absent = unlimited.
    this._capacities = new Map();
    // bookingId -> room, for cancel lookups.
    this._index = new Map();
    this._nextId = 1;
  }

  // Declare a room's capacity (max number of attendees per booking).
  // A room with no declared capacity is unlimited.
  setCapacity(room, capacity) {
    if (!Number.isInteger(capacity) || capacity < 1) {
      throw new RangeError('capacity must be a positive integer');
    }
    this._capacities.set(room, capacity);
  }

  _validateInterval(start, end) {
    if (!Number.isInteger(start) || !Number.isInteger(end)) {
      throw new TypeError('start and end must be integers');
    }
    if (end <= start) {
      throw new RangeError('end must be greater than start');
    }
  }

  _normalizeAttendees(attendees) {
    if (!Array.isArray(attendees)) {
      throw new TypeError('attendees must be an array of person ids');
    }
    return attendees;
  }

  // Room-level time conflict with an existing booking in the same room.
  _conflicts(room, start, end) {
    const bookings = this._rooms.get(room);
    if (!bookings) return false;
    for (const b of bookings) {
      if (overlaps(start, end, b.start, b.end)) return true;
    }
    return false;
  }

  // Per-person rule: is any of `attendees` already in a booking (ANY room)
  // whose interval overlaps [start, end)?
  _personConflict(start, end, attendees) {
    if (attendees.length === 0) return false;
    const set = new Set(attendees);
    for (const bookings of this._rooms.values()) {
      for (const b of bookings) {
        if (!overlaps(start, end, b.start, b.end)) continue;
        for (const p of b.attendees) {
          if (set.has(p)) return true;
        }
      }
    }
    return false;
  }

  // Single gate every creation path (single / recurring / promotion) shares:
  // room-time free, capacity respected, and no per-person overlap anywhere.
  _canBook(room, start, end, attendees) {
    if (this._conflicts(room, start, end)) return false;
    const cap = this._capacities.get(room);
    if (cap !== undefined && attendees.length > cap) return false;
    if (this._personConflict(start, end, attendees)) return false;
    return true;
  }

  _insert(room, start, end, organizer, attendees, id = this._nextId++) {
    const booking = { id, room, start, end, organizer, attendees: [...attendees] };
    let bookings = this._rooms.get(room);
    if (!bookings) {
      bookings = [];
      this._rooms.set(room, bookings);
    }
    bookings.push(booking);
    bookings.sort((x, y) => x.start - y.start);
    this._index.set(booking.id, room);
    return booking.id;
  }

  book(room, start, end, organizer, attendees = []) {
    this._validateInterval(start, end);
    attendees = this._normalizeAttendees(attendees);
    if (!this._canBook(room, start, end, attendees)) {
      return null; // rejected: no booking created
    }
    return this._insert(room, start, end, organizer, attendees);
  }

  bookRecurring(room, start, end, organizer, { everyMinutes, count }, attendees = []) {
    this._validateInterval(start, end);
    attendees = this._normalizeAttendees(attendees);
    if (!Number.isInteger(everyMinutes) || everyMinutes <= 0) {
      throw new RangeError('everyMinutes must be a positive integer');
    }
    if (!Number.isInteger(count) || count <= 0) {
      throw new RangeError('count must be a positive integer');
    }

    // Compute all occurrences up front and check every one: all-or-nothing.
    const occurrences = [];
    for (let i = 0; i < count; i++) {
      occurrences.push([start + i * everyMinutes, end + i * everyMinutes]);
    }

    // Reject if occurrences would conflict with EACH OTHER in time (same room,
    // same attendees, so a time overlap is both a room and a per-person clash).
    for (let i = 0; i < occurrences.length; i++) {
      const [s, e] = occurrences[i];
      for (let j = i + 1; j < occurrences.length; j++) {
        const [s2, e2] = occurrences[j];
        if (overlaps(s, e, s2, e2)) return null;
      }
    }

    // Reject if ANY occurrence violates room-time, capacity, or per-person
    // rules against existing bookings.
    for (const [s, e] of occurrences) {
      if (!this._canBook(room, s, e, attendees)) return null;
    }

    // All clear: book them all.
    return occurrences.map(([s, e]) => this._insert(room, s, e, organizer, attendees));
  }

  // Book if allowed; otherwise join the room's waitlist.
  // Returns { status: 'booked', id } or { status: 'waitlisted', id }.
  // The returned id is stable: a waitlisted entry keeps the same id when it is
  // later promoted into a real booking.
  bookOrWaitlist(room, start, end, organizer, attendees = []) {
    this._validateInterval(start, end);
    attendees = this._normalizeAttendees(attendees);
    if (this._canBook(room, start, end, attendees)) {
      return { status: 'booked', id: this._insert(room, start, end, organizer, attendees) };
    }
    const entry = { id: this._nextId++, room, start, end, organizer, attendees: [...attendees] };
    let queue = this._waitlists.get(room);
    if (!queue) {
      queue = [];
      this._waitlists.set(room, queue);
    }
    queue.push(entry); // append preserves arrival order
    return { status: 'waitlisted', id: entry.id };
  }

  // Waitlist entries for a room, in queue order (copies).
  waitlistFor(room) {
    const queue = this._waitlists.get(room);
    if (!queue) return [];
    return queue.map((e) => ({ ...e, attendees: [...e.attendees] }));
  }

  cancel(bookingId) {
    const room = this._index.get(bookingId);
    if (room === undefined) return false; // unknown or already cancelled
    const bookings = this._rooms.get(room);
    const idx = bookings.findIndex((b) => b.id === bookingId);
    bookings.splice(idx, 1);
    if (bookings.length === 0) this._rooms.delete(room);
    this._index.delete(bookingId);
    // Freeing an interval can unblock waitlisted entries in ANY room (the
    // per-person rule spans rooms), so re-check every room's waitlist.
    this._promoteWaitlists();
    return true;
  }

  // Promote compatible waitlist entries after an interval frees up. Passes over
  // every room's queue in arrival order; a promotion inserts a live booking, so
  // later entries (in that room or another) are checked against it too. Repeats
  // until a full sweep promotes nothing, since one promotion can unblock a
  // dependent entry elsewhere.
  _promoteWaitlists() {
    let promotedSomething = true;
    while (promotedSomething) {
      promotedSomething = false;
      for (const [room, queue] of this._waitlists) {
        for (let i = 0; i < queue.length; ) {
          const e = queue[i];
          if (this._canBook(room, e.start, e.end, e.attendees)) {
            this._insert(room, e.start, e.end, e.organizer, e.attendees, e.id);
            queue.splice(i, 1);
            promotedSomething = true;
          } else {
            i++;
          }
        }
        if (queue.length === 0) this._waitlists.delete(room);
      }
    }
  }

  schedule(room) {
    const bookings = this._rooms.get(room);
    if (!bookings) return [];
    // Return copies, ordered by start (already kept sorted).
    return bookings.map((b) => ({ ...b, attendees: [...b.attendees] }));
  }
}

module.exports = { BookingSystem };
