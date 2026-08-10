'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const { Booking } = require('../src/booking');
const { BookingRegistry } = require('../src/registry');

test('a booking is created and appears in the room schedule', () => {
  const reg = new BookingRegistry();
  const b = reg.book('A', 'alice', 10, 20);
  assert.ok(b);
  assert.equal(b.room, 'A');
  assert.equal(b.organizer, 'alice');
  const sched = reg.scheduleFor('A');
  assert.equal(sched.length, 1);
  assert.deepEqual([sched[0].start, sched[0].end], [10, 20]);
});

test('overlapping booking on the same room is rejected and nothing is created', () => {
  const reg = new BookingRegistry();
  reg.book('A', 'alice', 10, 20);
  const rejected = reg.book('A', 'bob', 15, 25);
  assert.equal(rejected, null);
  assert.equal(reg.scheduleFor('A').length, 1);
});

test('touching intervals do not conflict (half-open)', () => {
  const reg = new BookingRegistry();
  assert.ok(reg.book('A', 'alice', 10, 20));
  assert.ok(reg.book('A', 'bob', 20, 30));
  assert.equal(reg.scheduleFor('A').length, 2);
});

test('containment and identical intervals conflict', () => {
  const reg = new BookingRegistry();
  reg.book('A', 'alice', 10, 30);
  assert.equal(reg.book('A', 'bob', 15, 20), null); // inside
  assert.equal(reg.book('A', 'bob', 10, 30), null); // identical
  assert.equal(reg.book('A', 'bob', 5, 35), null);  // encloses
  assert.equal(reg.scheduleFor('A').length, 1);
});

test('different rooms never conflict', () => {
  const reg = new BookingRegistry();
  assert.ok(reg.book('A', 'alice', 10, 20));
  assert.ok(reg.book('B', 'bob', 10, 20));
  assert.equal(reg.scheduleFor('A').length, 1);
  assert.equal(reg.scheduleFor('B').length, 1);
});

test('schedule is ordered by start regardless of booking order', () => {
  const reg = new BookingRegistry();
  reg.book('A', 'a', 40, 50);
  reg.book('A', 'b', 10, 20);
  reg.book('A', 'c', 25, 30);
  assert.deepEqual(reg.scheduleFor('A').map((x) => x.start), [10, 25, 40]);
});

test('schedule of an unbooked room is empty', () => {
  const reg = new BookingRegistry();
  assert.deepEqual(reg.scheduleFor('Z'), []);
});

test('the returned schedule cannot mutate stored state', () => {
  const reg = new BookingRegistry();
  reg.book('A', 'alice', 10, 20);
  const sched = reg.scheduleFor('A');
  sched.push('garbage');
  assert.equal(reg.scheduleFor('A').length, 1);
});

test('a malformed interval is a caller error, not a rejection', () => {
  const reg = new BookingRegistry();
  assert.throws(() => reg.book('A', 'alice', 20, 10), RangeError);
  assert.throws(() => reg.book('A', 'alice', 20, 20), RangeError);
  assert.throws(() => reg.book('A', 'alice', 10.5, 20), TypeError);
});

test('Booking.overlaps encodes half-open semantics directly', () => {
  const a = new Booking('A', 'x', 10, 20);
  assert.equal(a.overlaps(new Booking('A', 'y', 20, 30)), false);
  assert.equal(a.overlaps(new Booking('A', 'y', 15, 25)), true);
  assert.equal(a.overlaps(new Booking('A', 'y', 0, 10)), false);
});

test('a recurring series creates count occurrences at the right offsets', () => {
  const reg = new BookingRegistry();
  const series = reg.bookSeries('A', 'alice', 10, 20, 60, 3);
  assert.ok(series);
  assert.deepEqual(series.map((b) => [b.start, b.end]), [[10, 20], [70, 80], [130, 140]]);
  assert.equal(reg.scheduleFor('A').length, 3);
});

test('series is all-or-nothing: one occurrence conflicting rejects the whole series', () => {
  const reg = new BookingRegistry();
  reg.book('A', 'bob', 75, 85); // will clash with the 2nd occurrence [70,80)
  const series = reg.bookSeries('A', 'alice', 10, 20, 60, 3);
  assert.equal(series, null);
  // nothing from the series was created — only bob's booking remains
  assert.deepEqual(reg.scheduleFor('A').map((b) => b.start), [75]);
});

