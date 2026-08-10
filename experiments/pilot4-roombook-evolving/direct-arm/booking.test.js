'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const { BookingSystem } = require('./booking');

test('book returns a booking id on success', () => {
  const sys = new BookingSystem();
  const id = sys.book('A', 10, 20, 'alice');
  assert.equal(typeof id, 'number');
  assert.ok(id > 0);
});

test('overlapping bookings on the same room are rejected', () => {
  const sys = new BookingSystem();
  assert.ok(sys.book('A', 10, 20, 'alice'));
  const id = sys.book('A', 15, 25, 'bob'); // overlaps [10,20)
  assert.equal(id, null);
  // The rejected booking must not have been created.
  assert.equal(sys.schedule('A').length, 1);
});

test('adjacent half-open intervals do NOT conflict', () => {
  const sys = new BookingSystem();
  assert.ok(sys.book('A', 10, 20, 'alice'));
  assert.ok(sys.book('A', 20, 30, 'bob')); // [20,30) touches but does not overlap
  assert.equal(sys.schedule('A').length, 2);
});

test('containment and identical intervals conflict', () => {
  const sys = new BookingSystem();
  assert.ok(sys.book('A', 10, 30, 'alice'));
  assert.equal(sys.book('A', 15, 20, 'bob'), null); // fully inside
  assert.equal(sys.book('A', 10, 30, 'carol'), null); // identical
  assert.equal(sys.book('A', 5, 35, 'dave'), null); // fully contains existing
  assert.equal(sys.schedule('A').length, 1);
});

test('different rooms never conflict with each other', () => {
  const sys = new BookingSystem();
  assert.ok(sys.book('A', 10, 20, 'alice'));
  assert.ok(sys.book('B', 10, 20, 'bob')); // same interval, different room
  assert.equal(sys.schedule('A').length, 1);
  assert.equal(sys.schedule('B').length, 1);
});

test('schedule returns bookings ordered by start time', () => {
  const sys = new BookingSystem();
  sys.book('A', 40, 50, 'd');
  sys.book('A', 10, 20, 'a');
  sys.book('A', 30, 40, 'c');
  sys.book('A', 20, 30, 'b');
  const starts = sys.schedule('A').map((b) => b.start);
  assert.deepEqual(starts, [10, 20, 30, 40]);
});

test('schedule for an unknown room is empty', () => {
  const sys = new BookingSystem();
  assert.deepEqual(sys.schedule('nope'), []);
});

test('schedule carries booking details', () => {
  const sys = new BookingSystem();
  const id = sys.book('A', 10, 20, 'alice');
  const [b] = sys.schedule('A');
  assert.deepEqual(b, { id, room: 'A', start: 10, end: 20, organizer: 'alice', attendees: [] });
});

test('schedule returns copies that do not mutate internal state', () => {
  const sys = new BookingSystem();
  sys.book('A', 10, 20, 'alice');
  const snap = sys.schedule('A');
  snap[0].start = 999;
  assert.equal(sys.schedule('A')[0].start, 10);
});

test('invalid intervals are rejected', () => {
  const sys = new BookingSystem();
  assert.throws(() => sys.book('A', 20, 10, 'x'), RangeError); // end < start
  assert.throws(() => sys.book('A', 10, 10, 'x'), RangeError); // empty
  assert.throws(() => sys.book('A', 1.5, 10, 'x'), TypeError); // non-integer
});

// ---- Stage 2: recurring bookings + cancel ----

test('bookRecurring creates count occurrences shifted by everyMinutes', () => {
  const sys = new BookingSystem();
  const ids = sys.bookRecurring('A', 10, 20, 'alice', { everyMinutes: 60, count: 3 });
  assert.equal(ids.length, 3);
  const intervals = sys.schedule('A').map((b) => [b.start, b.end]);
  assert.deepEqual(intervals, [
    [10, 20],
    [70, 80],
    [130, 140],
  ]);
});

test('bookRecurring returns the created ids in occurrence order', () => {
  const sys = new BookingSystem();
  const ids = sys.bookRecurring('A', 0, 10, 'alice', { everyMinutes: 100, count: 2 });
  const scheduled = sys.schedule('A');
  assert.deepEqual(ids, scheduled.map((b) => b.id));
});

