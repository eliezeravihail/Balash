/**
 * Falsifier suite T1–T15 from ARCHITECTURE.md §7.
 *
 * Each test is named for its table row and asserts through the public seam
 * only: createRoomBook / book / schedule and the two exported error types.
 * Every test runs against a fresh createRoomBook() instance unless the row
 * says otherwise (T14 uses two).
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  createRoomBook,
  InvalidIntervalError,
  BookingConflictError,
} from './roombook.js';

test('T1: half-open boundary — touching intervals [10,20) and [20,30) both succeed', () => {
  const { book, schedule } = createRoomBook();
  book('A', 10, 20, 'olga');
  book('A', 20, 30, 'pete');
  assert.equal(schedule('A').length, 2);
});

test('T2: identical interval rejected — booking A [10,20) twice throws BookingConflictError', () => {
  const { book } = createRoomBook();
  book('A', 10, 20, 'olga');
  assert.throws(() => book('A', 10, 20, 'pete'), BookingConflictError);
});

test('T3a: containment rejected — new [20,30) inside existing [10,40)', () => {
  const { book } = createRoomBook();
  book('A', 10, 40, 'olga');
  assert.throws(() => book('A', 20, 30, 'pete'), BookingConflictError);
});

test('T3b: containment rejected — new [10,40) surrounds existing [20,30)', () => {
  const { book } = createRoomBook();
  book('A', 20, 30, 'olga');
  assert.throws(() => book('A', 10, 40, 'pete'), BookingConflictError);
});

test('T4a: partial overlap rejected — new [20,40) starts inside existing [10,30)', () => {
  const { book } = createRoomBook();
  book('A', 10, 30, 'olga');
  assert.throws(() => book('A', 20, 40, 'pete'), BookingConflictError);
});

test('T4b: partial overlap rejected — new [10,30) ends inside existing [20,40)', () => {
  const { book } = createRoomBook();
  book('A', 20, 40, 'olga');
  assert.throws(() => book('A', 10, 30, 'pete'), BookingConflictError);
});

test('T5: rooms fully independent — A [10,20) exists, B [10,20) succeeds', () => {
  const { book, schedule } = createRoomBook();
  book('A', 10, 20, 'olga');
  book('B', 10, 20, 'pete');
  assert.equal(schedule('A').length, 1);
  assert.equal(schedule('B').length, 1);
});

test('T6: unknown/empty room — schedule("never-used") is [] (an array, not an error)', () => {
  const { schedule } = createRoomBook();
  const result = schedule('never-used');
  assert.ok(Array.isArray(result));
  assert.deepEqual(result, []);
});

test('T7: schedule ordered by start regardless of insertion order', () => {
  const { book, schedule } = createRoomBook();
  book('A', 50, 60, 'olga');
  book('A', 10, 20, 'pete');
  book('A', 30, 40, 'quinn');
  assert.deepEqual(schedule('A').map((b) => b.start), [10, 30, 50]);
});

test('T8: end <= start rejected, incl. zero length — [20,20) and [30,20) throw InvalidIntervalError', () => {
  const { book } = createRoomBook();
  assert.throws(() => book('A', 20, 20, 'olga'), InvalidIntervalError);
  assert.throws(() => book('A', 30, 20, 'olga'), InvalidIntervalError);
});

test('T9: non-integer times rejected — [10.5,20), [10,NaN), ["10",20) throw InvalidIntervalError', () => {
  const { book } = createRoomBook();
  assert.throws(() => book('A', 10.5, 20, 'olga'), InvalidIntervalError);
  assert.throws(() => book('A', 10, NaN, 'olga'), InvalidIntervalError);
  assert.throws(() => book('A', '10', 20, 'olga'), InvalidIntervalError);
});

test('T10: rejected call leaves no trace — schedule unchanged, later booking succeeds', () => {
  const { book, schedule } = createRoomBook();
  book('A', 10, 30, 'olga');
  const before = schedule('A');
  assert.throws(() => book('A', 20, 40, 'pete'), BookingConflictError); // T4-style
  assert.deepEqual(schedule('A'), before);
  const id = book('A', 100, 110, 'quinn');
  const after = schedule('A');
  assert.deepEqual(after.slice(0, before.length), before);
  assert.equal(after.length, before.length + 1);
  assert.equal(after[after.length - 1].id, id);
});

test('T10 (rejection creates no room key): invalid + conflicting-style rejections on a fresh room leave schedule empty', () => {
  // Same §3 commit-last guarantee as T10, exercised on a never-booked room:
  // a rejected call must not create the room key either.
  const { book, schedule } = createRoomBook();
  assert.throws(() => book('Z', 20, 10, 'olga'), InvalidIntervalError);
  assert.deepEqual(schedule('Z'), []);
});

test('T11: rejection kinds distinguishable at the seam by instanceof and name', () => {
  const { book } = createRoomBook();

  let invalid;
  try {
    book('A', 20, 20, 'olga'); // T8-style
  } catch (err) {
    invalid = err;
  }
  assert.ok(invalid instanceof InvalidIntervalError);
  assert.ok(!(invalid instanceof BookingConflictError));
  assert.equal(invalid.name, 'InvalidIntervalError');

  let nonInteger;
  try {
    book('A', 10.5, 20, 'olga'); // T9-style
  } catch (err) {
    nonInteger = err;
  }
  assert.ok(nonInteger instanceof InvalidIntervalError);
  assert.ok(!(nonInteger instanceof BookingConflictError));

  book('A', 10, 20, 'olga');
  let conflict;
  try {
    book('A', 10, 20, 'pete'); // T2-style
  } catch (err) {
    conflict = err;
  }
  assert.ok(conflict instanceof BookingConflictError);
  assert.ok(!(conflict instanceof InvalidIntervalError));
  assert.equal(conflict.name, 'BookingConflictError');
});

test('T12: id uniqueness across rooms — three bookings in A, B, C yield three distinct ids', () => {
  const { book } = createRoomBook();
  const ids = [
    book('A', 10, 20, 'olga'),
    book('B', 10, 20, 'pete'),
    book('C', 5, 15, 'quinn'),
  ];
  for (const id of ids) assert.equal(typeof id, 'string');
  assert.equal(new Set(ids).size, 3);
});

test('T13: seam cannot corrupt the store — fresh array per call, frozen records', () => {
  const { book, schedule } = createRoomBook();
  book('A', 10, 20, 'olga');
  book('A', 30, 40, 'pete');

  const snapshot = schedule('A');
  snapshot.push({ id: 'fake', room: 'A', start: 50, end: 60, organizer: 'mallory' });
  snapshot.splice(0, 1);

  const record = schedule('A')[0];
  assert.ok(Object.isFrozen(record));
  assert.throws(() => {
    'use strict';
    record.start = 999;
  }, TypeError);

  const fresh = schedule('A');
  assert.equal(fresh.length, 2);
  assert.deepEqual(fresh.map((b) => b.start), [10, 30]);
  assert.equal(fresh[0].start, 10);
  assert.notEqual(fresh, snapshot);
});

test('T14: instance isolation — booking in one createRoomBook() is invisible to another', () => {
  const one = createRoomBook();
  const two = createRoomBook();
  one.book('A', 10, 20, 'olga');
  assert.deepEqual(two.schedule('A'), []);
  // and the other room-book still works independently
  two.book('A', 10, 20, 'pete');
  assert.equal(one.schedule('A').length, 1);
  assert.equal(two.schedule('A').length, 1);
});

test('T15: book/schedule agree — returned id names exactly one record with matching fields', () => {
  const { book, schedule } = createRoomBook();
  book('A', 30, 40, 'someone-else');
  const id = book('A', 10, 20, 'olga');
  const matches = schedule('A').filter((b) => b.id === id);
  assert.equal(matches.length, 1);
  const [record] = matches;
  assert.equal(record.room, 'A');
  assert.equal(record.start, 10);
  assert.equal(record.end, 20);
  assert.equal(record.organizer, 'olga');
});

// ---------------------------------------------------------------------------
// Falsifier suite T16–T29 from ARCHITECTURE.md §7 (stage 2).
//
// Same discipline as T1–T15: each test is named for its table row and asserts
// through the public seam only — createRoomBook / book / bookRecurring /
// schedule / cancel and the four exported error types. T1–T15 above are the
// stage-2 regression gate and remain byte-for-byte the stage-1 suite; the two
// stage-2 error types are imported here (import declarations are hoisted) so
// nothing above this line changes.
import { InvalidRecurrenceError, UnknownBookingError } from './roombook.js';

test('T16: recurring scenario end-to-end — 3 distinct string ids, occurrences are ordinary frozen bookings', () => {
  const { bookRecurring, schedule } = createRoomBook();
  const ids = bookRecurring('A', 60, 120, 'team', { everyMinutes: 1440, count: 3 });
  assert.ok(Array.isArray(ids));
  assert.equal(ids.length, 3);
  for (const id of ids) assert.equal(typeof id, 'string');
  assert.equal(new Set(ids).size, 3);
  const sched = schedule('A');
  assert.deepEqual(
    sched.map((b) => [b.start, b.end]),
    [[60, 120], [1500, 1560], [2940, 3000]]
  );
  for (const b of sched) {
    assert.ok(Object.isFrozen(b));
    assert.equal(b.room, 'A');
    assert.equal(b.organizer, 'team');
  }
});

test('T17: occurrence-order id array — ids[i] names occurrence i; the array is fresh and caller-owned', () => {
  const { bookRecurring, schedule } = createRoomBook();
  const ids = bookRecurring('A', 60, 120, 'team', { everyMinutes: 1440, count: 3 });
  const byId = new Map(schedule('A').map((b) => [b.id, b]));
  assert.deepEqual([byId.get(ids[0]).start, byId.get(ids[0]).end], [60, 120]);
  assert.deepEqual([byId.get(ids[1]).start, byId.get(ids[1]).end], [1500, 1560]);
  assert.deepEqual([byId.get(ids[2]).start, byId.get(ids[2]).end], [2940, 3000]);
  // fresh and caller-owned: mutating it shows no effect through the seam
  ids.length = 0;
  ids.push('bk-999');
  assert.deepEqual(
    schedule('A').map((b) => [b.start, b.end]),
    [[60, 120], [1500, 1560], [2940, 3000]]
  );
});

test('T18: all-or-nothing by construction — later-occurrence conflict leaves no partial trace; occurrence 0 slot still bookable', () => {
  const { book, bookRecurring, schedule } = createRoomBook();
  book('A', 2940, 3000, 'olga'); // collides with occurrence 2 of the series
  const before = schedule('A');
  assert.throws(
    () => bookRecurring('A', 60, 120, 'team', { everyMinutes: 1440, count: 3 }),
    BookingConflictError
  );
  assert.deepEqual(schedule('A'), before); // byte-identical to before the call
  // the slot occurrence 0 would have taken is still bookable
  book('A', 60, 120, 'pete');
  assert.deepEqual(
    schedule('A').map((b) => [b.start, b.end]),
    [[60, 120], [2940, 3000]]
  );
});

test('T19: intra-series self-overlap (stride < duration) rejected whole via the batch-vs-batch check', () => {
  const { bookRecurring, schedule } = createRoomBook();
  assert.throws(
    () => bookRecurring('A', 0, 60, 'team', { everyMinutes: 30, count: 2 }),
    BookingConflictError
  );
  assert.deepEqual(schedule('A'), []);
});

test('T20: touching stride (everyMinutes == duration) succeeds — half-open predicate in the batch check', () => {
  const { bookRecurring, schedule } = createRoomBook();
  bookRecurring('A', 0, 60, 'team', { everyMinutes: 60, count: 3 });
  assert.deepEqual(
    schedule('A').map((b) => [b.start, b.end]),
    [[0, 60], [60, 120], [120, 180]]
  );
});

test('T21: count == 1 degenerate series behaves like book() — one booking, id array of length 1, cancelable', () => {
  const { bookRecurring, cancel, schedule } = createRoomBook();
  const ids = bookRecurring('A', 10, 20, 'olga', { everyMinutes: 5, count: 1 });
  assert.ok(Array.isArray(ids));
  assert.equal(ids.length, 1);
  const sched = schedule('A');
  assert.deepEqual(sched.map((b) => [b.start, b.end]), [[10, 20]]);
  assert.equal(sched[0].id, ids[0]);
  cancel(ids[0]); // cancelable like any book() id
  assert.deepEqual(schedule('A'), []);
});

test('T22: malformed recurrence — InvalidRecurrenceError each time, distinguishable by type, nothing booked', () => {
  const { bookRecurring, schedule } = createRoomBook();
  const badRecurrences = [
    { everyMinutes: 0, count: 2 },
    { everyMinutes: -10, count: 2 },
    { everyMinutes: 60, count: 0 },
    { everyMinutes: 60, count: -1 },
    { everyMinutes: 60, count: 1.5 },
    { everyMinutes: '60', count: 2 },
    undefined, // missing options
    null, // non-object
    'every day', // non-object
    42, // non-object
  ];
  for (const recurrence of badRecurrences) {
    let err;
    try {
      bookRecurring('A', 10, 20, 'olga', recurrence);
    } catch (e) {
      err = e;
    }
    const shown = JSON.stringify(recurrence) ?? String(recurrence);
    assert.ok(err instanceof InvalidRecurrenceError,
      `expected InvalidRecurrenceError for recurrence ${shown}`);
    assert.ok(!(err instanceof BookingConflictError), `for recurrence ${shown}`);
    assert.ok(!(err instanceof InvalidIntervalError), `for recurrence ${shown}`);
  }
  assert.deepEqual(schedule('A'), []); // nothing booked by any of them
});

test("T23: series conflicts scoped to the series' room — rooms independent under both creating paths", () => {
  const { book, bookRecurring, schedule } = createRoomBook();
  book('B', 60, 120, 'olga');
  // succeeds despite B's booking over the same times
  bookRecurring('A', 60, 120, 'team', { everyMinutes: 1440, count: 3 });
  assert.equal(schedule('A').length, 3);
  // a failing series in A leaves schedule(B) untouched
  const bBefore = schedule('B');
  assert.throws(
    () => bookRecurring('A', 60, 120, 'other', { everyMinutes: 1440, count: 3 }),
    BookingConflictError
  );
  assert.deepEqual(schedule('B'), bBefore);
});

test('T24: cancel frees the slot for the IDENTICAL interval — removal is real, new id issued', () => {
  const { book, cancel, schedule } = createRoomBook();
  const oldId = book('A', 10, 20, 'olga');
  cancel(oldId);
  const newId = book('A', 10, 20, 'pete');
  assert.notEqual(newId, oldId);
  const sched = schedule('A');
  assert.equal(sched.length, 1);
  assert.equal(sched[0].id, newId);
});

test('T25: occurrence canceled individually — siblings intact under original ids, middle slot rebookable', () => {
  const { book, bookRecurring, cancel, schedule } = createRoomBook();
  const ids = bookRecurring('A', 60, 120, 'team', { everyMinutes: 1440, count: 3 });
  cancel(ids[1]);
  assert.deepEqual(
    schedule('A').map((b) => [b.id, b.start, b.end]),
    [[ids[0], 60, 120], [ids[2], 2940, 3000]]
  );
  book('A', 1500, 1560, 'newcomer'); // the freed middle slot is rebookable
  assert.equal(schedule('A').length, 3);
});

test('T26: dead id — double-cancel and never-issued both UnknownBookingError, distinct from the other three types', () => {
  const { book, cancel } = createRoomBook();
  const id = book('A', 10, 20, 'olga');
  cancel(id);
  let doubled;
  try {
    cancel(id); // second cancel of the same id
  } catch (e) {
    doubled = e;
  }
  assert.ok(doubled instanceof UnknownBookingError);
  assert.equal(doubled.name, 'UnknownBookingError');

  const fresh = createRoomBook();
  for (const deadId of ['bk-999', 'nonsense']) {
    let err;
    try {
      fresh.cancel(deadId);
    } catch (e) {
      err = e;
    }
    assert.ok(err instanceof UnknownBookingError, `for id ${deadId}`);
    assert.equal(err.name, 'UnknownBookingError');
    assert.ok(!(err instanceof InvalidIntervalError));
    assert.ok(!(err instanceof BookingConflictError));
    assert.ok(!(err instanceof InvalidRecurrenceError));
  }
});

test('T27: cancel removes exactly one booking — other bookings and other rooms untouched', () => {
  const { book, cancel, schedule } = createRoomBook();
  const target = book('A', 10, 20, 'olga');
  book('A', 30, 40, 'pete');
  book('B', 10, 20, 'quinn');
  const bBefore = schedule('B');
  cancel(target);
  assert.deepEqual(schedule('A').map((b) => [b.start, b.end]), [[30, 40]]);
  assert.deepEqual(schedule('B'), bBefore);
});

test('T28: contractual check order — validity before conflict, interval gate before recurrence gate', () => {
  const { book, bookRecurring } = createRoomBook();
  book('A', 10, 30, 'olga');
  // non-integer AND inside the existing booking → invalid, not conflict
  assert.throws(() => book('A', 20.5, 25, 'pete'), InvalidIntervalError);
  // same via bookRecurring
  assert.throws(
    () => bookRecurring('A', 20.5, 25, 'pete', { everyMinutes: 60, count: 2 }),
    InvalidIntervalError
  );
  // invalid interval AND invalid recurrence → the interval gate reports first
  assert.throws(
    () => bookRecurring('A', 20, 10, 'pete', { everyMinutes: 0, count: 0 }),
    InvalidIntervalError
  );
});

test('T29: rejected/failed operations of ALL kinds leave no observable trace — schedule matches exactly the successful operations', () => {
  const rb = createRoomBook();
  rb.book('A', 2940, 3000, 'olga');
  // T18-style rejected series in A
  assert.throws(
    () => rb.bookRecurring('A', 60, 120, 'team', { everyMinutes: 1440, count: 3 }),
    BookingConflictError
  );
  // T26-style failed cancels: never-issued, then double-cancel
  assert.throws(() => rb.cancel('bk-999'), UnknownBookingError);
  const bId = rb.book('B', 10, 20, 'pete');
  rb.cancel(bId);
  assert.throws(() => rb.cancel(bId), UnknownBookingError);
  // invalid inputs of both kinds
  assert.throws(
    () => rb.bookRecurring('A', 5, 5, 'x', { everyMinutes: 1, count: 1 }),
    InvalidIntervalError
  );
  assert.throws(
    () => rb.bookRecurring('A', 5, 10, 'x', { everyMinutes: 0, count: 1 }),
    InvalidRecurrenceError
  );
  // a later book succeeds and the seam shows exactly the successful operations
  // (id values themselves are NOT asserted — ids are opaque per §2)
  rb.book('A', 60, 120, 'quinn');
  assert.deepEqual(
    rb.schedule('A').map((b) => [b.start, b.end, b.organizer]),
    [[60, 120, 'quinn'], [2940, 3000, 'olga']]
  );
  assert.deepEqual(rb.schedule('B'), []);
});

// ---------------------------------------------------------------------------
// Falsifier suite T30–T43 from ARCHITECTURE.md §7 (stage 3).
//
// Same discipline: each test is named for its table row and asserts through
// the public seam only. All waitlist state is asserted THROUGH BEHAVIOR only
// (the queue has no read operation): an entry "is queued" iff a suitable
// later cancel materializes it as a booking; an entry "is gone" iff no later
// cancel ever re-materializes it. T1–T29 above are the stage-3 regression
// gate and remain byte-for-byte the stage-1/2 suites; the stage-3 error type
// is imported here (import declarations are hoisted) so nothing above this
// line changes.
import { NoConflictError } from './roombook.js';

test('T30: join-only-on-conflict gate — bookable interval throws NoConflictError; rejected join leaves no trace', () => {
  const { book, joinWaitlist, cancel, schedule } = createRoomBook();
  const id = book('A', 10, 20, 'olga');
  let err;
  try {
    joinWaitlist('A', 30, 40, 'pete'); // currently bookable
  } catch (e) {
    err = e;
  }
  assert.ok(err instanceof NoConflictError);
  assert.ok(!(err instanceof BookingConflictError));
  assert.ok(!(err instanceof InvalidIntervalError));
  assert.equal(err.name, 'NoConflictError');
  // nothing was queued: canceling the only booking promotes nothing
  cancel(id);
  assert.deepEqual(schedule('A'), []);
});

test('T31: same interval rule through the same gate as bookings; validity before the conflict-required gate', () => {
  const { joinWaitlist } = createRoomBook();
  for (const [start, end] of [[20, 20], [30, 20], [10.5, 20], [10, NaN]]) {
    assert.throws(
      () => joinWaitlist('A', start, end, 'pete'),
      InvalidIntervalError,
      `for interval [${start}, ${end})`
    );
  }
  // invalid AND non-conflicting (empty room): the validity gate reports first
  let err;
  try {
    joinWaitlist('A', 20, 10, 'pete');
  } catch (e) {
    err = e;
  }
  assert.ok(err instanceof InvalidIntervalError);
  assert.ok(!(err instanceof NoConflictError));
});

test('T32: GOALS scenario end-to-end — promotion is a real ordinary booking via the one authority; entry leaves the queue', () => {
  const rb = createRoomBook();
  const olgaId = rb.book('A', 0, 30, 'olga');
  assert.equal(rb.joinWaitlist('A', 0, 30, 'pete'), undefined);
  rb.cancel(olgaId);
  const sched = rb.schedule('A');
  assert.equal(sched.length, 1);
  const [promoted] = sched;
  assert.ok(Object.isFrozen(promoted));
  assert.equal(promoted.room, 'A');
  assert.equal(promoted.start, 0);
  assert.equal(promoted.end, 30);
  assert.equal(promoted.organizer, 'pete');
  assert.equal(typeof promoted.id, 'string');
  assert.notEqual(promoted.id, olgaId);
  // the entry left the queue at promotion — nothing re-promotes
  rb.cancel(promoted.id);
  assert.deepEqual(rb.schedule('A'), []);
  assert.deepEqual(rb.schedule('A'), []); // and stays []
});

test('T33: multi-fit cascade — promote ALL that fit in join order, in one cancel', () => {
  const rb = createRoomBook();
  const big = rb.book('A', 0, 60, 'big');
  rb.joinWaitlist('A', 0, 30, 'w1');
  rb.joinWaitlist('A', 30, 60, 'w2');
  rb.cancel(big);
  const sched = rb.schedule('A');
  assert.deepEqual(
    sched.map((b) => [b.start, b.end, b.organizer]),
    [[0, 30, 'w1'], [30, 60, 'w2']] // BOTH promoted in the one cancel
  );
  // canceling each promoted booking then empties A permanently
  for (const b of sched) rb.cancel(b.id);
  assert.deepEqual(rb.schedule('A'), []);
});

test('T34: queue-order skip — earliest incompatible entry stays queued; later compatible entry promotes; skipped entry promotes on a later cancel', () => {
  const rb = createRoomBook();
  const b1 = rb.book('A', 0, 30, 'b1');
  const b2 = rb.book('A', 30, 60, 'b2');
  rb.joinWaitlist('A', 20, 40, 'w1'); // conflicts both bookings
  rb.joinWaitlist('A', 0, 20, 'w2');  // conflicts b1
  rb.cancel(b1);
  // w1 NOT promoted (overlaps remaining b2); w2 promoted
  assert.deepEqual(
    rb.schedule('A').map((b) => [b.start, b.end, b.organizer]),
    [[0, 20, 'w2'], [30, 60, 'b2']]
  );
  rb.cancel(b2);
  // w1 [20,40) now fits beside [0,20) and promotes
  assert.deepEqual(
    rb.schedule('A').map((b) => [b.start, b.end, b.organizer]),
    [[0, 20, 'w2'], [20, 40, 'w1']]
  );
});

test('T35: overlapping compatible entries — join order wins; the later stays queued and provably unbookable', () => {
  const rb = createRoomBook();
  const blocker = rb.book('A', 0, 30, 'blocker');
  rb.joinWaitlist('A', 0, 30, 'w1');
  rb.joinWaitlist('A', 10, 40, 'w2'); // overlaps w1; both conflict with blocker
  rb.cancel(blocker);
  const sched = rb.schedule('A');
  // w1 (earlier) promoted; w2 stays queued (conflicts w1's new booking)
  assert.deepEqual(sched.map((b) => [b.start, b.end, b.organizer]), [[0, 30, 'w1']]);
  // quiescence probe: w2's interval is unbookable between operations
  assert.throws(() => rb.book('A', 10, 40, 'direct'), BookingConflictError);
  rb.cancel(sched[0].id);
  assert.deepEqual(
    rb.schedule('A').map((b) => [b.start, b.end, b.organizer]),
    [[10, 40, 'w2']] // w2 promotes
  );
});

test('T36: promotion respects no-overlap against REMAINING bookings; an unpromotable freed slot stays directly free', () => {
  const rb = createRoomBook();
  const b1 = rb.book('A', 0, 30, 'b1');
  rb.book('A', 30, 60, 'b2');
  rb.joinWaitlist('A', 25, 45, 'w'); // conflicts both
  rb.cancel(b1);
  // w NOT promoted: it overlaps the remaining b2
  assert.deepEqual(rb.schedule('A').map((b) => [b.start, b.end]), [[30, 60]]);
  // no reservation ghost: the freed space is directly bookable
  rb.book('A', 0, 25, 'direct');
  assert.deepEqual(rb.schedule('A').map((b) => [b.start, b.end]), [[0, 25], [30, 60]]);
});

test('T37: cancel with empty or all-incompatible waitlist is exactly stage-2 cancel', () => {
  // (a) empty waitlist — T24 shape intact
  {
    const rb = createRoomBook();
    const oldId = rb.book('A', 10, 20, 'olga');
    rb.cancel(oldId);
    const newId = rb.book('A', 10, 20, 'pete');
    assert.notEqual(newId, oldId);
    assert.deepEqual(
      rb.schedule('A').map((b) => [b.id, b.start, b.end]),
      [[newId, 10, 20]]
    );
  }
  // (b) all-incompatible waitlist
  {
    const rb = createRoomBook();
    const b1 = rb.book('A', 0, 30, 'b1');
    rb.book('A', 30, 60, 'b2');
    rb.joinWaitlist('A', 35, 55, 'w'); // conflicts b2 only
    rb.cancel(b1);
    // nothing promoted; only b2 remains
    assert.deepEqual(rb.schedule('A').map((b) => [b.start, b.end]), [[30, 60]]);
    // the freed [0,30) is rebookable identically
    rb.book('A', 0, 30, 'again');
    assert.deepEqual(rb.schedule('A').map((b) => [b.start, b.end]), [[0, 30], [30, 60]]);
  }
});

test('T38: a promoted booking is ordinary — frozen stage-1 shape, cancelable, re-triggers promotion; duplicates coherent', () => {
  const rb = createRoomBook();
  const blocker = rb.book('A', 0, 30, 'blocker');
  rb.joinWaitlist('A', 0, 30, 'pete');  // w1
  rb.joinWaitlist('A', 0, 30, 'quinn'); // w2 — DUPLICATE interval, different requester
  rb.cancel(blocker);
  let sched = rb.schedule('A');
  assert.equal(sched.length, 1);
  const w1Booking = sched[0];
  assert.ok(Object.isFrozen(w1Booking));
  assert.equal(typeof w1Booking.id, 'string');
  assert.equal(w1Booking.organizer, 'pete');
  // record shape unchanged: no extra fields
  assert.deepEqual(
    Object.keys(w1Booking).sort(),
    ['end', 'id', 'organizer', 'room', 'start']
  );
  // an ordinary cancel of the promoted booking re-triggers the cascade
  rb.cancel(w1Booking.id);
  sched = rb.schedule('A');
  assert.deepEqual(sched.map((b) => [b.start, b.end, b.organizer]), [[0, 30, 'quinn']]);
  rb.cancel(sched[0].id);
  assert.deepEqual(rb.schedule('A'), []); // A empty permanently
});

test("T39: per-room isolation — a cancel examines only the freed room's queue", () => {
  const rb = createRoomBook();
  const aId = rb.book('A', 0, 30, 'a-org');
  const bId = rb.book('B', 0, 30, 'b-org');
  rb.joinWaitlist('B', 0, 30, 'wb'); // conflicts in B
  rb.cancel(aId);
  // schedule(B) unchanged: wb NOT promoted by A's cancel
  assert.deepEqual(
    rb.schedule('B').map((b) => [b.start, b.end, b.organizer]),
    [[0, 30, 'b-org']]
  );
  assert.deepEqual(rb.schedule('A'), []);
  rb.cancel(bId);
  assert.deepEqual(
    rb.schedule('B').map((b) => [b.start, b.end, b.organizer]),
    [[0, 30, 'wb']] // wb promotes in B
  );
});

test('T40: instance isolation extends to waitlists — factory closure confines both maps', () => {
  const one = createRoomBook();
  const two = createRoomBook();
  const oneId = one.book('A', 0, 30, 'olga');
  one.joinWaitlist('A', 0, 30, 'pete');
  const twoId = two.book('A', 0, 30, 'quinn');
  two.cancel(twoId);
  assert.deepEqual(two.schedule('A'), []); // no promotion from #1's queue
  assert.deepEqual(
    one.schedule('A').map((b) => [b.start, b.end, b.organizer]),
    [[0, 30, 'olga']] // #1 unchanged
  );
  one.cancel(oneId); // #1's own cancel then promotes its entry
  assert.deepEqual(
    one.schedule('A').map((b) => [b.start, b.end, b.organizer]),
    [[0, 30, 'pete']]
  );
});

test('T41: seam leaks nothing — join returns undefined, no queue residue in schedule, five stage-1 fields only', () => {
  const rb = createRoomBook();
  rb.book('A', 0, 60, 'big');
  // T33's setup, before its cancel
  assert.equal(rb.joinWaitlist('A', 0, 30, 'w1'), undefined);
  assert.equal(rb.joinWaitlist('A', 30, 60, 'w2'), undefined);
  const sched = rb.schedule('A');
  // ONLY [0,60) big — no queue residue in schedule
  assert.deepEqual(sched.map((b) => [b.start, b.end, b.organizer]), [[0, 60, 'big']]);
  assert.deepEqual(
    Object.keys(sched[0]).sort(),
    ['end', 'id', 'organizer', 'room', 'start']
  );
});

test('T42: quiescence sweep — between operations, no queued entry could be successfully booked', () => {
  // Replays T33–T39's scenarios; after EVERY public call, a direct book() of
  // each still-queued entry's exact room+interval must throw
  // BookingConflictError. The probe itself is a rejected call, so by T10's
  // guarantee it leaves no trace and cannot perturb the scenario.
  const probe = (rb, queued) => {
    for (const [room, start, end] of queued) {
      assert.throws(
        () => rb.book(room, start, end, 'quiescence-probe'),
        BookingConflictError,
        `queued entry ${room} [${start}, ${end}) must not be bookable between operations`
      );
    }
  };

  // T33 scenario
  {
    const rb = createRoomBook();
    const big = rb.book('A', 0, 60, 'big');           probe(rb, []);
    rb.joinWaitlist('A', 0, 30, 'w1');                probe(rb, [['A', 0, 30]]);
    rb.joinWaitlist('A', 30, 60, 'w2');               probe(rb, [['A', 0, 30], ['A', 30, 60]]);
    rb.cancel(big);                                   probe(rb, []); // both promoted
    const ids = rb.schedule('A').map((b) => b.id);
    rb.cancel(ids[0]);                                probe(rb, []);
    rb.cancel(ids[1]);                                probe(rb, []);
  }
  // T34 scenario
  {
    const rb = createRoomBook();
    const b1 = rb.book('A', 0, 30, 'b1');             probe(rb, []);
    const b2 = rb.book('A', 30, 60, 'b2');            probe(rb, []);
    rb.joinWaitlist('A', 20, 40, 'w1');               probe(rb, [['A', 20, 40]]);
    rb.joinWaitlist('A', 0, 20, 'w2');                probe(rb, [['A', 20, 40], ['A', 0, 20]]);
    rb.cancel(b1);                                    probe(rb, [['A', 20, 40]]); // w2 promoted, w1 queued
    rb.cancel(b2);                                    probe(rb, []); // w1 promoted
  }
  // T35 scenario
  {
    const rb = createRoomBook();
    const blocker = rb.book('A', 0, 30, 'blocker');   probe(rb, []);
    rb.joinWaitlist('A', 0, 30, 'w1');                probe(rb, [['A', 0, 30]]);
    rb.joinWaitlist('A', 10, 40, 'w2');               probe(rb, [['A', 0, 30], ['A', 10, 40]]);
    rb.cancel(blocker);                               probe(rb, [['A', 10, 40]]); // w1 promoted, w2 queued
    rb.cancel(rb.schedule('A')[0].id);                probe(rb, []); // w2 promoted
  }
  // T36 scenario
  {
    const rb = createRoomBook();
    const b1 = rb.book('A', 0, 30, 'b1');             probe(rb, []);
    rb.book('A', 30, 60, 'b2');                       probe(rb, []);
    rb.joinWaitlist('A', 25, 45, 'w');                probe(rb, [['A', 25, 45]]);
    rb.cancel(b1);                                    probe(rb, [['A', 25, 45]]); // w stays queued
    rb.book('A', 0, 25, 'direct');                    probe(rb, [['A', 25, 45]]); // still queued
  }
  // T37 scenario (b) — (a)'s waitlist is empty throughout: nothing to probe
  {
    const rb = createRoomBook();
    const b1 = rb.book('A', 0, 30, 'b1');             probe(rb, []);
    rb.book('A', 30, 60, 'b2');                       probe(rb, []);
    rb.joinWaitlist('A', 35, 55, 'w');                probe(rb, [['A', 35, 55]]);
    rb.cancel(b1);                                    probe(rb, [['A', 35, 55]]); // nothing promoted
    rb.book('A', 0, 30, 'again');                     probe(rb, [['A', 35, 55]]);
  }
  // T38 scenario
  {
    const rb = createRoomBook();
    const blocker = rb.book('A', 0, 30, 'blocker');   probe(rb, []);
    rb.joinWaitlist('A', 0, 30, 'pete');              probe(rb, [['A', 0, 30]]);
    rb.joinWaitlist('A', 0, 30, 'quinn');             probe(rb, [['A', 0, 30], ['A', 0, 30]]);
    rb.cancel(blocker);                               probe(rb, [['A', 0, 30]]); // w1 promoted, w2 queued
    rb.cancel(rb.schedule('A')[0].id);                probe(rb, []); // w2 promoted
    rb.cancel(rb.schedule('A')[0].id);                probe(rb, []);
  }
  // T39 scenario
  {
    const rb = createRoomBook();
    const aId = rb.book('A', 0, 30, 'a-org');         probe(rb, []);
    const bId = rb.book('B', 0, 30, 'b-org');         probe(rb, []);
    rb.joinWaitlist('B', 0, 30, 'wb');                probe(rb, [['B', 0, 30]]);
    rb.cancel(aId);                                   probe(rb, [['B', 0, 30]]); // wb still queued
    rb.cancel(bId);                                   probe(rb, []); // wb promoted
  }
});

test('T43: regression gate — stage-1/2 behavior unchanged; public surface exactly the stage contract', async () => {
  // The byte-for-byte half of this gate is structural and holds by
  // construction of this file: T1–T29 above ARE the stage-1/2 suites,
  // untouched (all stage-3 additions are append-only), and they pass in this
  // very run.
  //
  // The two trailing surface assertions of this test (the stage-3 export array
  // and the five-function instance array) were REMOVED in the stage-4
  // implementation round by Guide decision (ARCHITECTURE.md §7, "the T43
  // surface pin"): the GOALS-mandated seam growth — the `setCapacity` key and
  // the four new error exports — necessarily falsifies a stage-3 surface pin,
  // so the grown surface is pinned exactly ONCE, by T60 below. Everything else
  // in this test file above T44 is byte-for-byte unchanged.
});

// ---------------------------------------------------------------------------
// Falsifier suite T44–T60 from ARCHITECTURE.md §7 (stage 4).
//
// Same discipline: each test is named for its table row and asserts through
// the public seam only. Attendee-carrying state is asserted THROUGH BEHAVIOR
// ONLY — capacity via acceptance/rejection, person-overlap via rejection and
// promotion, queue state via the book-probe (the queue and capacities have no
// read operation). T1–T43 above are the regression gate and remain byte-for-
// byte the stage-1/2/3 suites (minus T43's two removed surface asserts — see
// its note). The four stage-4 error types are imported here (import
// declarations are hoisted) so nothing above this line changes.
import {
  InvalidCapacityError,
  InvalidAttendeesError,
  CapacityExceededError,
  PersonConflictError,
} from './roombook.js';

// N distinct opaque attendee ids: ids(5) => ['p0','p1','p2','p3','p4'].
const ids = (n) => Array.from({ length: n }, (_, i) => `p${i}`);

test('T44: capacity-value gate — bad values throw InvalidCapacityError; a failed declaration writes nothing', () => {
  const { setCapacity, book, schedule } = createRoomBook();
  for (const v of [-1, 1.5, '4', NaN, Infinity, null, undefined]) {
    let err;
    try {
      setCapacity('A', v);
    } catch (e) {
      err = e;
    }
    assert.ok(err instanceof InvalidCapacityError, `for capacity ${String(v)}`);
    assert.equal(err.name, 'InvalidCapacityError');
    assert.ok(!(err instanceof InvalidIntervalError));
    assert.ok(!(err instanceof InvalidRecurrenceError));
    assert.ok(!(err instanceof InvalidAttendeesError));
  }
  // Every declaration failed → A is still undeclared/unlimited: 5 attendees ok.
  book('A', 0, 30, 'olga', ids(5));
  assert.equal(schedule('A').length, 1);
});

test('T45: capacity gate at the authority — > rejected, == accepted; rejection leaves no trace; setCapacity returns undefined', () => {
  const { setCapacity, book, schedule } = createRoomBook();
  assert.equal(setCapacity('A', 4), undefined);
  let err;
  try {
    book('A', 0, 30, 'olga', ids(5)); // 5 > 4
  } catch (e) {
    err = e;
  }
  assert.ok(err instanceof CapacityExceededError);
  assert.equal(err.name, 'CapacityExceededError');
  assert.ok(!(err instanceof BookingConflictError));
  assert.deepEqual(schedule('A'), []); // rejection left no trace; slot still free
  const id = book('A', 0, 30, 'pete', ids(4)); // count == capacity passes
  assert.deepEqual(schedule('A').map((b) => [b.id, b.start, b.end]), [[id, 0, 30]]);
});

test('T46: capacity 0 semantics — omitted ≡ empty list; empty passes every capacity; one attendee rejected', () => {
  const { setCapacity, book, schedule } = createRoomBook();
  setCapacity('A', 0);
  book('A', 0, 30, 'olga');           // attendees omitted ≡ empty → passes cap 0
  book('A', 40, 50, 'pete', []);      // explicit empty → passes cap 0
  assert.throws(() => book('A', 60, 70, 'quinn', ids(1)), CapacityExceededError);
  assert.deepEqual(schedule('A').map((b) => [b.start, b.end]), [[0, 30], [40, 50]]);
});

test('T47: undeclared room is unlimited — a big attendee list on an undeclared room succeeds', () => {
  const { book, schedule } = createRoomBook();
  const id = book('A', 0, 30, 'org', ids(50));
  assert.equal(schedule('A').length, 1);
  assert.equal(schedule('A')[0].id, id);
});

test('T48: re-declare overwrites (future creations only); lowering evicts nothing and enables nothing', () => {
  const { setCapacity, book, joinWaitlist, schedule } = createRoomBook();
  setCapacity('A', 2);
  const id0 = book('A', 0, 30, 'olga', ids(2)); // count == 2, ok
  const before = schedule('A');
  setCapacity('A', 1); // lowering
  assert.deepEqual(schedule('A'), before); // nothing evicted — id0 (2 attendees) intact
  assert.throws(() => book('A', 40, 50, 'pete', ids(2)), CapacityExceededError); // 2 > 1
  const id1 = book('A', 40, 50, 'quinn', ids(1)); // 1 == 1, ok (future creations)
  assert.deepEqual(
    schedule('A').map((b) => b.id),
    [id0, id1]
  );
  // a queued over-capacity entry present: lowering/equal triggers NO promotion
  joinWaitlist('A', 0, 30, 'w', ids(2)); // A[0,30) occupied by id0 → queued
  setCapacity('A', 1); // re-declare equal (not a raise) → no promotion pass
  assert.deepEqual(schedule('A').map((b) => b.id), [id0, id1]); // w did not materialize
  // and the entry is still queued (its slot unbookable — quiescence probe)
  assert.throws(() => book('A', 0, 30, 'probe'), BookingConflictError);
});

test('T49: the one attendees gate on all three ops; element opacity; validity gate order', () => {
  const rb = createRoomBook();
  // duplicates rejected on book, bookRecurring, AND joinWaitlist — no trace
  assert.throws(() => rb.book('A', 0, 30, 'o', ['p1', 'p1']), InvalidAttendeesError);
  assert.throws(
    () => rb.bookRecurring('A', 0, 30, 'o', { everyMinutes: 60, count: 2 }, ['p1', 'p1']),
    InvalidAttendeesError
  );
  // joinWaitlist needs a room conflict to reach a non-validity gate; the
  // attendees gate is BEFORE the conflict-required gate, so an empty room
  // still reports the attendees error.
  assert.throws(() => rb.joinWaitlist('A', 0, 30, 'r', ['p1', 'p1']), InvalidAttendeesError);
  assert.deepEqual(rb.schedule('A'), []); // nothing created or queued by any of them

  // non-array attendees rejected
  for (const bad of ['p1', 7, {}]) {
    assert.throws(() => rb.book('B', 0, 30, 'o', bad), InvalidAttendeesError, `for ${String(bad)}`);
  }
  // weird opaque ids accepted — elements are NOT type-checked
  rb.book('C', 0, 30, 'o', ['', '🦆', 'p 1']);
  assert.equal(rb.schedule('C').length, 1);

  // contractual gate order:
  // invalid interval + duplicates → InvalidIntervalError (interval first)
  assert.throws(() => rb.book('D', 20, 10, 'o', ['p1', 'p1']), InvalidIntervalError);
  // bad recurrence + duplicates → InvalidRecurrenceError (recurrence before attendees)
  assert.throws(
    () => rb.bookRecurring('D', 0, 30, 'o', { everyMinutes: 0, count: 1 }, ['p1', 'p1']),
    InvalidRecurrenceError
  );
  // valid inputs + duplicates + would-conflict → InvalidAttendeesError (validity before authority)
  rb.book('E', 0, 30, 'blocker');
  assert.throws(() => rb.book('E', 0, 30, 'o', ['p1', 'p1']), InvalidAttendeesError);
});

test('T50: organizer is NOT implicitly an attendee — only listed ids are checked', () => {
  const rb = createRoomBook();
  rb.book('A', 0, 30, 'x', ['p1']);
  // organizer 'p1' in another room over an overlapping interval → succeeds:
  // the organizer label is not treated as an attendee (were it one, it would
  // person-conflict with A's listed p1).
  rb.book('B', 10, 20, 'p1');
  assert.equal(rb.schedule('B').length, 1);
  // p1 as an actual ATTENDEE, overlapping A, in a free room → PersonConflictError.
  // (Room C, not B: B[10,20) is now occupied, which would surface as a room
  // conflict first — the §3.6 room-before-person order. C isolates the person
  // rule. See the return-to-Guide note on the T50 table's room label.)
  assert.throws(() => rb.book('C', 10, 20, 'y', ['p1']), PersonConflictError);
});

test('T51: person rule domain = all rooms; half-open semantics; room-before-person order', () => {
  const rb = createRoomBook();
  rb.book('A', 0, 30, 'org', ['p1']);
  // cross-room person overlap (GOALS scenario)
  assert.throws(() => rb.book('B', 15, 25, 'org', ['p1']), PersonConflictError);
  // touching is legal (half-open): B[30,60) does not overlap A[0,30)
  rb.book('B', 30, 60, 'org', ['p1']);
  // no shared id → no person conflict
  rb.book('B', 15, 25, 'org', ['p2']);
  assert.deepEqual(
    rb.schedule('B').map((b) => [b.start, b.end]),
    [[15, 25], [30, 60]]
  );
  // same-room overlap with a shared attendee reports as a ROOM conflict, not a
  // person conflict (room leg runs first — the §3.4 subsumption consequence)
  let err;
  try {
    rb.book('A', 10, 40, 'org', ['p1']);
  } catch (e) {
    err = e;
  }
  assert.ok(err instanceof BookingConflictError);
  assert.ok(!(err instanceof PersonConflictError));
});

test('T52: all-or-nothing composes over capacity AND person — one bad occurrence rejects the whole series, no trace', () => {
  // (a) capacity: 3 attendees exceed capacity 2 → the whole series is rejected
  {
    const rb = createRoomBook();
    rb.setCapacity('A', 2);
    assert.throws(
      () => rb.bookRecurring('A', 60, 120, 'team', { everyMinutes: 1440, count: 3 }, ids(3)),
      CapacityExceededError
    );
    assert.deepEqual(rb.schedule('A'), []); // nothing written, no room key
    rb.book('A', 60, 120, 'pete'); // occurrence-0 slot still bookable
    assert.deepEqual(rb.schedule('A').map((b) => [b.start, b.end]), [[60, 120]]);
  }
  // (b) person: occurrence 2's time is p1-busy in another room → whole series rejected
  {
    const rb = createRoomBook();
    rb.book('B', 2940, 3000, 'other', ['p1']);
    const bBefore = rb.schedule('B');
    assert.throws(
      () => rb.bookRecurring('A', 60, 120, 'team', { everyMinutes: 1440, count: 3 }, ['p1']),
      PersonConflictError
    );
    assert.deepEqual(rb.schedule('A'), []);      // no ids minted, no trace
    assert.deepEqual(rb.schedule('B'), bBefore); // untouched
  }
});

test('T53: no false intra-series person conflict — the deleted batch-leg lemma', () => {
  const rb = createRoomBook();
  // p1 busy in B only at [200,300), overlapping NO occurrence
  rb.book('B', 200, 300, 'other', ['p1']);
  // own touching occurrences [0,60),[60,120),[120,180) all share ['p1','p2'] —
  // legal: the person check scans only the committed store, never the batch.
  const seriesIds = rb.bookRecurring('A', 0, 60, 'team', { everyMinutes: 60, count: 3 }, ['p1', 'p2']);
  assert.equal(seriesIds.length, 3);
  assert.deepEqual(
    rb.schedule('A').map((b) => [b.start, b.end]),
    [[0, 60], [60, 120], [120, 180]]
  );
});

test('T54: join gate unchanged — validity + conflict-required only; capacity/person NOT join gates', () => {
  // over-capacity entry is accepted at join (capacity is not a join gate)
  {
    const rb = createRoomBook();
    rb.book('A', 0, 30, 'b');       // occupies A[0,30)
    rb.setCapacity('A', 1);
    assert.equal(rb.joinWaitlist('A', 0, 30, 'w', ['p', 'q']), undefined); // 2 > cap 1, still accepted
  }
  // person-busy entry is accepted at join (person-overlap is not a join gate)
  {
    const rb = createRoomBook();
    rb.book('C', 0, 30, 'org', ['p1']); // p1 busy in C
    rb.book('A', 0, 30, 'blk');         // A[0,30) conflict so join is allowed
    assert.equal(rb.joinWaitlist('A', 0, 30, 'w2', ['p1']), undefined); // p1 busy, still accepted
  }
});

test('T55: capacity-blocked entry stays queued; a capacity RAISE is an enabling event reaching the owner', () => {
  const rb = createRoomBook();
  const b = rb.book('A', 0, 30, 'b'); // occupies A[0,30)
  rb.setCapacity('A', 1);
  rb.joinWaitlist('A', 0, 30, 'w', ['p', 'q']); // accepted (over cap; not a join gate)
  rb.cancel(b); // frees the interval, but capacity 1 < 2 attendees → w NOT promoted
  assert.deepEqual(rb.schedule('A'), []);
  assert.throws(() => rb.book('A', 0, 30, 'org', ['p', 'q']), CapacityExceededError); // probe: still blocked
  rb.setCapacity('A', 2); // strict raise → enabling event → w promotes
  assert.deepEqual(
    rb.schedule('A').map((b) => [b.start, b.end, b.organizer]),
    [[0, 30, 'w']]
  );
  // queue is now empty: cancel the promoted booking, nothing re-promotes
  rb.cancel(rb.schedule('A')[0].id);
  assert.deepEqual(rb.schedule('A'), []);
  assert.deepEqual(rb.schedule('A'), []); // stays []
});

test('T56: cross-room enabling falsifier — a person-freeing cancel in ANOTHER room promotes into B', () => {
  const rb = createRoomBook();
  const idA = rb.book('A', 0, 30, 'org', ['p1']); // p1 busy in A
  const idB = rb.book('B', 0, 30, 'org');         // B[0,30) occupied (no attendees)
  rb.joinWaitlist('B', 0, 30, 'w', ['p1']);       // valid: room conflict with idB
  rb.cancel(idB); // frees B's interval, but p1 still busy in A → w NOT promoted
  assert.deepEqual(rb.schedule('B'), []);
  assert.throws(() => rb.book('B', 0, 30, 'org', ['p1']), PersonConflictError); // probe: person-blocked
  rb.cancel(idA); // a cancel in ANOTHER room frees p1 → w promotes into B
  assert.deepEqual(
    rb.schedule('B').map((b) => [b.start, b.end, b.organizer]),
    [[0, 30, 'w']]
  );
});

test('T57: global join order — cross-room competition for one person resolves by the one instance-wide order', () => {
  const rb = createRoomBook();
  const idC = rb.book('C', 0, 30, 'org', ['p1']); // the sole obstacle for both entries
  const bA = rb.book('A', 0, 30, 'a-org');
  const bB = rb.book('B', 0, 30, 'b-org');
  rb.joinWaitlist('A', 0, 30, 'w1', ['p1']); // earlier GLOBAL join
  rb.joinWaitlist('B', 0, 30, 'w2', ['p1']); // later GLOBAL join
  rb.cancel(bA); // w1 still p1-blocked (C), w2 still room-blocked (bB) → both queued
  assert.deepEqual(rb.schedule('A'), []);
  rb.cancel(bB); // both now person-blocked by p1 in C → both stay queued
  assert.throws(() => rb.book('A', 0, 30, 'x', ['p1']), PersonConflictError);
  assert.throws(() => rb.book('B', 0, 30, 'x', ['p1']), PersonConflictError);
  rb.cancel(idC); // ONE event enables both; w1 (earlier global join) wins
  assert.deepEqual(
    rb.schedule('A').map((b) => [b.start, b.end, b.organizer]),
    [[0, 30, 'w1']]
  );
  assert.deepEqual(rb.schedule('B'), []); // w2 stays queued: person-conflicts w1's new booking
  assert.throws(() => rb.book('B', 0, 30, 'x', ['p1']), PersonConflictError);
  rb.cancel(rb.schedule('A')[0].id); // p1 frees again → w2 promotes into B
  assert.deepEqual(
    rb.schedule('B').map((b) => [b.start, b.end, b.organizer]),
    [[0, 30, 'w2']]
  );
});

test('T58: quiescence sweep over the enlarged event set — after EVERY public call no queued entry passes all four rules', () => {
  // Probe each still-queued entry via book(room, start, end, fresh-org,
  // attendees): it must throw one of the three authority answers. Each probe
  // is a rejected call, so by T10's guarantee it leaves no trace.
  const probe = (rb, queued) => {
    for (const [room, start, end, att] of queued) {
      let err;
      try {
        rb.book(room, start, end, 'quiescence-probe', att);
      } catch (e) {
        err = e;
      }
      assert.ok(
        err instanceof BookingConflictError ||
        err instanceof CapacityExceededError ||
        err instanceof PersonConflictError,
        `queued entry ${room} [${start}, ${end}) att=${JSON.stringify(att)} must not be bookable`
      );
    }
  };

  // T55 scenario — capacity block + raise, probing after EVERY setCapacity
  {
    const rb = createRoomBook();
    const b = rb.book('A', 0, 30, 'b');            probe(rb, []);
    rb.setCapacity('A', 1);                        probe(rb, []);
    rb.joinWaitlist('A', 0, 30, 'w', ['p', 'q']); probe(rb, [['A', 0, 30, ['p', 'q']]]);
    rb.cancel(b);                                  probe(rb, [['A', 0, 30, ['p', 'q']]]); // capacity-blocked
    rb.setCapacity('A', 1);                        probe(rb, [['A', 0, 30, ['p', 'q']]]); // equal: no promotion
    rb.setCapacity('A', 0);                        probe(rb, [['A', 0, 30, ['p', 'q']]]); // lower: no promotion
    rb.setCapacity('A', 2);                        probe(rb, []); // raise: w promotes
  }
  // T56 scenario — cross-room person block, freed by a cancel elsewhere
  {
    const rb = createRoomBook();
    const idA = rb.book('A', 0, 30, 'org', ['p1']);  probe(rb, []);
    const idB = rb.book('B', 0, 30, 'org');          probe(rb, []);
    rb.joinWaitlist('B', 0, 30, 'w', ['p1']);        probe(rb, [['B', 0, 30, ['p1']]]);
    rb.cancel(idB);                                  probe(rb, [['B', 0, 30, ['p1']]]); // person-blocked
    rb.cancel(idA);                                  probe(rb, []); // freed p1 → w promotes
  }
  // T57 scenario — global-join-order race
  {
    const rb = createRoomBook();
    const idC = rb.book('C', 0, 30, 'org', ['p1']);  probe(rb, []);
    const bA = rb.book('A', 0, 30, 'a-org');         probe(rb, []);
    const bB = rb.book('B', 0, 30, 'b-org');         probe(rb, []);
    rb.joinWaitlist('A', 0, 30, 'w1', ['p1']);       probe(rb, [['A', 0, 30, ['p1']]]);
    rb.joinWaitlist('B', 0, 30, 'w2', ['p1']);       probe(rb, [['A', 0, 30, ['p1']], ['B', 0, 30, ['p1']]]);
    rb.cancel(bA);                                   probe(rb, [['A', 0, 30, ['p1']], ['B', 0, 30, ['p1']]]);
    rb.cancel(bB);                                   probe(rb, [['A', 0, 30, ['p1']], ['B', 0, 30, ['p1']]]);
    rb.cancel(idC);                                  probe(rb, [['B', 0, 30, ['p1']]]); // w1 promoted, w2 queued
    rb.cancel(rb.schedule('A')[0].id);               probe(rb, []); // w2 promoted
  }
});

test('T59: attendee lists copied at the seam (inbound defense); Booking record shape unchanged', () => {
  const rb = createRoomBook();
  const arr = ['p1'];
  rb.book('A', 0, 30, 'org', arr);
  arr.push('p2'); // mutate the caller's array AFTER the call
  // the original list ['p1'] is the truth inside: p1 is busy, p2 never was.
  // Probe the person-conflict FIRST (a rejected call leaves no trace), then the
  // success — so both may use room B exactly as the table interval names.
  assert.throws(() => rb.book('B', 0, 30, 'org', ['p1']), PersonConflictError);
  rb.book('B', 0, 30, 'org', ['p2']); // p2 never became busy → succeeds
  assert.equal(rb.schedule('B').length, 1);

  // same defense for a waitlist entry mutated after join and before promotion
  // (fresh ids q1/q2, unused elsewhere, so promotion is not blocked by p1/p2)
  const arr2 = ['q1'];
  const blk = rb.book('D', 0, 30, 'blk');
  rb.joinWaitlist('D', 0, 30, 'w', arr2); // entry copies ['q1']
  arr2.push('q2');                        // mutate after join
  rb.cancel(blk);                         // w promotes into D with ['q1']
  assert.deepEqual(rb.schedule('D').map((b) => b.organizer), ['w']);
  assert.throws(() => rb.book('F', 0, 30, 'org', ['q1']), PersonConflictError); // q1 busy via w
  rb.book('F', 0, 30, 'org', ['q2']); // q2 never busy (entry copy was ['q1']) → succeeds

  // Booking record: frozen, exactly the five stage-1 keys, even for
  // attendee-carrying bookings — attendees never cross the seam.
  const record = rb.schedule('A')[0];
  assert.ok(Object.isFrozen(record));
  assert.deepEqual(
    Object.keys(record).sort(),
    ['end', 'id', 'organizer', 'room', 'start']
  );
});

test('T60: stage-4 surface pin — module exports and the frozen six-function instance; instance isolation incl. capacities', async () => {
  const mod = await import('./roombook.js');
  assert.deepEqual(Object.keys(mod).sort(), [
    'BookingConflictError',
    'CapacityExceededError',
    'InvalidAttendeesError',
    'InvalidCapacityError',
    'InvalidIntervalError',
    'InvalidRecurrenceError',
    'NoConflictError',
    'PersonConflictError',
    'UnknownBookingError',
    'createRoomBook',
  ]);
  const rb = createRoomBook();
  assert.ok(Object.isFrozen(rb));
  assert.deepEqual(
    Object.keys(rb).sort(),
    ['book', 'bookRecurring', 'cancel', 'joinWaitlist', 'schedule', 'setCapacity']
  );
  // instance isolation extends to capacities: setCapacity in one never
  // constrains the other
  const one = createRoomBook();
  const two = createRoomBook();
  one.setCapacity('A', 1);
  two.book('A', 0, 30, 'org', ids(5)); // #2 undeclared/unlimited → succeeds
  assert.equal(two.schedule('A').length, 1);
  assert.throws(() => one.book('A', 0, 30, 'org', ids(5)), CapacityExceededError); // #1 capped
  // and a cancel in one never promotes the other's entries
  const a = createRoomBook();
  const b = createRoomBook();
  const aId = a.book('R', 0, 30, 'org');
  a.joinWaitlist('R', 0, 30, 'wa'); // queued in #a
  const bId = b.book('R', 0, 30, 'org');
  b.cancel(bId); // #b's cancel must not promote #a's entry
  assert.deepEqual(b.schedule('R'), []);
  assert.deepEqual(a.schedule('R').map((x) => x.organizer), ['org']); // #a unchanged
  a.cancel(aId); // #a's own cancel promotes its entry
  assert.deepEqual(a.schedule('R').map((x) => x.organizer), ['wa']);
});