test('a series that overlaps itself is rejected as a whole', () => {
  const reg = new BookingRegistry();
  // stride 5 < duration 10, so consecutive occurrences overlap each other
  const series = reg.bookSeries('A', 'alice', 10, 20, 5, 3);
  assert.equal(series, null);
  assert.deepEqual(reg.scheduleFor('A'), []);
});

test('a non-overlapping self-adjacent series succeeds (half-open)', () => {
  const reg = new BookingRegistry();
  // stride equals duration: [10,20),[20,30),[30,40) — touching, not overlapping
  const series = reg.bookSeries('A', 'alice', 10, 20, 10, 3);
  assert.ok(series);
  assert.equal(reg.scheduleFor('A').length, 3);
});

test('series in different rooms do not interfere', () => {
  const reg = new BookingRegistry();
  assert.ok(reg.bookSeries('A', 'alice', 10, 20, 60, 3));
  assert.ok(reg.bookSeries('B', 'bob', 10, 20, 60, 3));
  assert.equal(reg.scheduleFor('A').length, 3);
  assert.equal(reg.scheduleFor('B').length, 3);
});

test('series count must be a positive integer (caller error)', () => {
  const reg = new BookingRegistry();
  assert.throws(() => reg.bookSeries('A', 'alice', 10, 20, 60, 0), RangeError);
  assert.throws(() => reg.bookSeries('A', 'alice', 10, 20, 60, 2.5), RangeError);
});

test('cancelling a booking frees its interval for a later booking', () => {
  const reg = new BookingRegistry();
  const b = reg.book('A', 'alice', 10, 20);
  assert.equal(reg.book('A', 'bob', 15, 25), null); // blocked while b exists
  assert.deepEqual(reg.cancel(b), { removed: true, promoted: [] });
  assert.equal(reg.scheduleFor('A').length, 0);
  assert.ok(reg.book('A', 'bob', 15, 25)); // now free
});

test('cancelling one occurrence of a series leaves the rest', () => {
  const reg = new BookingRegistry();
  const series = reg.bookSeries('A', 'alice', 10, 20, 60, 3);
  assert.equal(reg.cancel(series[1]).removed, true); // remove [70,80)
  assert.deepEqual(reg.scheduleFor('A').map((b) => b.start), [10, 130]);
  // the freed slot can be rebooked
  assert.ok(reg.book('A', 'bob', 70, 80));
});

test('cancelling a booking that is not present returns false and changes nothing', () => {
  const reg = new BookingRegistry();
  const b = reg.book('A', 'alice', 10, 20);
  assert.equal(reg.cancel(b).removed, true);
  assert.equal(reg.cancel(b).removed, false); // second time: already gone
  const stranger = new Booking('Z', 'nobody', 0, 5);
  assert.equal(reg.cancel(stranger).removed, false);
});

test('a waitlisted request is promoted when a cancel frees its interval', () => {
  const reg = new BookingRegistry();
  const held = reg.book('A', 'alice', 10, 20);
  assert.equal(reg.book('A', 'bob', 15, 25), null); // bob is turned away
  const entry = reg.waitlist('A', 'bob', 15, 25); // ...and waits instead
  assert.equal(reg.scheduleFor('A').length, 1); // waiting is not booked

  const result = reg.cancel(held);
  assert.equal(result.removed, true);
  assert.deepEqual(result.promoted, [entry]); // the very handle bob was given
  assert.deepEqual(reg.scheduleFor('A').map((b) => [b.start, b.end]), [[15, 25]]);
});

test('a waitlisted request that still conflicts after a cancel is not promoted', () => {
  const reg = new BookingRegistry();
  const a1 = reg.book('A', 'alice', 10, 20);
  reg.book('A', 'alice', 20, 30); // a2, still there after a1 is cancelled
  const entry = reg.waitlist('A', 'bob', 15, 25); // overlaps both a1 and a2

  const result = reg.cancel(a1); // frees [10,20) but [20,30) still blocks bob
  assert.deepEqual(result.promoted, []);
  assert.equal(reg.scheduleFor('A').length, 1); // only a2 remains; bob still waiting
});