test('bookRecurring is all-or-nothing: one conflict rejects the whole series', () => {
  const sys = new BookingSystem();
  // Pre-book a slot that collides with the 2nd occurrence [70,80).
  assert.ok(sys.book('A', 75, 90, 'bob'));
  const result = sys.bookRecurring('A', 10, 20, 'alice', { everyMinutes: 60, count: 3 });
  assert.equal(result, null);
  // Nothing from the series was booked; only bob's original remains.
  assert.equal(sys.schedule('A').length, 1);
  assert.equal(sys.schedule('A')[0].organizer, 'bob');
});

test('bookRecurring rejects a series that would overlap itself', () => {
  const sys = new BookingSystem();
  // duration 20 but step 10 -> consecutive occurrences overlap.
  const result = sys.bookRecurring('A', 0, 20, 'alice', { everyMinutes: 10, count: 3 });
  assert.equal(result, null);
  assert.equal(sys.schedule('A').length, 0);
});

test('bookRecurring with adjacent occurrences (step == duration) succeeds', () => {
  const sys = new BookingSystem();
  const ids = sys.bookRecurring('A', 0, 10, 'alice', { everyMinutes: 10, count: 3 });
  assert.equal(ids.length, 3);
  assert.deepEqual(sys.schedule('A').map((b) => [b.start, b.end]), [
    [0, 10],
    [10, 20],
    [20, 30],
  ]);
});

test('bookRecurring validates everyMinutes and count', () => {
  const sys = new BookingSystem();
  assert.throws(() => sys.bookRecurring('A', 0, 10, 'a', { everyMinutes: 0, count: 2 }), RangeError);
  assert.throws(() => sys.bookRecurring('A', 0, 10, 'a', { everyMinutes: 10, count: 0 }), RangeError);
  assert.throws(() => sys.bookRecurring('A', 0, 10, 'a', { everyMinutes: 1.5, count: 2 }), RangeError);
});

test('cancel frees the interval so it can be booked again', () => {
  const sys = new BookingSystem();
  const id = sys.book('A', 10, 20, 'alice');
  assert.equal(sys.book('A', 15, 25, 'bob'), null); // conflicts while held
  assert.equal(sys.cancel(id), true);
  assert.equal(sys.schedule('A').length, 0);
  assert.ok(sys.book('A', 15, 25, 'bob')); // now free
});

test('cancel returns false for unknown or already-cancelled ids', () => {
  const sys = new BookingSystem();
  const id = sys.book('A', 10, 20, 'alice');
  assert.equal(sys.cancel(9999), false);
  assert.equal(sys.cancel(id), true);
  assert.equal(sys.cancel(id), false); // already cancelled
});

test('cancel only removes the targeted booking', () => {
  const sys = new BookingSystem();
  const ids = sys.bookRecurring('A', 10, 20, 'alice', { everyMinutes: 60, count: 3 });
  assert.equal(sys.cancel(ids[1]), true);
  const intervals = sys.schedule('A').map((b) => [b.start, b.end]);
  assert.deepEqual(intervals, [
    [10, 20],
    [130, 140],
  ]);
});

// ---- Stage 3: waitlist with auto-promotion ----

test('bookOrWaitlist books immediately when the interval is free', () => {
  const sys = new BookingSystem();
  const res = sys.bookOrWaitlist('A', 10, 20, 'alice');
  assert.equal(res.status, 'booked');
  assert.equal(sys.schedule('A').length, 1);
  assert.deepEqual(sys.waitlistFor('A'), []);
});

test('bookOrWaitlist waitlists on conflict instead of turning away', () => {
  const sys = new BookingSystem();
  sys.book('A', 10, 20, 'alice');
  const res = sys.bookOrWaitlist('A', 15, 25, 'bob'); // conflicts
  assert.equal(res.status, 'waitlisted');
  assert.equal(sys.schedule('A').length, 1); // no booking created
  assert.deepEqual(
    sys.waitlistFor('A').map((e) => [e.start, e.end, e.organizer]),
    [[15, 25, 'bob']]
  );
});

test('cancel auto-promotes the earliest compatible waitlist entry', () => {
  const sys = new BookingSystem();
  const held = sys.book('A', 10, 20, 'alice');
  const res = sys.bookOrWaitlist('A', 15, 25, 'bob');
  sys.cancel(held); // frees [10,20), so bob's [15,25) fits
  assert.deepEqual(sys.waitlistFor('A'), []); // promoted off the waitlist
  const sched = sys.schedule('A');
  assert.equal(sched.length, 1);
  assert.deepEqual([sched[0].start, sched[0].end, sched[0].organizer], [15, 25, 'bob']);
  // Promoted entry keeps its original id.
  assert.equal(sched[0].id, res.id);
});