test('promotion is not triggered by cancelling an absent booking', () => {
  const reg = new BookingRegistry();
  const held = reg.book('A', 'alice', 10, 20);
  reg.waitlist('A', 'bob', 10, 20);
  const ghost = new Booking('A', 'nobody', 100, 110);
  const result = reg.cancel(ghost); // not present -> no interval freed
  assert.deepEqual(result, { removed: false, promoted: [] });
  assert.equal(reg.scheduleFor('A').length, 1); // held still there, bob still waiting
});

test('cascade promotes multiple non-overlapping entries in queue order', () => {
  const reg = new BookingRegistry();
  const held = reg.book('A', 'alice', 0, 100); // blocks everything
  const e1 = reg.waitlist('A', 'x', 0, 30);
  const e2 = reg.waitlist('A', 'y', 30, 60);
  const e3 = reg.waitlist('A', 'z', 60, 90);

  const result = reg.cancel(held);
  assert.deepEqual(result.promoted, [e1, e2, e3]); // all three fit, queue order
  assert.deepEqual(reg.scheduleFor('A').map((b) => b.start), [0, 30, 60]);
});

test('cascade skips an entry that conflicts with one just promoted, keeps queue order', () => {
  const reg = new BookingRegistry();
  const held = reg.book('A', 'alice', 0, 100);
  const early = reg.waitlist('A', 'x', 0, 40);  // queued first, fits
  const clash = reg.waitlist('A', 'y', 20, 60); // overlaps `early`, must be skipped
  const later = reg.waitlist('A', 'z', 40, 80);  // fits after `early`

  const result = reg.cancel(held);
  assert.deepEqual(result.promoted, [early, later]); // clash skipped, order preserved
  assert.deepEqual(reg.scheduleFor('A').map((b) => [b.start, b.end]), [[0, 40], [40, 80]]);
});

test('a skipped waitlist entry stays queued and can be promoted by a later cancel', () => {
  const reg = new BookingRegistry();
  const a1 = reg.book('A', 'alice', 10, 20);
  const a2 = reg.book('A', 'alice', 20, 30);
  const entry = reg.waitlist('A', 'bob', 15, 25); // overlaps both

  assert.deepEqual(reg.cancel(a1).promoted, []); // still blocked by a2 -> stays queued
  const result = reg.cancel(a2); // now nothing blocks bob
  assert.deepEqual(result.promoted, [entry]);
  assert.deepEqual(reg.scheduleFor('A').map((b) => [b.start, b.end]), [[15, 25]]);
});

test('a promoted booking behaves as a real booking (blocks and can be cancelled)', () => {
  const reg = new BookingRegistry();
  const held = reg.book('A', 'alice', 10, 20);
  const entry = reg.waitlist('A', 'bob', 10, 20);
  const promoted = reg.cancel(held).promoted[0];
  assert.equal(promoted, entry);
  assert.equal(reg.book('A', 'carol', 10, 20), null); // promoted booking now blocks
  assert.equal(reg.cancel(promoted).removed, true);    // and is a cancellable booking
});

test('waitlisting a malformed interval is a caller error', () => {
  const reg = new BookingRegistry();
  assert.throws(() => reg.waitlist('A', 'bob', 20, 10), RangeError);
});

// ---- Stage 4: capacity ----

test('a booking exceeding room capacity is rejected; within capacity is accepted', () => {
  const reg = new BookingRegistry();
  reg.setCapacity('A', 2);
  assert.equal(reg.book('A', 'alice', 10, 20, ['p1', 'p2', 'p3']), null);
  assert.ok(reg.book('A', 'alice', 10, 20, ['p1', 'p2']));
});

test('an undeclared room is unlimited', () => {
  const reg = new BookingRegistry();
  assert.ok(reg.book('A', 'alice', 10, 20, ['p1', 'p2', 'p3', 'p4', 'p5']));
});

test('capacity 0 admits only attendee-less bookings', () => {
  const reg = new BookingRegistry();
  reg.setCapacity('A', 0);
  assert.equal(reg.book('A', 'alice', 10, 20, ['p1']), null);
  assert.ok(reg.book('A', 'alice', 10, 20)); // no attendees -> holds the room only
});

test('capacity is enforced all-or-nothing across a series', () => {
  const reg = new BookingRegistry();
  reg.setCapacity('A', 1);
  const series = reg.bookSeries('A', 'alice', 10, 20, 60, 3, ['p1', 'p2']);
  assert.equal(series, null);
  assert.deepEqual(reg.scheduleFor('A'), []); // nothing created
});

test('capacity is enforced on waitlist promotion', () => {
  const reg = new BookingRegistry();
  reg.setCapacity('A', 1);
  const held = reg.book('A', 'alice', 10, 20, ['p1']); // occupies the room
  const tooBig = reg.waitlist('A', 'bob', 10, 20, ['p2', 'p3']); // over capacity
  const ok = reg.waitlist('A', 'carol', 10, 20, ['p4']); // within capacity, queued after
  const result = reg.cancel(held);
  assert.deepEqual(result.promoted, [ok]); // tooBig skipped on capacity, carol promoted
  assert.deepEqual(reg.scheduleFor('A').map((b) => b.attendees.slice()), [['p4']]);
});

test('setCapacity rejects a nonsensical capacity', () => {
  const reg = new BookingRegistry();
  assert.throws(() => reg.setCapacity('A', -1), RangeError);
  assert.throws(() => reg.setCapacity('A', 1.5), RangeError);
});

// ---- Stage 4: per-person no-overlap (cross-room) ----

test('a person cannot be in two overlapping meetings in different rooms', () => {
  const reg = new BookingRegistry();
  assert.ok(reg.book('A', 'alice', 10, 20, ['p1']));
  assert.equal(reg.book('B', 'bob', 15, 25, ['p1']), null); // p1 double-booked across rooms
});

test('the same person in touching (non-overlapping) meetings is fine', () => {
  const reg = new BookingRegistry();
  assert.ok(reg.book('A', 'alice', 10, 20, ['p1']));
  assert.ok(reg.book('B', 'bob', 20, 30, ['p1'])); // half-open: no overlap
});

test('different people overlapping in different rooms do not conflict', () => {
  const reg = new BookingRegistry();
  assert.ok(reg.book('A', 'alice', 10, 20, ['p1']));
  assert.ok(reg.book('B', 'bob', 10, 20, ['p2']));
});

test('the same-room rule still holds regardless of attendees', () => {
  const reg = new BookingRegistry();
  assert.ok(reg.book('A', 'alice', 10, 20, ['p1']));
  assert.equal(reg.book('A', 'bob', 15, 25, ['p2']), null); // different people, same room, overlap
});

test('per-person rule is enforced all-or-nothing across a series', () => {
  const reg = new BookingRegistry();
  reg.book('B', 'bob', 130, 140, ['p1']); // clashes only with the 3rd occurrence
  const series = reg.bookSeries('A', 'alice', 10, 20, 60, 3, ['p1']);
  assert.equal(series, null);
  assert.deepEqual(reg.scheduleFor('A'), []); // whole series rejected, nothing created
});

test('per-person rule is enforced on waitlist promotion', () => {
  const reg = new BookingRegistry();
  const busy = reg.book('A', 'alice', 10, 20, ['p1']); // p1 busy in room A
  const blocker = reg.book('B', 'bob', 10, 20, ['p2']); // occupies room B
  const entry = reg.waitlist('B', 'carol', 10, 20, ['p1']); // wants room B but p1 is busy in A
  const result = reg.cancel(blocker); // frees room B interval, scans B's waitlist
  assert.deepEqual(result.promoted, []); // p1 still busy in room A -> not promoted
  assert.deepEqual(reg.scheduleFor('B'), []);
  assert.equal(reg.scheduleFor('A').length, 1); // busy untouched
});

test('a waitlist promotion respecting both rules succeeds', () => {
  const reg = new BookingRegistry();
  reg.setCapacity('B', 2);
  const blocker = reg.book('B', 'bob', 10, 20, ['p2']);
  const entry = reg.waitlist('B', 'carol', 10, 20, ['p1']); // fits capacity, p1 free elsewhere
  const result = reg.cancel(blocker);
  assert.deepEqual(result.promoted, [entry]);
  assert.deepEqual(reg.scheduleFor('B').map((b) => b.attendees.slice()), [['p1']]);
});