test('promotion respects queue order among compatible entries', () => {
  const sys = new BookingSystem();
  const held = sys.book('A', 0, 100, 'owner');
  const first = sys.bookOrWaitlist('A', 10, 20, 'alice'); // queued 1st
  const second = sys.bookOrWaitlist('A', 12, 22, 'bob'); // queued 2nd, overlaps alice
  sys.cancel(held);
  // Both fit the freed room individually, but they overlap each other; the
  // earliest-queued wins and the later one stays waitlisted.
  const sched = sys.schedule('A');
  assert.equal(sched.length, 1);
  assert.equal(sched[0].id, first.id);
  assert.deepEqual(
    sys.waitlistFor('A').map((e) => e.id),
    [second.id]
  );
});

test('several non-overlapping entries all get promoted in one cancel', () => {
  const sys = new BookingSystem();
  const held = sys.book('A', 0, 100, 'owner');
  const a = sys.bookOrWaitlist('A', 0, 10, 'alice');
  const b = sys.bookOrWaitlist('A', 10, 20, 'bob'); // adjacent, no overlap
  const c = sys.bookOrWaitlist('A', 20, 30, 'carol');
  sys.cancel(held);
  assert.deepEqual(sys.waitlistFor('A'), []);
  assert.deepEqual(
    sys.schedule('A').map((s) => s.id),
    [a.id, b.id, c.id]
  );
});

test('promotion skips entries that still conflict, keeping them queued', () => {
  const sys = new BookingSystem();
  const other = sys.book('A', 50, 60, 'owner'); // stays booked
  const held = sys.book('A', 10, 20, 'alice');
  const bob = sys.bookOrWaitlist('A', 15, 25, 'bob'); // needs [10,20) freed
  const carol = sys.bookOrWaitlist('A', 55, 65, 'carol'); // conflicts with [50,60), still blocked
  sys.cancel(held);
  assert.deepEqual(
    sys.schedule('A').map((s) => [s.start, s.end]),
    [[15, 25], [50, 60]]
  );
  assert.deepEqual(
    sys.waitlistFor('A').map((e) => e.id),
    [carol.id]
  );
  assert.ok(other && bob && carol);
});

test('waitlistFor returns copies and unknown rooms are empty', () => {
  const sys = new BookingSystem();
  assert.deepEqual(sys.waitlistFor('nope'), []);
  sys.book('A', 10, 20, 'alice');
  sys.bookOrWaitlist('A', 15, 25, 'bob');
  const snap = sys.waitlistFor('A');
  snap[0].start = 999;
  assert.equal(sys.waitlistFor('A')[0].start, 15);
});

// ---- Stage 4: capacity + per-person no-overlap rule ----

test('a room with no declared capacity is unlimited', () => {
  const sys = new BookingSystem();
  const id = sys.book('A', 10, 20, 'org', ['p1', 'p2', 'p3', 'p4', 'p5']);
  assert.ok(id);
});

test('booking is rejected when attendees exceed capacity', () => {
  const sys = new BookingSystem();
  sys.setCapacity('A', 2);
  assert.equal(sys.book('A', 10, 20, 'org', ['p1', 'p2', 'p3']), null);
  assert.equal(sys.schedule('A').length, 0);
  // exactly at capacity is allowed
  assert.ok(sys.book('A', 10, 20, 'org', ['p1', 'p2']));
});

test('setCapacity validates its argument', () => {
  const sys = new BookingSystem();
  assert.throws(() => sys.setCapacity('A', 0), RangeError);
  assert.throws(() => sys.setCapacity('A', 1.5), RangeError);
});

test('a person cannot be in two overlapping meetings in the same room', () => {
  const sys = new BookingSystem();
  sys.book('A', 10, 20, 'org', ['alice']);
  assert.equal(sys.book('A', 15, 25, 'org', ['alice']), null);
});

test('the per-person rule spans rooms', () => {
  const sys = new BookingSystem();
  sys.book('A', 10, 20, 'org', ['alice']);
  // Different room, overlapping time, same person -> rejected.
  assert.equal(sys.book('B', 15, 25, 'org', ['alice']), null);
  assert.equal(sys.schedule('B').length, 0);
});

test('per-person rule allows the same person in adjacent (non-overlapping) meetings', () => {
  const sys = new BookingSystem();
  assert.ok(sys.book('A', 10, 20, 'org', ['alice']));
  assert.ok(sys.book('B', 20, 30, 'org', ['alice'])); // adjacent, different room
});

test('per-person rule ignores non-shared attendees', () => {
  const sys = new BookingSystem();
  sys.book('A', 10, 20, 'org', ['alice']);
  assert.ok(sys.book('B', 15, 25, 'org', ['bob'])); // overlapping time, disjoint people
});

test('recurring series is rejected as a whole on a per-person conflict', () => {
  const sys = new BookingSystem();
  // Blocks the 2nd occurrence [70,80) via alice in another room.
  sys.book('B', 75, 85, 'org', ['alice']);
  const res = sys.bookRecurring('A', 10, 20, 'org', { everyMinutes: 60, count: 3 }, ['alice']);
  assert.equal(res, null);
  assert.equal(sys.schedule('A').length, 0); // nothing booked
});

test('recurring series is rejected as a whole on a capacity violation', () => {
  const sys = new BookingSystem();
  sys.setCapacity('A', 1);
  const res = sys.bookRecurring('A', 10, 20, 'org', { everyMinutes: 60, count: 3 }, ['p1', 'p2']);
  assert.equal(res, null);
  assert.equal(sys.schedule('A').length, 0);
});

test('waitlist entry is NOT promoted if it would violate the per-person rule', () => {
  const sys = new BookingSystem();
  const held = sys.book('A', 10, 20, 'org', ['alice']); // blocks room A time
  // alice is also busy in room B during [20,30) — adjacent to `held` (so it is
  // bookable now) but overlapping the waitlisted [15,25) request.
  const elsewhere = sys.book('B', 20, 30, 'org', ['alice']);
  assert.ok(elsewhere);
  const res = sys.bookOrWaitlist('A', 15, 25, 'org', ['alice']); // waitlisted
  assert.equal(res.status, 'waitlisted');
  sys.cancel(held); // frees room A, but alice is still busy in room B
  assert.equal(sys.schedule('A').length, 0); // not promoted
  assert.deepEqual(sys.waitlistFor('A').map((e) => e.id), [res.id]);
  // Once alice's other meeting ends, cancelling it promotes the entry.
  sys.cancel(elsewhere);
  const sched = sys.schedule('A');
  assert.equal(sched.length, 1);
  assert.equal(sched[0].id, res.id);
});

test('waitlist entry is NOT promoted if it would exceed capacity', () => {
  const sys = new BookingSystem();
  sys.setCapacity('A', 1);
  const held = sys.book('A', 10, 20, 'org', ['p1']);
  const res = sys.bookOrWaitlist('A', 15, 25, 'org', ['p1', 'p2']); // 2 > cap 1
  assert.equal(res.status, 'waitlisted');
  sys.cancel(held); // room free, but capacity still exceeded
  assert.equal(sys.schedule('A').length, 0);
  assert.deepEqual(sys.waitlistFor('A').map((e) => e.id), [res.id]);
});

test('cancelling in one room can promote a waitlist entry in another room', () => {
  const sys = new BookingSystem();
  // alice booked in room B; a room-A request needing alice is waitlisted
  // (room A itself is free, but alice is busy in B).
  const bBooking = sys.book('B', 10, 30, 'org', ['alice']);
  const res = sys.bookOrWaitlist('A', 15, 25, 'org', ['alice']);
  assert.equal(res.status, 'waitlisted');
  sys.cancel(bBooking); // frees alice -> room-A entry becomes promotable
  const sched = sys.schedule('A');
  assert.equal(sched.length, 1);
  assert.equal(sched[0].id, res.id);
  assert.deepEqual(sys.waitlistFor('A'), []);
});

test('attendees are carried on the booking and returned as copies', () => {
  const sys = new BookingSystem();
  const src = ['alice', 'bob'];
  sys.book('A', 10, 20, 'org', src);
  src.push('mallory'); // mutating caller's array must not affect stored booking
  const [b] = sys.schedule('A');
  assert.deepEqual(b.attendees, ['alice', 'bob']);
});

test('book rejects a non-array attendees argument', () => {
  const sys = new BookingSystem();
  assert.throws(() => sys.book('A', 10, 20, 'org', 'alice'), TypeError);
});
